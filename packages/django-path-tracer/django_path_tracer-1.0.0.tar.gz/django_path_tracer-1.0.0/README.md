# Django Path Tracer

A Python package for tracing Django function calls, constants, and models to their API endpoints.

## Features

- **Metadata-First Approach**: Builds complete metadata before tracing
- **Comprehensive Analysis**: Tracks functions, classes, constants, models, and their relationships
- **Django-Specific**: Identifies Django Views, URL patterns, Celery tasks, and Signals
- **Caching**: Supports metadata caching for faster subsequent runs
- **Batch Processing**: Can process multiple targets at once

## Installation

```bash
pip install django-path-tracer
```

Or install from source:

```bash
git clone <repository>
cd django-path-tracer
pip install -e .
```

## Usage

### Command Line

```bash
# Trace a single function
django-path-tracer function_name

# Trace with cache rebuild
django-path-tracer function_name --rebuild

# Batch processing
django-path-tracer --input-json targets.json --output-json results.json
```

### Python API

```python
from django_path_tracer import MetadataBuilder, PathFinder

# Build metadata
builder = MetadataBuilder(".")
metadata = builder.build_all_metadata()

# Find paths
finder = PathFinder(metadata)
paths = finder.find_paths("function_name")

for path in paths:
    if path.status == "success":
        print(f"Found endpoint: {path.endpoint}")
```

## Requirements

- Python 3.8+
- Django project structure

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

