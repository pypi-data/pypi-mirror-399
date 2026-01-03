#!/usr/bin/env python3
"""
Django Path Tracer V2: Improved approach with metadata-first design.

Phase 1: Build Complete Metadata
- Scan all functions/methods/classes
- Build comprehensive call graph
- Store all relationships (calls, instantiations, references)
- Identify Django Views, Celery tasks, Signals

Phase 2: Intelligent Path Finding
- Query the metadata to find paths
- Handle complex cases (dynamic calls, class methods)
- Provide detailed path information

This approach is better because:
- Separates metadata building from path finding
- Allows caching and reuse of metadata
- Better visibility into what's happening
- Easier to debug and extend
"""

import ast
import os
import sys
import re
import json
import warnings
import argparse
from collections import defaultdict, deque
from typing import Dict, Set, List, Optional, Tuple, Any
from dataclasses import dataclass, field, asdict

# ==========================================
# CONFIGURATION
# ==========================================
PROJECT_ROOT = "."
IGNORE_DIRS = {
    'node_modules', '.git', 'venv', 'env', '__pycache__',
    'migrations', 'tests', 'test', 'dist', 'build', '.next',
    '.idea', '.vscode', 'staticfiles', 'dumps', 'pr_api_tracer'
}

DJANGO_VIEW_BASES = {
    'View', 'APIView', 'TemplateView', 'RedirectView',
    'ListView', 'DetailView', 'CreateView', 'UpdateView', 'DeleteView',
    'FormView', 'GenericAPIView', 'ListAPIView', 'CreateAPIView',
    'RetrieveAPIView', 'UpdateAPIView', 'DestroyAPIView',
    'ListCreateAPIView', 'RetrieveUpdateAPIView', 'RetrieveUpdateDestroyAPIView',
    'ViewSet', 'ModelViewSet', 'ReadOnlyModelViewSet', 'GenericViewSet'
}

# ==========================================
# METADATA STRUCTURES
# ==========================================

@dataclass
class FunctionMetadata:
    """Complete metadata for a function/method/class."""
    qualified_name: str
    name: str
    type: str  # 'function', 'method', 'class', 'constant', 'variable', 'model', 'enum'
    file: str
    line: int
    class_name: Optional[str] = None
    bases: List[str] = field(default_factory=list)
    decorators: List[str] = field(default_factory=list)
    value_type: Optional[str] = None  # For constants/variables: 'dict', 'list', 'str', etc.
    
    # Relationships
    called_by: Set[str] = field(default_factory=set)  # Who calls this
    calls: Set[str] = field(default_factory=set)  # What this calls
    instantiated_by: Set[str] = field(default_factory=set)  # Who instantiates (if class)
    methods: Set[str] = field(default_factory=set)  # Methods (if class)
    passed_as_reference: Set[str] = field(default_factory=set)  # Passed as function reference
    
    # Special flags
    is_django_view: bool = False
    is_celery_task: bool = False
    is_signal_handler: bool = False
    
    # URL mapping (if view)
    api_endpoints: List[Dict[str, str]] = field(default_factory=list)
    
    def to_dict(self):
        """Convert to dictionary for JSON serialization."""
        result = asdict(self)
        # Convert sets to lists for JSON
        result['called_by'] = list(self.called_by)
        result['calls'] = list(self.calls)
        result['instantiated_by'] = list(self.instantiated_by)
        result['methods'] = list(self.methods)
        result['passed_as_reference'] = list(self.passed_as_reference)
        return result

@dataclass
class PathSegment:
    """A segment in a call path."""
    from_func: str
    to_func: str
    relationship_type: str  # 'direct_call', 'class_instantiation', 'method_reference', 'dynamic_call'
    details: Dict[str, Any] = field(default_factory=dict)

@dataclass
class CompletePath:
    """A complete path from function to API endpoint."""
    target: str
    segments: List[PathSegment]
    endpoint: Optional[Dict[str, str]] = None
    view: Optional[str] = None
    status: str = "success"  # 'success', 'dead_end', 'celery_task', 'signal', 'view_no_url'
    message: str = ""

# ==========================================
# PHASE 1: METADATA BUILDER
# ==========================================

