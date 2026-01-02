# Django Context Memory - CLI Guide

Complete guide to using the `django-context` command-line interface.

---

## Table of Contents

- [Installation](#installation)
- [Quick Start](#quick-start)
- [Global Flags](#global-flags)
- [Commands](#commands)
  - [init](#init)
  - [scan](#scan)
  - [scan-all](#scan-all)
  - [build](#build)
  - [build-all](#build-all)
  - [status](#status)
  - [clean](#clean)
  - [validate](#validate)
  - [generate-docs](#generate-docs)
- [Workflow Examples](#workflow-examples)
- [Configuration](#configuration)
- [Troubleshooting](#troubleshooting)

---

## Installation

### From PyPI (Once Published)

```bash
pip install django-context-memory
```

### From Source (Development)

```bash
# Clone or navigate to the library directory
cd django_context_memory

# Install in editable mode
pip install -e .

# Verify installation
django-context --version
```

---

## Quick Start

```bash
# Navigate to your Django project root (where manage.py is)
cd /path/to/your/django/project

# 1. Initialize context memory
django-context init

# 2. Scan all apps
django-context scan-all

# 3. Build aggregated context
django-context build-all

# 4. Check status
django-context status
```

Your context is now ready! The aggregated context file is at:
`.app_memory/claude_aggregated_context.json`

---

## Global Flags

These flags work with any command:

### `--version`
Show version number and exit.

```bash
django-context --version
# Output: django-context-memory 1.0.0
```

### `--verbose` / `-v`
Enable detailed logging output.

```bash
django-context build-all --verbose
```

### `--config <file>`
Specify a custom configuration file path.

```bash
django-context init --config /path/to/custom_config.json
```

---

## Commands

### `init`

Initialize Django Context Memory in your project.

**Usage:**
```bash
django-context init
```

**What it does:**
- Creates `.context_memory_config.json` configuration file
- Creates `.app_memory/` directory for storing context data
- Discovers all Django apps in your project
- Generates project documentation (if `auto_generate_docs` is enabled)

**Output:**
```
Initializing Django Context Memory in: /path/to/project

[OK] Created configuration at: .context_memory_config.json
[OK] Created memory directory: .app_memory
[OK] Discovered 5 Django apps:
  - app1
  - app2
  - app3
  - app4
  - app5

📝 Generating project documentation...
[OK] Documentation generated

[SUCCESS] Initialization complete!

Next steps:
  1. Run: django-context scan-all
  2. Run: django-context build-all
  3. Your AI assistant can now read .app_memory/claude_aggregated_context.json
```

---

### `scan`

Scan a specific Django app and create a snapshot.

**Usage:**
```bash
django-context scan <app_name>
```

**Flags:**
- `--dry-run` - Show what would be scanned without actually scanning

**Examples:**
```bash
# Scan the 'users' app
django-context scan users

# Preview what would be scanned
django-context scan users --dry-run
```

**Output:**
```
Scanning app: users
[OK] Created snapshot with 15 files
  Deep analysis: True
```

**What it creates:**
- `.app_memory/users/snapshot.json` - Contains file analysis data

---

### `scan-all`

Scan all Django apps in the project.

**Usage:**
```bash
django-context scan-all
```

**Flags:**
- `--dry-run` - Show what would be scanned without actually scanning

**Examples:**
```bash
# Scan all apps
django-context scan-all

# Preview all apps that would be scanned
django-context scan-all --dry-run
```

**Output:**
```
Scanning 5 apps...

  Scanning users... [OK] (15 files)
  Scanning products... [OK] (23 files)
  Scanning orders... [OK] (18 files)
  Scanning payments... [OK] (12 files)
  Scanning dashboard... [OK] (8 files)

[SUCCESS] Scan complete!
```

---

### `build`

Build context for a specific app from its snapshot.

**Usage:**
```bash
django-context build <app_name>
```

**Examples:**
```bash
# Build context for 'users' app
django-context build users
```

**Output:**
```
Building context for: users
✓ Context built successfully
  Files: 15
  Models: 3
  Views: 8
  URL patterns: 12
```

**What it creates:**
- `.app_memory/users/app_memory.json` - Versioned context data
- `.app_memory/users/claude_context.json` - Claude-optimized format

**Requirements:**
- Must run `django-context scan <app_name>` first

---

### `build-all`

Build aggregated context for all apps in the project.

**Usage:**
```bash
django-context build-all
```

**What it does:**
1. Discovers all Django apps
2. Creates fresh snapshots with deep analysis for each app
3. Builds individual context for each app
4. Generates aggregated context combining all apps
5. Performs cross-app dependency analysis

**Output:**
```
Building aggregated context for all apps...

✅ Aggregated context built successfully!

Project: MyProject
  Apps: 5
  Files: 76

Global Statistics:
  Models: 12
  Views: 34
  URL patterns: 45
  Forms: 8
  Classes: 67
  Functions: 89

📁 Context saved to:
  .app_memory/claude_aggregated_context.json
```

**What it creates:**
- `.app_memory/claude_aggregated_context.json` - **Main output file**
- `.app_memory/aggregated_context.json` - Human-readable version
- Updates all individual app contexts

**This is the most important command** - run this to get complete project intelligence!

---

### `status`

Show current context memory status.

**Usage:**
```bash
django-context status
```

**Output:**
```
Project: MyProject
Memory directory: .app_memory

Aggregated Context:
  ✓ Generated at: 2025-12-29T12:34:56
  ✓ Total apps: 5
  ✓ Total files: 76

Apps (5):
  users
    Snapshot: ✓
    Context:  ✓
  products
    Snapshot: ✓
    Context:  ✓
  orders
    Snapshot: ✓
    Context:  ✓
  payments
    Snapshot: ✗
    Context:  ✗
  dashboard
    Snapshot: ✓
    Context:  ✓
```

**Symbols:**
- ✓ = Exists
- ✗ = Not found

---

### `clean`

Clean generated context files.

**Usage:**
```bash
django-context clean [--app <app_name>]
```

**Flags:**
- `--app <app_name>` - Clean only a specific app (optional)

**Examples:**
```bash
# Clean all context files (prompts for confirmation)
django-context clean

# Clean context for specific app
django-context clean --app users
```

**Output:**
```
Clean all context files? (y/N): y
Cleaning context files...
[OK] Cleaned .app_memory directory
```

**Warning:** This deletes all generated context data!

---

### `validate`

Validate configuration and project setup.

**Usage:**
```bash
django-context validate
```

**What it checks:**
- Django project indicators (manage.py, settings.py, wsgi.py)
- Configuration file existence and validity
- Memory directory existence
- Discovered apps

**Output (Success):**
```
Validating Django Context Memory setup...

[OK] Django project detected
[OK] Configuration file exists: .context_memory_config.json
[OK] Configuration is valid
[OK] Memory directory exists: .app_memory
[OK] Found 5 Django apps:
  - users
  - products
  - orders
  - payments
  - dashboard

[SUCCESS] Validation complete!
```

**Output (Issues Found):**
```
Validating Django Context Memory setup...

[WARNING] Django project indicators not found (manage.py, settings.py, wsgi.py)
[WARNING] No configuration file found at .context_memory_config.json
  Run 'django-context init' to create one
[WARNING] Memory directory not found: .app_memory
[OK] Found 5 Django apps:
  - users
  - products
  - orders
  - payments
  - dashboard

[SUCCESS] Validation complete!
```

---

### `generate-docs`

Generate project documentation without full initialization.

**Usage:**
```bash
django-context generate-docs
```

**What it creates:**
- `.app_memory/PROJECT_README.md` - Project-specific README
- `.app_memory/CLAUDE_POLICY.md` - Claude-specific usage policies

**Output:**
```
Generating project documentation...

[OK] Documentation generated:
  - .app_memory/PROJECT_README.md
  - .app_memory/CLAUDE_POLICY.md

[SUCCESS] Documentation generation complete!
```

**Use case:** Regenerate docs after project changes without re-initializing.

---

## Workflow Examples

### First-Time Setup

```bash
# Step 1: Initialize
django-context init

# Step 2: Build everything
django-context build-all

# Step 3: Verify
django-context status
```

### Daily Development Workflow

```bash
# After making code changes, rebuild context
django-context build-all

# Check what changed
django-context status
```

### Working with Specific Apps

```bash
# Scan only the app you're working on
django-context scan myapp

# Build context for that app
django-context build myapp

# When ready, update the aggregated context
django-context build-all
```

### Debugging Setup Issues

```bash
# Check if everything is configured correctly
django-context validate

# Enable verbose logging to see what's happening
django-context build-all --verbose
```

### Preview Before Scanning

```bash
# See what apps would be scanned
django-context scan-all --dry-run

# See what a specific app would include
django-context scan myapp --dry-run
```

---

## Configuration

### Configuration File

The `.context_memory_config.json` file controls behavior:

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
    ".venv/*",
    "staticfiles/*",
    "media/*"
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
# Change memory directory
export DJANGO_CONTEXT_MEMORY_DIR=".custom_memory"

# Enable verbose logging
export DJANGO_CONTEXT_VERBOSE=1

# Disable deep analysis
export DJANGO_CONTEXT_DEEP_ANALYSIS=0

# Then run commands normally
django-context build-all
```

### Key Settings

- **`deep_analysis`**: Enable full AST-based code analysis (recommended: `true`)
- **`auto_generate_docs`**: Generate docs during init (recommended: `true`)
- **`include_tests`**: Include test files in analysis (default: `false`)
- **`include_migrations`**: Include migration files (default: `false`)
- **`max_file_size`**: Skip files larger than this (bytes)
- **`scan_timeout`**: Maximum time for scanning (seconds)

---

## Troubleshooting

### "No Django apps discovered"

**Problem:** `django-context` can't find your apps.

**Solutions:**
1. Make sure you're in the Django project root (where `manage.py` is)
2. Check that your apps are in `INSTALLED_APPS` in settings.py
3. Run `django-context validate` to diagnose

### "No snapshot found for app"

**Problem:** Trying to build context before scanning.

**Solution:**
```bash
# Scan first
django-context scan myapp

# Then build
django-context build myapp
```

Or just use:
```bash
# This does everything
django-context build-all
```

### "Permission denied"

**Problem:** Can't write to `.app_memory` directory.

**Solution:**
```bash
# Linux/Mac
chmod -R u+w .app_memory

# Or delete and reinitialize
rm -rf .app_memory
django-context init
```

### "Command not found: django-context"

**Problem:** CLI not installed or not in PATH.

**Solutions:**
```bash
# Reinstall the package
pip uninstall django-context-memory
pip install django-context-memory

# Or for development
pip install -e ./django_context_memory

# Verify
django-context --version
```

### Empty context / No functions found

**Problem:** Context is built but shows empty data.

**Solution:**
1. Make sure `deep_analysis` is enabled in config
2. Run `django-context build-all` (not just `build`)
3. Check that your files have actual code (not just stubs)
4. Use `--verbose` to see what's being scanned:
   ```bash
   django-context build-all --verbose
   ```

### Context file is outdated

**Problem:** Code changed but context still shows old data.

**Solution:**
```bash
# Rebuild to get fresh analysis
django-context build-all

# Or clean and rebuild
django-context clean
django-context build-all
```

---

## Advanced Usage

### Custom Configuration File

```bash
# Use a different config file
django-context init --config .my_custom_config.json
django-context build-all --config .my_custom_config.json
```

### CI/CD Integration

```bash
#!/bin/bash
# .github/workflows/update-context.sh

# Install library
pip install django-context-memory

# Build context
django-context build-all

# Commit updated context
git add .app_memory/
git commit -m "Update context memory"
git push
```

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

# Rebuild context before every commit
django-context build-all --quiet

# Add updated context to commit
git add .app_memory/
```

---

## Output Files

### `.app_memory/claude_aggregated_context.json`

**Main output file** - Contains complete project intelligence:
- All apps' models, views, forms, functions, classes
- Cross-app dependencies
- Global statistics
- Machine-readable format optimized for AI assistants

### `.app_memory/<app>/snapshot.json`

Per-app snapshot with:
- File-by-file analysis
- Imports and dependencies
- Functions, classes, views, models
- Hash fingerprints for change detection

### `.app_memory/<app>/claude_context.json`

Claude-optimized context for individual app.

### `.app_memory/PROJECT_README.md`

Auto-generated project documentation.

### `.app_memory/CLAUDE_POLICY.md`

AI assistant usage policies specific to your project.

---

## Getting Help

```bash
# Show all commands
django-context --help

# Show help for specific command
django-context build --help
django-context scan-all --help
```

---

## Next Steps

1. **First time?** Run `django-context init` then `django-context build-all`
2. **Need to update?** Just run `django-context build-all` again
3. **Debugging?** Use `django-context validate` and `--verbose` flag
4. **Integrating with AI?** Point your AI assistant to `.app_memory/claude_aggregated_context.json`

---

**Django Context Memory** - Deep code intelligence for AI-assisted development
