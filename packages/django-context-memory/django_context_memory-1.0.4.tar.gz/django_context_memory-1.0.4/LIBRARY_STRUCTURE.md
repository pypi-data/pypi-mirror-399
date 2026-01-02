# Django Context Memory - Library Structure

## Overview

This library provides **three ways** to use Django Context Memory:

1. **CLI Commands** - Command-line interface
2. **Python API** - Import and use programmatically
3. **Web Dashboard** - Optional Django web UI (built-in)

## Package Structure

```
django_context_memory/
├── django_context_memory/          # Main Python package
│   ├── __init__.py                 # Package exports
│   ├── analyzer.py                 # AST-based code analysis
│   ├── builder.py                  # Context building
│   ├── scanner.py                  # Project scanning
│   ├── config.py                   # Configuration management
│   ├── cli.py                      # CLI commands
│   ├── doc_generator.py            # Documentation generation
│   ├── utils.py                    # Utility functions
│   │
│   ├── apps.py                     # Django app configuration
│   ├── views.py                    # Django views (web UI)
│   ├── urls.py                     # Django URL patterns
│   │
│   └── templates/
│       └── django_context_memory/
│           └── index.html          # Web dashboard template
│
├── setup.py                        # Package configuration
├── pyproject.toml                  # Build system config
├── README.md                       # Main documentation
├── INSTALLATION.md                 # Installation guide
├── CLI_GUIDE.md                    # CLI documentation
├── CHANGELOG.md                    # Version history
├── LICENSE                         # MIT License
└── MANIFEST.in                     # Package data manifest
```

## Usage Methods

### 1. CLI Usage (No Django Required)

```bash
# Install library
pip install django-context-memory

# Use CLI commands
cd /path/to/your/django/project
django-context init
django-context build-all
```

**No Django configuration needed for CLI usage.**

### 2. Python API Usage (No Django Required)

```python
from django_context_memory import Config, ContextBuilder

# Use programmatically
builder = ContextBuilder('/path/to/project')
context = builder.build_aggregated_context()
```

**No Django configuration needed for Python API usage.**

### 3. Web Dashboard (Requires Django)

**Step 1:** Add to `settings.py`:
```python
INSTALLED_APPS = [
    ...
    'django_context_memory',  # Add this
]
```

**Step 2:** Add to `urls.py`:
```python
urlpatterns = [
    ...
    path('context-memory/', include('django_context_memory.urls')),
]
```

**Step 3:** Access at `http://localhost:8000/context-memory/`

## How It Works

### As a CLI Tool

When installed via pip, the `django-context` command becomes available globally:
- Entry point defined in `setup.py`: `"django-context=django_context_memory.cli:main"`
- Works in any Django project directory
- No installation in Django `INSTALLED_APPS` needed

### As a Python Library

Import and use classes directly:
- `Config` - Configuration management
- `ProjectScanner` - Discover and scan Django apps
- `CodeAnalyzer` - Analyze Python files using AST
- `ContextBuilder` - Build context and aggregations
- `DocGenerator` - Generate documentation

### As a Django App

When added to `INSTALLED_APPS`:
- Django discovers it via `apps.py` (`DjangoContextMemoryConfig`)
- URLs are routed via `urls.py`
- Views in `views.py` provide JSON API and HTML rendering
- Templates in `templates/django_context_memory/` are automatically discovered
- All business logic delegates to the core library classes

## Key Design Principles

1. **Zero Dependencies**: Core functionality has no runtime dependencies
2. **Django Optional**: Django only required for web UI, not CLI or API
3. **No Code Duplication**: Web UI views delegate to library classes
4. **Modular**: Each component (CLI, API, Web) can be used independently
5. **Single Source**: One library package provides all three usage methods

## What Changed from app_memory

Previously, `app_memory` was a separate Django app that duplicated code.

**Old structure:**
```
app_memory/                   # Separate Django app
├── code_analyzer.py          # DUPLICATE of library analyzer
├── views.py (657 lines)      # DUPLICATE logic
└── templates/

django_context_memory/        # Separate library
└── django_context_memory/
    ├── analyzer.py
    ├── builder.py
    └── ...
```

**New structure:**
```
django_context_memory/        # Single library package
└── django_context_memory/
    ├── analyzer.py           # Core business logic
    ├── builder.py
    ├── scanner.py
    ├── views.py              # Thin Django wrapper (delegates to core)
    ├── urls.py
    ├── apps.py
    └── templates/
```

**Benefits:**
- ✅ No code duplication
- ✅ Single package to maintain
- ✅ Easier to publish to PyPI
- ✅ Users get all three usage methods (CLI, API, Web) from one install

## Installation for End Users

```bash
# Install from PyPI (once published)
pip install django-context-memory

# Now you can:
# 1. Use CLI anywhere
django-context --help

# 2. Import in Python
from django_context_memory import ContextBuilder

# 3. Add to Django INSTALLED_APPS for web UI
# (See INSTALLATION.md for details)
```

## Development Installation

```bash
# Clone repository
git clone https://github.com/GavinHolder/django-context-memory

# Install in editable mode
cd django-context-memory
pip install -e .

# Verify
django-context --version
python -c "from django_context_memory import Config; print('OK')"
```

## Publishing to PyPI

See [PUBLISHING_TO_PYPI.md](PUBLISHING_TO_PYPI.md) for complete publishing guide.

**Quick publish:**
```bash
cd django_context_memory

# Build
python -m build

# Check
twine check dist/*

# Upload
twine upload dist/*
```

## GitHub Actions

The repository includes `.github/workflows/publish.yml` for automatic PyPI publishing when creating GitHub releases.

---

**Summary:** One library package (`django-context-memory`) provides CLI, Python API, and optional Django web UI—all from a single `pip install`.
