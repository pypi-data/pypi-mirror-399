"""
Django Context Memory - Deep code intelligence for AI assistants

A library for generating structured, machine-readable context from Django codebases.
"""

__version__ = "1.0.4"

# Core library components
from .config import Config
from .scanner import ProjectScanner
from .analyzer import CodeAnalyzer
from .builder import ContextBuilder
from .doc_generator import DocumentationGenerator
from .utils import setup_logging, validate_django_project, safe_read_file

__all__ = [
    # Version
    "__version__",

    # Core classes
    "Config",
    "ProjectScanner",
    "CodeAnalyzer",
    "ContextBuilder",
    "DocumentationGenerator",

    # Utilities
    "setup_logging",
    "validate_django_project",
    "safe_read_file",
]
