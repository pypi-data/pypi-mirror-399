"""
Project and app scanning functionality
"""

import hashlib
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from .config import Config
from .analyzer import CodeAnalyzer

logger = logging.getLogger(__name__)


class ProjectScanner:
    """Scans Django projects to discover apps and generate context"""

    def __init__(self, project_root: Path, config: Optional[Config] = None):
        """
        Initialize scanner

        Args:
            project_root: Path to Django project root
            config: Optional configuration object
        """
        self.project_root = Path(project_root)
        self.config = config or Config(project_root)

    def discover_apps(self) -> List[Dict[str, str]]:
        """
        Discover all Django apps in the project

        Returns:
            List of dictionaries with app name and path
        """
        apps = []
        try:
            for item in self.project_root.iterdir():
                if item.is_dir() and not item.name.startswith('.') and not item.name.startswith('_'):
                    # Check if it's a Django app (has apps.py, models.py, or views.py)
                    try:
                        if (item / 'apps.py').exists() or (item / 'models.py').exists() or (item / 'views.py').exists():
                            if not self.config.should_exclude(item):
                                apps.append({
                                    'name': item.name,
                                    'path': str(item)
                                })
                    except PermissionError:
                        logger.warning(f"Permission denied accessing {item}")
                        continue
        except Exception as e:
            logger.error(f"Error discovering apps in {self.project_root}: {e}")
            return []

        return sorted(apps, key=lambda x: x['name'])

    def scan_app(self, app_path: Path, deep_analysis: bool = None) -> List[Dict[str, Any]]:
        """
        Scan a specific app directory

        Args:
            app_path: Path to the app directory
            deep_analysis: Whether to perform deep analysis (uses config if None)

        Returns:
            List of file information dictionaries
        """
        # Validate app_path
        if not app_path.exists():
            raise ValueError(f"App path does not exist: {app_path}")
        if not app_path.is_dir():
            raise ValueError(f"App path is not a directory: {app_path}")

        if deep_analysis is None:
            deep_analysis = self.config.deep_analysis

        files = []
        try:
            for p in app_path.rglob("*"):
                if p.is_file() and not self.config.should_exclude(p):
                    try:
                        if deep_analysis:
                            # Use deep code analysis
                            file_info = self._analyze_file(p, app_path)
                        else:
                            # Legacy mode: just metadata
                            file_info = {
                                "path": str(p.relative_to(app_path)),
                                "hash": self._fingerprint(p),
                                "size": p.stat().st_size,
                            }
                        files.append(file_info)
                    except Exception as e:
                        logger.warning(f"Error scanning file {p}: {e}")
                        continue
        except Exception as e:
            logger.error(f"Error scanning app {app_path}: {e}")
            raise

        return files

    def _analyze_file(self, file_path: Path, app_root: Path) -> Dict[str, Any]:
        """
        Analyze a single file

        Args:
            file_path: Path to the file
            app_root: Root directory of the app

        Returns:
            File analysis dictionary
        """
        # Only analyze Python files
        if file_path.suffix != '.py':
            return {
                "path": str(file_path.relative_to(app_root)),
                "type": "non_python",
                "size": file_path.stat().st_size,
                "hash": self._fingerprint(file_path),
                "extension": file_path.suffix
            }

        analyzer = CodeAnalyzer(file_path, app_root)
        analysis = analyzer.analyze()
        # Add hash for change detection
        analysis["hash"] = self._fingerprint(file_path)
        return analysis

    def _fingerprint(self, path: Path) -> str:
        """
        Generate SHA256 hash of file contents

        Args:
            path: Path to the file

        Returns:
            SHA256 hash string
        """
        try:
            return hashlib.sha256(path.read_bytes()).hexdigest()
        except PermissionError:
            logger.warning(f"Permission denied reading {path}")
            return "permission_denied"
        except FileNotFoundError:
            logger.error(f"File not found: {path}")
            return "not_found"
        except Exception as e:
            logger.error(f"Error fingerprinting {path}: {e}")
            return "unreadable"

    def scan_project(self, deep_analysis: bool = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        Scan entire project

        Args:
            deep_analysis: Whether to perform deep analysis (uses config if None)

        Returns:
            Dictionary mapping app names to their file lists
        """
        apps = self.discover_apps()
        project_scan = {}

        logger.info(f"Scanning project with {len(apps)} apps")

        for app_info in apps:
            app_name = app_info['name']
            app_path = Path(app_info['path'])

            logger.info(f"Scanning {app_name}...")
            try:
                files = self.scan_app(app_path, deep_analysis=deep_analysis)
                project_scan[app_name] = files
                logger.debug(f"Scanned {app_name}: {len(files)} files")
            except Exception as e:
                logger.error(f"Failed to scan {app_name}: {e}")
                project_scan[app_name] = []

        return project_scan

    def get_app_memory_dir(self, app_name: str) -> Path:
        """
        Get memory directory for specific app

        Args:
            app_name: Name of the app

        Returns:
            Path to app's memory directory
        """
        app_memory_dir = self.config.memory_dir / app_name
        app_memory_dir.mkdir(parents=True, exist_ok=True)
        return app_memory_dir

    def get_project_info(self) -> Dict[str, Any]:
        """
        Get basic project information

        Returns:
            Dictionary with project metadata
        """
        apps = self.discover_apps()

        # Try to detect Django version
        django_version = None
        requirements_file = self.project_root / "requirements.txt"
        if requirements_file.exists():
            try:
                content = requirements_file.read_text()
                import re
                match = re.search(r'Django[>=<~!]+([\d.]+)', content, re.IGNORECASE)
                if match:
                    django_version = match.group(1)
            except Exception:
                pass

        return {
            "name": self.config.project_name,
            "root": str(self.project_root),
            "apps_count": len(apps),
            "apps": [app['name'] for app in apps],
            "django_version": django_version,
            "python_version": None,  # Could detect from runtime.txt or similar
        }