class MetadataBuilder:
    """Builds complete metadata for all functions in the codebase."""
    
    def __init__(self, root_dir: str):
        self.root_dir = root_dir
        self.metadata: Dict[str, FunctionMetadata] = {}
        self.imports_map: Dict[str, Dict[str, str]] = {}  # file -> {local_name: qualified_path}
        
    def build_all_metadata(self) -> Dict[str, FunctionMetadata]:
        """Build complete metadata for entire codebase."""
        print("🔍 Phase 1: Building Complete Metadata...")
        print("=" * 80)
        
        # Step 1: Scan all files and build initial metadata
        print("\n📋 Step 1: Scanning files and extracting definitions...")
        self._scan_all_files()
        print(f"   ✅ Found {len(self.metadata)} definitions")
        
        # Step 2: Build call relationships
        print("\n🔗 Step 2: Building call relationships...")
        self._build_call_relationships()
        
        # Step 3: Build class relationships
        print("\n🏗️  Step 3: Building class relationships...")
        self._build_class_relationships()
        
        # Step 4: Identify special types (Views, Tasks, Signals)
        print("\n🎯 Step 4: Identifying special types...")
        self._identify_special_types()
        
        # Step 5: Map Views to URLs
        print("\n🌐 Step 5: Mapping Views to URLs...")
        self._map_views_to_urls()
        
        print("\n" + "=" * 80)
        print("✅ Metadata building complete!")
        print(f"   Total functions: {len([m for m in self.metadata.values() if m.type != 'class'])}")
        print(f"   Total classes: {len([m for m in self.metadata.values() if m.type == 'class'])}")
        print(f"   Django Views: {len([m for m in self.metadata.values() if m.is_django_view])}")
        print(f"   API Endpoints: {sum(len(m.api_endpoints) for m in self.metadata.values())}")
        
        return self.metadata
    
    def _scan_all_files(self):
        """Scan all Python files and extract definitions."""
        file_count = 0
        
        for root, dirs, files in os.walk(self.root_dir):
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
            
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, self.root_dir)
                    
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                        
                        with warnings.catch_warnings():
                            warnings.filterwarnings("ignore", category=SyntaxWarning)
                            tree = ast.parse(content, filename=file_path)
                        
                        # Resolve imports
                        import_resolver = ImportResolver(file_path, self.root_dir)
                        import_resolver.visit(tree)
                        self.imports_map[rel_path] = import_resolver.imports
                        
                        # Extract definitions
                        extractor = DefinitionExtractor(rel_path, import_resolver.imports)
                        extractor.visit(tree)
                        
                        # Store metadata
                        for qualified_name, info in extractor.definitions.items():
                            self.metadata[qualified_name] = FunctionMetadata(
                                qualified_name=qualified_name,
                                name=info["name"],
                                type=info["type"],
                                file=info["file"],
                                line=info["line"],
                                class_name=info.get("class"),
                                bases=info.get("bases", []),
                                decorators=info.get("decorators", []),
                                value_type=info.get("value_type")
                            )
                        
                        file_count += 1
                    except Exception as e:
                        # Debug: print errors for constants.py files
                        if "constants.py" in rel_path or "consts.py" in rel_path:
                            print(f"   ⚠️  Error parsing {rel_path}: {e}")
                        pass
        
        print(f"   Scanned {file_count} Python files")
    
    def _build_call_relationships(self):
        """Build call relationships between functions."""
        call_count = 0
        
        for root, dirs, files in os.walk(self.root_dir):
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
            
            for file in files:
                if file.endswith(".py"):
                    file_path = os.path.join(root, file)
                    rel_path = os.path.relpath(file_path, self.root_dir)
                    
                    if rel_path not in self.imports_map:
                        continue
                    
                    try:
                        with open(file_path, "r", encoding="utf-8") as f:
                            content = f.read()
                        
                        with warnings.catch_warnings():
                            warnings.filterwarnings("ignore", category=SyntaxWarning)
                            tree = ast.parse(content, filename=file_path)
                        
                        # Build call graph for this file
                        builder = CallGraphBuilder(rel_path, self.imports_map[rel_path], self.metadata)
                        builder.visit(tree)
                        call_count += builder.call_count
                    except:
                        pass
        
        print(f"   Built {call_count} call relationships")
    
    def _build_class_relationships(self):
        """Build relationships between classes and their methods."""
        for qualified_name, meta in self.metadata.items():
            if meta.type in ["class", "model"]:
                # Find all methods of this class
                for method_qualified, method_meta in self.metadata.items():
                    if (method_meta.class_name == meta.name and 
                        method_meta.file == meta.file):
                        meta.methods.add(method_qualified)
                        method_meta.called_by.add(qualified_name)  # Class "calls" its methods
    
    def _identify_special_types(self):
        """Identify Django Views, Celery tasks, Signals, Models."""
        for qualified_name, meta in self.metadata.items():
            # Check if Django View
            if "views.py" in meta.file:
                meta.is_django_view = True
            elif meta.type in ["class", "model"]:
                for base in meta.bases:
                    if base in DJANGO_VIEW_BASES:
                        meta.is_django_view = True
                        break
            
            # Models are already identified by type, but mark them explicitly
            if meta.type == "model":
                # Models can be used in views, serializers, etc.
                pass
            
            # Check decorators
            for decorator in meta.decorators:
                if "shared_task" in decorator or "celery.task" in decorator:
                    meta.is_celery_task = True
                if "receiver" in decorator:
                    meta.is_signal_handler = True
    
    def _map_views_to_urls(self):
        """Map Django Views to their URL endpoints."""
        url_parser = URLParser()
        url_parser.parse_all_urls(self.root_dir)
        
        endpoint_count = 0
        for view_class, url_infos in url_parser.view_to_urls.items():
            # Find the view in metadata
            for qualified_name, meta in self.metadata.items():
                if meta.name == view_class and meta.is_django_view:
                    meta.api_endpoints = url_infos
                    endpoint_count += len(url_infos)
                    break
        
        print(f"   Mapped {endpoint_count} API endpoints to Views")
    
    def save_metadata(self, filepath: str):
        """Save metadata to JSON file."""
        data = {name: meta.to_dict() for name, meta in self.metadata.items()}
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"💾 Metadata saved to {filepath}")
    
    def load_metadata(self, filepath: str):
        """Load metadata from JSON file."""
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        for name, meta_dict in data.items():
            meta = FunctionMetadata(**meta_dict)
            # Convert lists back to sets
            meta.called_by = set(meta_dict.get('called_by', []))
            meta.calls = set(meta_dict.get('calls', []))
            meta.instantiated_by = set(meta_dict.get('instantiated_by', []))
            meta.methods = set(meta_dict.get('methods', []))
            meta.passed_as_reference = set(meta_dict.get('passed_as_reference', []))
            self.metadata[name] = meta
        
        print(f"📂 Metadata loaded from {filepath}")

