# Quick Start Guide - Django Context Memory

Get up and running with Django Context Memory in 5 minutes.

## Installation

### From PyPI (when published)
```bash
pip install django-context-memory
```

### From Source (Development)
```bash
cd django_context_memory
pip install -e .
```

## Basic Usage

### 1. Navigate to Your Django Project
```bash
cd /path/to/your/django/project
```

### 2. Initialize Context Memory
```bash
django-context init
```

This will:
- Create `.app_memory/` directory
- Scan your project structure
- Generate configuration file
- Discover all Django apps
- Create project-specific README and Claude policy

**Output Example:**
```
Initializing Django Context Memory in: /path/to/project

✓ Created configuration at: .context_memory_config.json
✓ Created memory directory: .app_memory
✓ Discovered 7 Django apps:
  - infrastructure
  - dashboard
  - backup
  - restore
  - monitoring
  - container_ops
  - settings

📝 Generating project documentation...
✓ Documentation generated

✅ Initialization complete!
```

### 3. Scan Your Apps
```bash
# Scan all apps at once (recommended)
django-context scan-all

# Or scan individual apps
django-context scan infrastructure
django-context scan dashboard
```

**Output Example:**
```
Scanning 7 apps...

  Scanning backup... ✓ (7 files)
  Scanning container_ops... ✓ (6 files)
  Scanning dashboard... ✓ (9 files)
  Scanning infrastructure... ✓ (27 files)
  Scanning monitoring... ✓ (6 files)
  Scanning restore... ✓ (6 files)
  Scanning settings... ✓ (11 files)

✅ Scan complete!
```

### 4. Build Context
```bash
# Build aggregated context for all apps (recommended)
django-context build-all

# Or build individual app context
django-context build infrastructure
```

**Output Example:**
```
Building aggregated context for all apps...

✅ Aggregated context built successfully!

Project: WebAppManager
  Apps: 7
  Files: 72

Global Statistics:
  Models: 3
  Views: 11
  URL patterns: 16
  Forms: 3
  Classes: 19
  Functions: 20

📁 Context saved to:
  .app_memory/claude_aggregated_context.json
```

### 5. Check Status
```bash
django-context status
```

**Output Example:**
```
Project: WebAppManager
Memory directory: .app_memory

Aggregated Context:
  ✓ Generated at: 2025-12-29T07:00:02.994907
  ✓ Total apps: 7
  ✓ Total files: 72

Apps (7):
  infrastructure
    Snapshot: ✓
    Context:  ✓
  dashboard
    Snapshot: ✓
    Context:  ✓
  ...
```

## What Gets Created

After running the commands above, you'll have:

```
your-project/
├── .app_memory/
│   ├── claude_aggregated_context.json  ← Main file for AI
│   ├── aggregated_context.json         ← Human-readable summary
│   ├── README.md                       ← Documentation
│   ├── CLAUDE_POLICY.md               ← AI policy
│   ├── infrastructure/
│   │   ├── snapshot.json
│   │   ├── app_memory.json
│   │   └── claude_context.json
│   ├── dashboard/
│   │   └── ...
│   └── ...
└── .context_memory_config.json        ← Configuration
```

## Configuration

Edit `.context_memory_config.json` to customize:

```json
{
  "project_name": "WebAppManager",
  "memory_dir": ".app_memory",
  "exclude_patterns": [
    "*/migrations/*",
    "*/__pycache__/*",
    "*.pyc"
  ],
  "deep_analysis": true,
  "auto_generate_docs": true
}
```

## Using with Claude Code

After building context, Claude Code will automatically read `.app_memory/claude_aggregated_context.json` and have complete knowledge of:

- All your Django models and fields
- All views and URL patterns
- Cross-app dependencies
- Technology stack
- Project structure

No more hallucinations or invented field names!

## Common Workflows

### Initial Setup (First Time)
```bash
django-context init
django-context scan-all
django-context build-all
```

### After Making Changes
```bash
# Option 1: Rebuild everything
django-context scan-all
django-context build-all

# Option 2: Rebuild single app
django-context scan infrastructure
django-context build infrastructure
django-context build-all  # Update aggregated context
```

### Check What's Been Built
```bash
django-context status
```

### Clean and Start Fresh
```bash
django-context clean
django-context scan-all
django-context build-all
```

## Programmatic Usage

You can also use the library directly in Python:

```python
from django_context_memory import ContextBuilder, ProjectScanner, Config
from pathlib import Path

# Initialize
project_root = Path('/path/to/project')
config = Config(project_root)
builder = ContextBuilder(project_root, config)

# Scan and build
builder.create_snapshot('infrastructure', stage='start')
context = builder.build_app_context('infrastructure')

# Build aggregated context
aggregated = builder.build_aggregated_context()

# Check status
status = builder.get_status()
```

## Troubleshooting

### Command not found: django-context
```bash
# Reinstall the package
pip install -e .

# Or use python -m
python -m django_context_memory.cli --help
```

### No apps discovered
Make sure you're in your Django project root (where `manage.py` is).

### Context is stale
```bash
django-context scan-all
django-context build-all
```

## Next Steps

- Read the full [README.md](README.md)
- Check generated `.app_memory/CLAUDE_POLICY.md`
- Explore the [examples directory](examples/)
- Report issues on GitHub

---

**Happy coding with AI assistance!** 🚀
