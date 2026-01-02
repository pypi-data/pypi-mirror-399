"""
Configuration management for Django Context Memory
"""

import json
import logging
import os
from pathlib import Path
from typing import Dict, List, Any, Optional

logger = logging.getLogger(__name__)


class Config:
    """Configuration manager for context memory system"""

    DEFAULT_CONFIG = {
        "project_name": None,
        "memory_dir": ".app_memory",
        "exclude_patterns": [
            "*/migrations/*",
            "*/__pycache__/*",
            "*.pyc",
            "*.pyo",
            ".git/*",
            ".svn/*",
            "*.sqlite3",
            "*.db",
            "node_modules/*",
            "venv/*",
            "env/*",
            ".venv/*",
            ".env/*",
            "staticfiles/*",
            "media/*",
        ],
        "deep_analysis": True,
        "auto_generate_docs": True,
        "include_tests": False,
        "include_migrations": False,
        "max_file_size": 1048576,  # 1MB
        "scan_timeout": 300,  # 5 minutes
        "verbose": False,
    }

    def __init__(self, project_root: Path, config_file: Optional[str] = None):
        """
        Initialize configuration

        Args:
            project_root: Path to the project root
            config_file: Optional path to config file (default: .context_memory_config.json)
        """
        self.project_root = Path(project_root)
        self.config_file = config_file or ".context_memory_config.json"
        self.config_path = self.project_root / self.config_file
        self.config = self._load_config()
        self._apply_environment_overrides()

    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file or use defaults"""
        config = self.DEFAULT_CONFIG.copy()

        if self.config_path.exists():
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    user_config = json.load(f)
                # Merge with defaults
                config.update(user_config)
                logger.debug(f"Loaded config from {self.config_path}")
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON in config file: {e}")
                logger.warning("Using default configuration")
            except Exception as e:
                logger.error(f"Could not load config file: {e}")
                logger.warning("Using default configuration")
        else:
            logger.debug("Config file not found, using defaults")

        return config

    def _apply_environment_overrides(self):
        """Apply environment variable overrides"""
        # DJANGO_CONTEXT_MEMORY_DIR environment variable
        env_memory_dir = os.getenv("DJANGO_CONTEXT_MEMORY_DIR")
        if env_memory_dir:
            self.config["memory_dir"] = env_memory_dir
            logger.debug(f"Memory dir overridden by environment: {env_memory_dir}")

        # DJANGO_CONTEXT_VERBOSE environment variable
        env_verbose = os.getenv("DJANGO_CONTEXT_VERBOSE")
        if env_verbose:
            self.config["verbose"] = env_verbose.lower() in ("1", "true", "yes")

        # DJANGO_CONTEXT_DEEP_ANALYSIS environment variable
        env_deep_analysis = os.getenv("DJANGO_CONTEXT_DEEP_ANALYSIS")
        if env_deep_analysis:
            self.config["deep_analysis"] = env_deep_analysis.lower() in ("1", "true", "yes")

    def save(self):
        """Save current configuration to file"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=2)
            logger.debug(f"Configuration saved to {self.config_path}")
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            raise

    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(key, default)

    def set(self, key: str, value: Any):
        """Set configuration value"""
        self.config[key] = value

    @property
    def memory_dir(self) -> Path:
        """Get memory directory path"""
        return self.project_root / self.config["memory_dir"]

    @property
    def project_name(self) -> str:
        """Get project name"""
        return self.config.get("project_name") or self.project_root.name

    @property
    def exclude_patterns(self) -> List[str]:
        """Get exclude patterns"""
        return self.config.get("exclude_patterns", [])

    @property
    def deep_analysis(self) -> bool:
        """Whether to perform deep code analysis"""
        return self.config.get("deep_analysis", True)

    @property
    def auto_generate_docs(self) -> bool:
        """Whether to auto-generate documentation"""
        return self.config.get("auto_generate_docs", True)

    def should_exclude(self, path: Path) -> bool:
        """Check if path should be excluded based on patterns"""
        from fnmatch import fnmatch

        path_str = str(path)
        for pattern in self.exclude_patterns:
            if fnmatch(path_str, pattern) or pattern in path.parts:
                return True
        return False

    def initialize(self):
        """Initialize configuration with defaults and save"""
        # Auto-detect project name
        if not self.config.get("project_name"):
            self.config["project_name"] = self.project_root.name

        # Create memory directory
        self.memory_dir.mkdir(parents=True, exist_ok=True)

        # Validate configuration
        self.validate()

        # Save configuration
        self.save()

        return self.config

    def validate(self) -> bool:
        """
        Validate configuration values

        Returns:
            True if valid

        Raises:
            ValueError: If configuration is invalid
        """
        errors = []

        # Validate max_file_size
        max_size = self.config.get("max_file_size")
        if max_size is not None and (not isinstance(max_size, int) or max_size < 0):
            errors.append(f"max_file_size must be a positive integer, got: {max_size}")

        # Validate scan_timeout
        timeout = self.config.get("scan_timeout")
        if timeout is not None and (not isinstance(timeout, int) or timeout < 1):
            errors.append(f"scan_timeout must be a positive integer, got: {timeout}")

        # Validate boolean fields
        bool_fields = ["deep_analysis", "auto_generate_docs", "include_tests", "include_migrations", "verbose"]
        for field in bool_fields:
            value = self.config.get(field)
            if value is not None and not isinstance(value, bool):
                errors.append(f"{field} must be boolean, got: {type(value).__name__}")

        # Validate exclude_patterns
        patterns = self.config.get("exclude_patterns")
        if patterns is not None and not isinstance(patterns, list):
            errors.append(f"exclude_patterns must be a list, got: {type(patterns).__name__}")

        if errors:
            error_msg = "Configuration validation failed:\n" + "\n".join(f"  - {e}" for e in errors)
            logger.error(error_msg)
            raise ValueError(error_msg)

        logger.debug("Configuration validated successfully")
        return True

    def reset_to_defaults(self):
        """Reset configuration to default values"""
        logger.info("Resetting configuration to defaults")
        self.config = self.DEFAULT_CONFIG.copy()
        # Reapply environment overrides
        self._apply_environment_overrides()

    @property
    def verbose(self) -> bool:
        """Whether to use verbose output"""
        return self.config.get("verbose", False)

    @property
    def max_file_size(self) -> int:
        """Maximum file size to process (in bytes)"""
        return self.config.get("max_file_size", 1048576)

    @property
    def scan_timeout(self) -> int:
        """Scan timeout in seconds"""
        return self.config.get("scan_timeout", 300)

    @property
    def include_tests(self) -> bool:
        """Whether to include test files"""
        return self.config.get("include_tests", False)

    @property
    def include_migrations(self) -> bool:
        """Whether to include migration files"""
        return self.config.get("include_migrations", False)
