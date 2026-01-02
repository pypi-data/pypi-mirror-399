# Changelog

All notable changes to Django Context Memory will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.3] - 2025-12-29

### Fixed
- Version bump to resolve PyPI upload conflicts (1.0.0, 1.0.1, 1.0.2 were burned)

## [1.0.2] - 2025-12-29

### Fixed
- Version bump to resolve PyPI upload conflicts

## [1.0.1] - 2025-12-29

### Added
- **Built-in Django Web UI**: Web dashboard now included in the library package
- Django app configuration (`apps.py`, `views.py`, `urls.py`)
- Professional light-themed web interface for context management
- Templates packaged with library for easy Django integration

### Changed
- Consolidated all functionality into single library package
- Web UI is now optional Django integration (add to INSTALLED_APPS)
- Fixed Unicode emoji issues in CLI output (replaced with ASCII markers)
- Updated documentation with Django integration instructions

### Removed
- Dependency on separate `app_memory` Django app (functionality now built-in)

### Fixed
- CLI output now works on Windows consoles (no Unicode errors)
- Package imports properly configured for all usage methods

## [1.0.0] - 2025-12-29

### Added
- Initial production release of Django Context Memory
- Deep code analysis using Python AST
- Django-aware extraction (models, views, forms, admin, serializers, URLs)
- Project scanning and app discovery
- Context building with summaries
- Aggregated context generation with cross-app analysis
- CLI tools for easy usage (`django-context` command)
- Configuration management with validation
- Auto-generation of project-specific documentation
- Auto-generation of Claude-specific policies
- Pip-installable package
- Comprehensive documentation
- Comprehensive error handling and logging throughout all modules
- Configuration validation with type checking
- Environment variable overrides (DJANGO_CONTEXT_MEMORY_DIR, DJANGO_CONTEXT_VERBOSE, etc.)
- Utility module with helper functions (formatting, file operations, validation)
- Unicode encoding fallback for file reading
- Configurable file size limits and scan timeouts
- Enhanced exclude patterns for common directories (.venv, staticfiles, media)

### Features
- **Code Analyzer**: Extracts functions, classes, models, views, forms, URLs, imports
- **Project Scanner**: Discovers Django apps and scans file structure
- **Context Builder**: Builds structured context with versioning
- **CLI Interface**: Simple commands for initialization and context building
- **Documentation Generator**: Auto-generates README and policies
- **Configuration**: Flexible configuration via JSON file
- **Deep Analysis**: Full AST-based code intelligence
- **Cross-App Analysis**: Maps dependencies and relationships

### Technology Stack
- Python 3.8+
- No runtime dependencies (Django optional)
- Uses Python's built-in `ast` module for parsing

---

## Future Releases

### Planned Features
- Support for more frameworks (Flask, FastAPI)
- Integration with more AI assistants
- Web UI for context visualization
- Real-time context updates
- Context diffing and change detection
- Export to various formats
- Plugin system for custom analyzers

---

For detailed information about each release, see the commit history at:
https://github.com/GavinHolder/django-context-memory
