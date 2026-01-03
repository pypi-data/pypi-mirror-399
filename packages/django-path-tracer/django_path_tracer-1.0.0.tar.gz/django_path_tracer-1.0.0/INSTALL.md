# Installing django-path-tracer

## Installation Methods

### 1. Install from Local Source (Development)

```bash
# From the project root
cd django_path_tracer
pip install -e .
```

This installs the package in "editable" mode, so changes to the code are immediately available.

### 2. Install from Git Repository

```bash
pip install git+https://github.com/user-focus/talk-to-your-users.git#subdirectory=django_path_tracer
```

### 3. Install from PyPI (Future)

```bash
pip install django-path-tracer
```

## Verify Installation

After installation, verify the command is available:

```bash
django-path-tracer --help
```

You should see:
```
usage: django-path-tracer [-h] [--rebuild] [--cache CACHE] [--input-json INPUT_JSON] [--output-json OUTPUT_JSON] [target]

Django Path Tracer V2
...
```

## Usage After Installation

Once installed, you can use it from anywhere:

```bash
# Single target
django-path-tracer function_name

# Batch mode
django-path-tracer --input-json targets.json --output-json results.json

# With cache rebuild
django-path-tracer function_name --rebuild
```

## Package Structure

```
django_path_tracer/
├── __init__.py          # Package initialization
├── django_path_tracer.py # Main module (1212 lines)
├── setup.py             # Package setup
├── README.md            # Package documentation
└── INSTALL.md           # This file
```

## Uninstall

```bash
pip uninstall django-path-tracer
```