# ==========================================
# PHASE 2: PATH FINDER
# ==========================================

class PathFinder:
    """Finds paths from functions to API endpoints using metadata."""
    
    def __init__(self, metadata: Dict[str, FunctionMetadata]):
        self.metadata = metadata
    
    def find_paths(self, target: str, max_depth: int = 10) -> List[CompletePath]:
        """Find all paths from target to API endpoints."""
        # Find target in metadata
        target_meta = self._find_target(target)
        if not target_meta:
            return []
        
        paths = []
        queue = deque([(target_meta.qualified_name, 0, [])])
        visited = set()
        
        while queue:
            current_name, depth, path_segments = queue.popleft()
            
            if current_name in visited or depth > max_depth:
                continue
            
            visited.add(current_name)
            current_meta = self.metadata.get(current_name)
            if not current_meta:
                continue
            
            # Check if we've reached a View
            if current_meta.is_django_view and current_meta.api_endpoints:
                # Found an endpoint!
                for endpoint in current_meta.api_endpoints:
                    paths.append(CompletePath(
                        target=target,
                        segments=path_segments,
                        endpoint=endpoint,
                        view=current_meta.name,
                        status="success",
                        message=f"✅ API Found -> {endpoint.get('method', 'GET')} /{endpoint.get('url', '')}"
                    ))
                continue
            
            # Check special cases
            if current_meta.is_celery_task:
                paths.append(CompletePath(
                    target=target,
                    segments=path_segments,
                    status="celery_task",
                    message=f"🔄 Background Job: Called by Celery Task '{current_meta.name}'"
                ))
                continue
            
            if current_meta.is_signal_handler:
                paths.append(CompletePath(
                    target=target,
                    segments=path_segments,
                    status="signal",
                    message=f"⚡ Event Driven: Triggered by Signal '{current_meta.name}'"
                ))
                continue
            
            # Continue tracing upward
            # For constants/variables/models, "called_by" means "used_by"
            all_callers = (
                current_meta.called_by |
                current_meta.instantiated_by |
                current_meta.passed_as_reference
            )
            
            if not all_callers:
                # For constants/variables, provide more helpful message
                if current_meta.type in ["constant", "variable"]:
                    paths.append(CompletePath(
                        target=target,
                        segments=path_segments,
                        status="dead_end",
                        message=f"⚠️ Constant/Variable '{current_meta.name}' defined but not traced to API endpoint. It may be used indirectly."
                    ))
                elif current_meta.type == "model":
                    paths.append(CompletePath(
                        target=target,
                        segments=path_segments,
                        status="dead_end",
                        message=f"⚠️ Model '{current_meta.name}' defined but not traced to API endpoint. It may be used in serializers, views, or admin."
                    ))
                else:
                    paths.append(CompletePath(
                        target=target,
                        segments=path_segments,
                        status="dead_end",
                        message="⚠️ Dead End: Function not used explicitly."
                    ))
                continue
            
            for caller_name in all_callers:
                if caller_name not in visited:
                    caller_meta = self.metadata.get(caller_name)
                    if caller_meta:
                        # Determine relationship type
                        if caller_name in current_meta.instantiated_by:
                            rel_type = "class_instantiation"
                        elif caller_name in current_meta.passed_as_reference:
                            rel_type = "method_reference"
                        else:
                            rel_type = "direct_call"
                        
                        new_segment = PathSegment(
                            from_func=caller_name,
                            to_func=current_name,
                            relationship_type=rel_type
                        )
                        
                        queue.append((caller_name, depth + 1, path_segments + [new_segment]))
        
        return paths
    
    def _find_target(self, target: str) -> Optional[FunctionMetadata]:
        """Find target function/constant/model in metadata."""
        # Try exact match first
        if target in self.metadata:
            return self.metadata[target]
        
        # Try partial matches - prioritize exact name matches
        exact_matches = []
        partial_matches = []
        
        for qualified_name, meta in self.metadata.items():
            if meta.name == target:
                exact_matches.append((qualified_name, meta))
            elif qualified_name.endswith(f"::{target}"):
                partial_matches.append((qualified_name, meta))
            elif target in qualified_name:
                partial_matches.append((qualified_name, meta))
        
        # Return first exact match, or first partial match
        if exact_matches:
            return exact_matches[0][1]
        if partial_matches:
            return partial_matches[0][1]
        
        return None

