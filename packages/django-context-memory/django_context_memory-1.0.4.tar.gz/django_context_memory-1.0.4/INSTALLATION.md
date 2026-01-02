# Django Context Memory - Installation Guide

## For New Projects (Once Published to PyPI)

### Install from PyPI
```bash
pip install django-context-memory
```

### CLI Usage
```bash
# Initialize context memory in your Django project
django-context init

# Scan all apps
django-context scan-all

# Build context for a specific app
django-context build myapp

# Build aggregated context for all apps
django-context build-all

# Check status
django-context status

# Clean generated files
django-context clean
```

### Python API Usage
```python
from django_context_memory import Config, ProjectScanner, ContextBuilder

# Initialize
PROJECT_ROOT = Path("/path/to/your/django/project")
config = Config(PROJECT_ROOT)
scanner = ProjectScanner(PROJECT_ROOT, config)
builder = ContextBuilder(PROJECT_ROOT, config)

# Scan and build context
apps = scanner.discover_apps()
for app_info in apps:
    snapshot = builder.create_snapshot(app_info['name'])
    context = builder.build_app_context(app_info['name'])

# Build aggregated context
aggregated = builder.build_aggregated_context()
```

### Django Integration (Optional Web UI Dashboard)

The library includes a built-in web dashboard. To enable it:

**1. Add to `INSTALLED_APPS` in settings.py:**

```python
# settings.py
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # Your apps
    'your_app',

    # Add Django Context Memory web UI
    'django_context_memory',  # <-- Add this
]
```

**2. Include URLs in urls.py:**

```python
# urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # Add Django Context Memory dashboard
    path('context-memory/', include('django_context_memory.urls')),  # <-- Add this
]
```

**3. Run migrations (optional - no database tables needed):**

```bash
python manage.py migrate
```

**4. Access the dashboard:**

Visit `http://localhost:8000/context-memory/` to use the web UI for:
- Viewing discovered apps
- Creating snapshots (START/END)
- Building context for apps
- Building aggregated context
- Viewing statistics

**Note:** The web UI is completely optional. You can use just the CLI or Python API if preferred.

---

## For Development (Current Project)

### Install in Editable Mode

From the project root:

```bash
# Install the library in editable mode
pip install -e ./django_context_memory

# Verify installation
python -c "from django_context_memory import Config; print('OK')"
```

### If You Get Import Errors

The package structure should be:
```
django_context_memory/           # Project directory
├── django_context_memory/       # Actual Python package
│   ├── __init__.py
│   ├── config.py
│   ├── scanner.py
│   ├── analyzer.py
│   ├── builder.py
│   ├── cli.py
│   ├── doc_generator.py
│   └── utils.py
├── setup.py
├── pyproject.toml
└── README.md
```

If imports fail, try:
```bash
# Uninstall and reinstall
pip uninstall django-context-memory
pip install -e ./django_context_memory

# Or add to PYTHONPATH temporarily
export PYTHONPATH="${PYTHONPATH}:./django_context_memory"  # Linux/Mac
set PYTHONPATH=%PYTHONPATH%;.\django_context_memory         # Windows CMD
```

---

## Configuration

### Create Configuration File (Optional)

In your Django project root, create `.context_memory_config.json`:

```json
{
  "project_name": "MyProject",
  "memory_dir": ".app_memory",
  "exclude_patterns": [
    "*/migrations/*",
    "*/__pycache__/*",
    "*.pyc",
    ".git/*",
    "venv/*",
    ".venv/*"
  ],
  "deep_analysis": true,
  "auto_generate_docs": true,
  "include_tests": false,
  "include_migrations": false,
  "max_file_size": 1048576,
  "scan_timeout": 300,
  "verbose": false
}
```

### Environment Variables

Override configuration with environment variables:

```bash
# Set memory directory
export DJANGO_CONTEXT_MEMORY_DIR=".custom_memory"

# Enable verbose logging
export DJANGO_CONTEXT_VERBOSE=1

# Disable deep analysis
export DJANGO_CONTEXT_DEEP_ANALYSIS=0
```

---

## Usage Examples

### Example 1: Quick Start
```bash
cd /path/to/your/django/project
django-context init
django-context scan-all
django-context build-all

# Generated files will be in .app_memory/
ls .app_memory/claude_aggregated_context.json
```

### Example 2: Programmatic Usage
```python
from pathlib import Path
from django_context_memory import ContextBuilder

# Build context for your project
builder = ContextBuilder(Path.cwd())

# Create snapshot for an app
snapshot = builder.create_snapshot('myapp', stage='start')
print(f"Scanned {len(snapshot['files'])} files")

# Build context
context = builder.build_app_context('myapp')
print(f"Models found: {len(context['summary']['models'])}")

# Build for all apps
aggregated = builder.build_aggregated_context()
print(f"Total apps: {aggregated['total_apps']}")
print(f"Total files: {aggregated['total_files']}")
```

### Example 3: Custom Configuration
```python
from pathlib import Path
from django_context_memory import Config, ContextBuilder

# Create custom config
config = Config(Path.cwd())
config.set('deep_analysis', True)
config.set('verbose', True)
config.set('max_file_size', 2097152)  # 2MB
config.save()

# Use with builder
builder = ContextBuilder(Path.cwd(), config)
```

---

## Troubleshooting

### Issue: "cannot import name 'Config'"

**Solution**: Make sure the library is installed:
```bash
pip list | grep django-context-memory
```

If not installed:
```bash
pip install django-context-memory
# Or for development:
pip install -e path/to/django_context_memory
```

### Issue: "App not found"

**Solution**: Make sure you're in the Django project root:
```bash
# Should contain manage.py
ls manage.py

# Check discovered apps
django-context status
```

### Issue: "Permission denied"

**Solution**: Check file permissions:
```bash
# Make sure .app_memory directory is writable
chmod -R u+w .app_memory
```

### Issue: "No module named django_context_memory"

**Solution**: The library isn't in Python path:
```bash
# Check Python path
python -c "import sys; print('\n'.join(sys.path))"

# Install library
pip install django-context-memory
```

---

## Requirements

- Python 3.8 or higher
- Django 3.2 or higher (optional, only for Django integration)
- No other runtime dependencies

---

## Next Steps

1. **Generate context**: Run `django-context build-all` in your project
2. **Use with Claude**: The generated `.app_memory/claude_aggregated_context.json` contains all project intelligence
3. **Integrate in workflow**: Add context generation to your development workflow
4. **Customize**: Adjust `.context_memory_config.json` to your needs

---

## Support

- GitHub: https://github.com/GavinHolder/django-context-memory
- Issues: https://github.com/GavinHolder/django-context-memory/issues
- Documentation: https://github.com/GavinHolder/django-context-memory#readme