# ==========================================
# HELPER CLASSES (from original implementation)
# ==========================================

class ImportResolver(ast.NodeVisitor):
    """Resolves imports to their actual module paths."""
    
    def __init__(self, current_file: str, root_dir: str):
        self.current_file = current_file
        self.root_dir = root_dir
        self.imports = {}
    
    def resolve_module_path(self, module_name: Optional[str], level: int = 0) -> Optional[str]:
        """Resolve a module path from import statement."""
        if level > 0:
            base = os.path.dirname(self.current_file)
            for _ in range(level - 1):
                base = os.path.dirname(base)
            
            if module_name:
                candidate = os.path.join(base, module_name.replace('.', os.sep)) + ".py"
            else:
                candidate = os.path.join(base, "__init__.py")
            
            if os.path.exists(candidate):
                return os.path.relpath(candidate, self.root_dir)
            return None
        
        if not module_name:
            return None
            
        rel_path = module_name.replace('.', os.sep) + ".py"
        if os.path.exists(rel_path):
            return rel_path
        
        pkg_path = module_name.replace('.', os.sep) + os.sep + "__init__.py"
        if os.path.exists(pkg_path):
            return pkg_path
        return None
    
    def visit_Import(self, node):
        for alias in node.names:
            local_name = alias.asname or alias.name
            module_path = self.resolve_module_path(alias.name, 0)
            if module_path:
                self.imports[local_name] = f"{module_path}::{alias.name}"
    
    def visit_ImportFrom(self, node):
        source_file = self.resolve_module_path(node.module, node.level)
        if not source_file:
            return
            
        for alias in node.names:
            local_name = alias.asname or alias.name
            orig_name = alias.name
            qualified = f"{source_file}::{orig_name}"
            self.imports[local_name] = qualified

class DefinitionExtractor(ast.NodeVisitor):
    """Extracts function/class definitions."""
    
    def __init__(self, file_path: str, imports: Dict[str, str]):
        self.file_path = file_path
        self.imports = imports
        self.current_class = None
        self.current_function = None
        self.definitions = {}
    
    def get_qualified_name(self, name: str, is_class: bool = False) -> str:
        """Get qualified name for a function/class."""
        if self.current_class and not is_class:
            return f"{self.file_path}::{self.current_class}.{name}"
        return f"{self.file_path}::{name}"
    
    def visit_ClassDef(self, node):
        prev_class = self.current_class
        self.current_class = node.name
        qualified = self.get_qualified_name(node.name, is_class=True)
        
        bases = []
        for base in node.bases:
            if isinstance(base, ast.Name):
                bases.append(base.id)
            elif isinstance(base, ast.Attribute):
                bases.append(base.attr)
        
        decorators = []
        for decorator in node.decorator_list:
            decorator_name = self._get_decorator_name(decorator)
            if decorator_name:
                decorators.append(decorator_name)
        
        # Determine if it's a model (inherits from models.Model)
        is_model = False
        for base in bases:
            if "Model" in base or "models.Model" in str(base):
                is_model = True
                break
        
        # Check if it's in models.py file (common Django pattern)
        if "models.py" in self.file_path:
            is_model = True
        
        class_type = "model" if is_model else "class"
        
        self.definitions[qualified] = {
            "file": self.file_path,
            "line": node.lineno,
            "type": class_type,
            "name": node.name,
            "class": None,
            "bases": bases,
            "decorators": decorators,
            "value_type": None
        }
        
        self.generic_visit(node)
        self.current_class = prev_class
    
    def visit_FunctionDef(self, node):
        if node.name.startswith("__") and node.name.endswith("__"):
            self.generic_visit(node)
            return
        
        prev_func = self.current_function
        self.current_function = node.name
        
        decorators = []
        for decorator in node.decorator_list:
            decorator_name = self._get_decorator_name(decorator)
            if decorator_name:
                decorators.append(decorator_name)
        
        qualified = self.get_qualified_name(node.name)
        self.definitions[qualified] = {
            "file": self.file_path,
            "line": node.lineno,
            "type": "method" if self.current_class else "function",
            "name": node.name,
            "class": self.current_class,
            "bases": [],
            "decorators": decorators,
            "value_type": None
        }
        
        self.generic_visit(node)
        self.current_function = prev_func
    
    def visit_Assign(self, node):
        """Track constant/variable assignments."""
        for target in node.targets:
            if isinstance(target, ast.Name):
                # Module-level or class-level assignment
                name = target.id
                
                # Skip if it's inside a function (local variable) - but track class attributes
                # Only skip if we're inside a function AND not in a class
                if self.current_function and not self.current_class:
                    # This is a local variable in a function, skip it
                    continue
                
                # Determine if it's a constant (UPPER_CASE) or variable
                is_constant = name.isupper() and '_' in name
                var_type = "constant" if is_constant else "variable"
                
                # Try to infer value type
                value_type = None
                if isinstance(node.value, ast.Dict):
                    value_type = "dict"
                elif isinstance(node.value, ast.List):
                    value_type = "list"
                elif isinstance(node.value, ast.Constant):
                    if isinstance(node.value.value, str):
                        value_type = "str"
                    elif isinstance(node.value.value, int):
                        value_type = "int"
                elif hasattr(ast, 'Str') and isinstance(node.value, ast.Str):
                    value_type = "str"
                
                qualified = self.get_qualified_name(name)
                self.definitions[qualified] = {
                    "file": self.file_path,
                    "line": node.lineno,
                    "type": var_type,
                    "name": name,
                    "class": self.current_class,
                    "bases": [],
                    "decorators": [],
                    "value_type": value_type
                }
        
        self.generic_visit(node)
    
    def _get_decorator_name(self, decorator) -> Optional[str]:
        """Extract decorator name from AST node."""
        if isinstance(decorator, ast.Name):
            return decorator.id
        elif isinstance(decorator, ast.Attribute):
            return decorator.attr
        elif isinstance(decorator, ast.Call):
            if isinstance(decorator.func, ast.Name):
                return decorator.func.id
            elif isinstance(decorator.func, ast.Attribute):
                return decorator.func.attr
        return None

class CallGraphBuilder(ast.NodeVisitor):
    """Builds call graph relationships and updates metadata."""
    
    def __init__(self, file_path: str, imports: Dict[str, str], metadata: Dict[str, FunctionMetadata]):
        self.file_path = file_path
        self.imports = imports
        self.metadata = metadata
        self.current_class = None
        self.current_function = None
        self.call_count = 0
    
    def get_qualified_name(self, name: str, is_class: bool = False) -> str:
        """Get qualified name for a function/class."""
        if self.current_class and not is_class:
            return f"{self.file_path}::{self.current_class}.{name}"
        return f"{self.file_path}::{name}"
    
    def visit_ClassDef(self, node):
        prev_class = self.current_class
        self.current_class = node.name
        self.generic_visit(node)
        self.current_class = prev_class
    
    def visit_FunctionDef(self, node):
        if node.name.startswith("__") and node.name.endswith("__"):
            self.generic_visit(node)
            return
        
        prev_func = self.current_function
        self.current_function = node.name
        self.generic_visit(node)
        self.current_function = prev_func
    
    def visit_Call(self, node):
        """Track function calls and update metadata."""
        if not self.current_function:
            self.generic_visit(node)
            return
        
        caller_qualified = self.get_qualified_name(self.current_function)
        caller_meta = self.metadata.get(caller_qualified)
        if not caller_meta:
            self.generic_visit(node)
            return
        
        # Extract callee
        qualified_callee = self._extract_callee(node)
        
        if qualified_callee:
            callee_meta = self.metadata.get(qualified_callee)
            if callee_meta:
                # Update relationships
                caller_meta.calls.add(qualified_callee)
                callee_meta.called_by.add(caller_qualified)
                self.call_count += 1
            
            # Check for class/model instantiation
            if callee_meta and callee_meta.type in ["class", "model"]:
                caller_meta.calls.add(qualified_callee)
                callee_meta.instantiated_by.add(caller_qualified)
                # Link all methods of the class to the caller
                for method_name in callee_meta.methods:
                    method_meta = self.metadata.get(method_name)
                    if method_meta:
                        method_meta.called_by.add(caller_qualified)
        
        # Track function references passed as arguments
        for arg in node.args:
            func_ref = self._extract_function_reference(arg)
            if func_ref:
                ref_meta = self.metadata.get(func_ref)
                if ref_meta:
                    ref_meta.passed_as_reference.add(caller_qualified)
                    caller_meta.calls.add(func_ref)
        
        self.generic_visit(node)
    
    def visit_Name(self, node):
        """Track usage of constants, variables, and models."""
        if not self.current_function:
            self.generic_visit(node)
            return
        
        # Skip if it's a function call (handled in visit_Call)
        if isinstance(node.ctx, ast.Store):
            self.generic_visit(node)
            return
        
        name = node.id
        caller_qualified = self.get_qualified_name(self.current_function)
        caller_meta = self.metadata.get(caller_qualified)
        if not caller_meta:
            self.generic_visit(node)
            return
        
        # Check if this is an imported constant/variable/model
        if name in self.imports:
            imported_qualified = self.imports[name]
            imported_meta = self.metadata.get(imported_qualified)
            if imported_meta:
                # Track usage
                if imported_meta.type in ["constant", "variable", "model"]:
                    caller_meta.calls.add(imported_qualified)
                    imported_meta.called_by.add(caller_qualified)
                    self.call_count += 1
        else:
            # Check if it's a constant/variable in the same file
            if self.current_class:
                qualified = f"{self.file_path}::{self.current_class}.{name}"
            else:
                qualified = f"{self.file_path}::{name}"
            
            used_meta = self.metadata.get(qualified)
            if used_meta and used_meta.type in ["constant", "variable", "model"]:
                caller_meta.calls.add(qualified)
                used_meta.called_by.add(caller_qualified)
                self.call_count += 1
        
        self.generic_visit(node)
    
    def visit_Attribute(self, node):
        """Track attribute access (e.g., models.Model, constants.REVERSE_SENTIMENT_LIST)."""
        if not self.current_function:
            self.generic_visit(node)
            return
        
        caller_qualified = self.get_qualified_name(self.current_function)
        caller_meta = self.metadata.get(caller_qualified)
        if not caller_meta:
            self.generic_visit(node)
            return
        
        # Check if accessing a constant/variable from a module
        if isinstance(node.value, ast.Name):
            module_name = node.value.id
            attr_name = node.attr
            
            if module_name in self.imports:
                base_qualified = self.imports[module_name]
                # Try to find the constant/variable
                # This is a heuristic - we'd need to know the module structure
                # For now, check if the base is a known module path
                if base_qualified.endswith(f"::{module_name}"):
                    # Try to construct the full path
                    constant_qualified = f"{base_qualified}.{attr_name}"
                    constant_meta = self.metadata.get(constant_qualified)
                    if constant_meta and constant_meta.type in ["constant", "variable"]:
                        caller_meta.calls.add(constant_qualified)
                        constant_meta.called_by.add(caller_qualified)
                        self.call_count += 1
        
        self.generic_visit(node)
    
    def _extract_callee(self, node) -> Optional[str]:
        """Extract callee qualified name from call node."""
        if isinstance(node.func, ast.Name):
            called_name = node.func.id
            if called_name in self.imports:
                return self.imports[called_name]
            else:
                if self.current_class:
                    return f"{self.file_path}::{self.current_class}.{called_name}"
                else:
                    return f"{self.file_path}::{called_name}"
        
        elif isinstance(node.func, ast.Attribute):
            attr_name = node.func.attr
            
            if isinstance(node.func.value, ast.Name):
                if node.func.value.id == 'self' and self.current_class:
                    return f"{self.file_path}::{self.current_class}.{attr_name}"
                elif node.func.value.id in self.imports:
                    base = self.imports[node.func.value.id]
                    return f"{base}.{attr_name}"
                else:
                    # Could be instance.method()
                    var_name = node.func.value.id
                    return f"{self.file_path}::{var_name}.{attr_name}"
        
        return None
    
    def _extract_function_reference(self, node) -> Optional[str]:
        """Extract function reference from AST node."""
        if isinstance(node, ast.Name):
            func_name = node.id
            if func_name in self.imports:
                return self.imports[func_name]
            if self.current_class:
                return f"{self.file_path}::{self.current_class}.{func_name}"
            return f"{self.file_path}::{func_name}"
        
        elif isinstance(node, ast.Attribute):
            if isinstance(node.value, ast.Name):
                var_name = node.value.id
                if var_name == 'self' and self.current_class:
                    return f"{self.file_path}::{self.current_class}.{node.attr}"
                elif var_name in self.imports:
                    base = self.imports[var_name]
                    return f"{base}.{node.attr}"
                else:
                    return f"{self.file_path}::{var_name}.{node.attr}"
        
        return None

class URLParser:
    """Parses Django urls.py files to map views to endpoints."""
    
    def __init__(self):
        self.view_to_urls = defaultdict(list)
    
    def parse_all_urls(self, root_dir: str):
        """Parse all urls.py files in the project."""
        for root, dirs, files in os.walk(root_dir):
            dirs[:] = [d for d in dirs if d not in IGNORE_DIRS]
            
            if "urls.py" in files:
                urls_path = os.path.join(root, "urls.py")
                self._parse_urls_file(urls_path)
    
    def _parse_urls_file(self, urls_path: str):
        """Parse a single urls.py file."""
        try:
            with open(urls_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            app_name_match = re.search(r"app_name\s*=\s*['\"]([^'\"]+)['\"]", content)
            app_name = app_name_match.group(1) if app_name_match else None
            
            tree = ast.parse(content, filename=urls_path)
            
            imports = {}
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        imports[alias.name] = module
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id == "urlpatterns":
                            if isinstance(node.value, ast.List):
                                self._extract_patterns(node.value.elts, urls_path, imports, app_name)
        except:
            pass
    
    def _extract_patterns(self, patterns, urls_path, imports, app_name):
        """Extract URL patterns."""
        for pattern in patterns:
            if isinstance(pattern, ast.Call):
                func = pattern.func
                if isinstance(func, ast.Name) and func.id in ["path", "re_path", "url"]:
                    if len(pattern.args) >= 2:
                        route = self._get_string_value(pattern.args[0])
                        if not route:
                            continue
                        
                        view_arg = pattern.args[1]
                        view_info = self._extract_view_info(view_arg, imports, urls_path)
                        
                        if view_info:
                            view_class = view_info["view_class"]
                            url_pattern = route.strip("/")
                            
                            if app_name:
                                full_url = f"{app_name}/{url_pattern}"
                            else:
                                full_url = url_pattern
                            
                            # Infer HTTP method from view class name
                            method = self._infer_method(view_class)
                            
                            url_info = {
                                "url": full_url,
                                "method": method,
                                "file": urls_path
                            }
                            
                            self.view_to_urls[view_class].append(url_info)
    
    def _get_string_value(self, node) -> Optional[str]:
        """Extract string value from AST node."""
        if isinstance(node, ast.Constant):
            return node.value
        elif hasattr(ast, 'Str') and isinstance(node, ast.Str):
            return node.s
        elif isinstance(node, ast.Str):  # Python < 3.8 compatibility
            return node.s
        return None
    
    def _extract_view_info(self, view_node, imports, urls_path):
        """Extract view class name from AST node."""
        if isinstance(view_node, ast.Call):
            if isinstance(view_node.func, ast.Attribute) and view_node.func.attr == "as_view":
                if isinstance(view_node.func.value, ast.Attribute):
                    if isinstance(view_node.func.value.value, ast.Name):
                        module_name = view_node.func.value.value.id
                        view_class = view_node.func.value.attr
                        return {
                            "view_class": view_class,
                            "view_module": imports.get(module_name, ""),
                            "file": urls_path
                        }
        elif isinstance(view_node, ast.Attribute):
            if isinstance(view_node.value, ast.Name):
                module = imports.get(view_node.value.id, "")
                view_class = view_node.attr
                return {
                    "view_class": view_class,
                    "view_module": module,
                    "file": urls_path
                }
        elif isinstance(view_node, ast.Name):
            return {
                "view_class": view_node.id,
                "view_module": "",
                "file": urls_path
            }
        return None
    
    def _infer_method(self, view_class: str) -> str:
        """Infer HTTP method from view class name."""
        view_lower = view_class.lower()
        
        if "create" in view_lower or "post" in view_lower:
            return "POST"
        elif "update" in view_lower or "put" in view_lower or "patch" in view_lower:
            return "PATCH" if "patch" in view_lower or "update" in view_lower else "PUT"
        elif "delete" in view_lower or "destroy" in view_lower:
            return "DELETE"
        elif "list" in view_lower:
            return "GET"
        elif "retrieve" in view_lower or "get" in view_lower or "detail" in view_lower:
            return "GET"
        elif "change" in view_lower:
            return "PATCH"  # Common pattern for change endpoints
        
        return "GET/POST"

# ==========================================
# MAIN
# ==========================================

def trace_targets_to_json(targets: List[str], metadata: Dict[str, FunctionMetadata], output_file: Optional[str] = None) -> List[Dict]:
    """Trace multiple targets and return JSON-serializable results."""
    finder = PathFinder(metadata)
    all_results = []
    
    for target in targets:
        paths = finder.find_paths(target)
        
        for path in paths:
            result = {
                'target': target,
                'status': path.status,
                'message': path.message,
                'endpoint': path.endpoint,
                'view': path.view,
                'segments': []
            }
            
            # Convert segments to dict
            for segment in path.segments:
                from_meta = metadata.get(segment.from_func)
                to_meta = metadata.get(segment.to_func)
                from_name = from_meta.name if from_meta else segment.from_func.split("::")[-1]
                to_name = to_meta.name if to_meta else segment.to_func.split("::")[-1]
                
                result['segments'].append({
                    'from': from_name,
                    'to': to_name,
                    'from_qualified': segment.from_func,
                    'to_qualified': segment.to_func,
                    'relationship_type': segment.relationship_type
                })
            
            all_results.append(result)
    
    if output_file:
        with open(output_file, 'w') as f:
            json.dump(all_results, f, indent=2)
    
    return all_results

def main():
    parser = argparse.ArgumentParser(description='Django Path Tracer V2')
    parser.add_argument('target', nargs='?', help='Target function/constant/model name')
    parser.add_argument('--rebuild', action='store_true', help='Rebuild metadata cache')
    parser.add_argument('--cache', default='metadata_cache.json', help='Metadata cache file')
    parser.add_argument('--input-json', help='Input JSON file with list of targets')
    parser.add_argument('--output-json', help='Output JSON file for results')
    
    args = parser.parse_args()
    
    # Phase 1: Build or load metadata
    builder = MetadataBuilder(PROJECT_ROOT)
    
    if not args.rebuild and os.path.exists(args.cache):
        print("📂 Loading cached metadata...")
        builder.load_metadata(args.cache)
    else:
        metadata = builder.build_all_metadata()
        builder.save_metadata(args.cache)
    
    # Handle batch processing mode
    if args.input_json:
        print(f"🚀 Django Path Tracer V2 (Batch Mode)")
        print(f"   Input: {args.input_json}")
        print(f"\n{'='*80}\n")
        
        # Load targets from JSON
        with open(args.input_json, 'r') as f:
            data = json.load(f)
        
        # Extract targets from changed items
        if 'changed_items' in data:
            targets = []
            for item in data['changed_items']:
                qualified_name = item.get('qualified_name') or item.get('name')
                if qualified_name:
                    # Try both qualified name and just the name
                    targets.append(qualified_name.split('::')[-1])
                    if '.' in qualified_name:
                        # Also try the method name alone
                        method_name = qualified_name.split('.')[-1]
                        if method_name not in targets:
                            targets.append(method_name)
        else:
            targets = data.get('targets', [])
        
        print(f"🔍 Tracing {len(targets)} target(s)...")
        print("=" * 80 + "\n")
        
        results = trace_targets_to_json(targets, builder.metadata, args.output_json)
        
        if args.output_json:
            print(f"✅ Results written to {args.output_json}")
        else:
            # Print summary
            successful = [r for r in results if r['status'] == 'success']
            print(f"✅ Found {len(successful)} successful path(s)")
            print(f"⚠️  Found {len(results) - len(successful)} other path(s)")
        
        return
    
    # Single target mode
    if not args.target:
        parser.print_help()
        sys.exit(1)
    
    print(f"🚀 Django Path Tracer V2 (Metadata-First Approach)")
    print(f"   Target: {args.target}")
    print(f"\n{'='*80}\n")
    
    # Phase 2: Find paths
    print(f"\n{'='*80}")
    print("🔍 Phase 2: Finding Paths...")
    print("=" * 80 + "\n")
    
    finder = PathFinder(builder.metadata)
    paths = finder.find_paths(args.target)
    
    if not paths:
        print(f"❌ No paths found for '{args.target}'")
        return
    
    # Separate successful paths from others
    successful_paths = [p for p in paths if p.status == "success"]
    other_paths = [p for p in paths if p.status != "success"]
    
    if successful_paths:
        print(f"✅ Found {len(successful_paths)} API endpoint(s) to test:\n")
        
        # Group by endpoint
        endpoints_by_url = {}
        for path in successful_paths:
            if path.endpoint:
                url = path.endpoint.get('url', '')
                method = path.endpoint.get('method', 'GET')
                key = f"{method} /{url}"
                if key not in endpoints_by_url:
                    endpoints_by_url[key] = {
                        'method': method,
                        'url': url,
                        'view': path.view,
                        'paths': []
                    }
                endpoints_by_url[key]['paths'].append(path)
        
        # Display endpoints
        for i, (key, endpoint_info) in enumerate(endpoints_by_url.items(), 1):
            print(f"{i}. {endpoint_info['method']:15} /{endpoint_info['url']}")
            print(f"   View: {endpoint_info['view']}")
            print(f"   Found via {len(endpoint_info['paths'])} path(s)")
            print()
        
        # Show detailed paths
        print(f"\n{'='*80}")
        print("📋 Detailed Call Chains:")
        print("=" * 80 + "\n")
        
        for i, path in enumerate(successful_paths, 1):
            print(f"Path {i}: {path.status}")
            print(f"  {path.message}")
            
            if path.segments:
                print(f"  Call Chain:")
                for j, segment in enumerate(path.segments, 1):
                    from_meta = builder.metadata.get(segment.from_func)
                    to_meta = builder.metadata.get(segment.to_func)
                    from_name = from_meta.name if from_meta else segment.from_func.split("::")[-1]
                    to_name = to_meta.name if to_meta else segment.to_func.split("::")[-1]
                    print(f"    {j}. {from_name} -> {to_name} ({segment.relationship_type})")
            
            if path.endpoint:
                print(f"  Endpoint: {path.endpoint.get('method')} /{path.endpoint.get('url')}")
                print(f"  View: {path.view}")
            print()
    
    if other_paths:
        print(f"\n{'='*80}")
        print(f"⚠️  Other Paths ({len(other_paths)}):")
        print("=" * 80 + "\n")
        
        for i, path in enumerate(other_paths, 1):
            print(f"Path {i}: {path.status}")
            print(f"  {path.message}")
            if path.segments:
                print(f"  Call Chain:")
                for j, segment in enumerate(path.segments, 1):
                    from_meta = builder.metadata.get(segment.from_func)
                    to_meta = builder.metadata.get(segment.to_func)
                    from_name = from_meta.name if from_meta else segment.from_func.split("::")[-1]
                    to_name = to_meta.name if to_meta else segment.to_func.split("::")[-1]
                    print(f"    {j}. {from_name} -> {to_name} ({segment.relationship_type})")
            print()

if __name__ == "__main__":
    main()

