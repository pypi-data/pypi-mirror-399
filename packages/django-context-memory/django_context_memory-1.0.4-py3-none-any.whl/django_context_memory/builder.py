"""
Context building functionality
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional
from .config import Config
from .scanner import ProjectScanner

logger = logging.getLogger(__name__)


class ContextBuilder:
    """Builds structured context from scanned project data"""

    def __init__(self, project_root: Path, config: Optional[Config] = None):
        """
        Initialize context builder

        Args:
            project_root: Path to Django project root
            config: Optional configuration object
        """
        self.project_root = Path(project_root)
        self.config = config or Config(project_root)
        self.scanner = ProjectScanner(project_root, self.config)

    def create_snapshot(self, app_name: str, stage: str = "start", deep_analysis: bool = None) -> Dict[str, Any]:
        """
        Create a snapshot for a specific app

        Args:
            app_name: Name of the Django app
            stage: 'start' or 'end'
            deep_analysis: Whether to perform deep analysis

        Returns:
            Snapshot data dictionary
        """
        logger.info(f"Creating {stage} snapshot for {app_name}")

        # Validate app exists
        app_path = self.project_root / app_name
        if not app_path.exists():
            logger.error(f"App '{app_name}' not found at {app_path}")
            raise FileNotFoundError(f"App '{app_name}' not found at {app_path}")

        if not app_path.is_dir():
            logger.error(f"App path is not a directory: {app_path}")
            raise ValueError(f"App path is not a directory: {app_path}")

        # Validate stage
        if stage not in ("start", "end"):
            logger.warning(f"Invalid stage '{stage}', using 'start'")
            stage = "start"

        try:
            memory_dir = self.scanner.get_app_memory_dir(app_name)
            snapshot_file = memory_dir / "snapshot.json"

            files = self.scanner.scan_app(app_path, deep_analysis=deep_analysis)

            snapshot = {
                "app": app_name,
                "stage": stage,
                "timestamp": datetime.utcnow().isoformat(),
                "deep_analysis": deep_analysis if deep_analysis is not None else self.config.deep_analysis,
                "files": files,
            }

            # Save snapshot
            with open(snapshot_file, 'w', encoding='utf-8') as f:
                json.dump(snapshot, f, indent=2)

            logger.info(f"Snapshot saved: {len(files)} files scanned")
            return snapshot

        except Exception as e:
            logger.error(f"Failed to create snapshot for {app_name}: {e}")
            raise

    def build_app_context(self, app_name: str) -> Dict[str, Any]:
        """
        Build context for a specific app from its snapshot

        Args:
            app_name: Name of the Django app

        Returns:
            Context payload dictionary
        """
        logger.info(f"Building context for {app_name}")

        try:
            memory_dir = self.scanner.get_app_memory_dir(app_name)
            snapshot_file = memory_dir / "snapshot.json"
            app_memory_file = memory_dir / "app_memory.json"
            claude_context_file = memory_dir / "claude_context.json"

            if not snapshot_file.exists():
                logger.error(f"No snapshot found for {app_name}")
                raise FileNotFoundError(
                    f"No snapshot found for {app_name}. Run create_snapshot() first."
                )

            # Load snapshot
            try:
                with open(snapshot_file, 'r', encoding='utf-8') as f:
                    snap = json.load(f)
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON in snapshot for {app_name}: {e}")
                raise ValueError(f"Corrupted snapshot file for {app_name}")

            # Build comprehensive context summary
            context_summary = self._build_context_summary(snap["files"], app_name)

            payload = {
                "app": app_name,
                "generated_at": datetime.utcnow().isoformat(),
                "file_count": len(snap["files"]),
                "deep_analysis": snap.get("deep_analysis", False),
                "stage": snap.get("stage", "unknown"),
                "files": snap["files"],
                "summary": context_summary,
            }

            # Save versioned memory
            self._save_memory(app_name, payload, app_memory_file)

            # Save Claude-optimized context
            with open(claude_context_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "type": "claude_context",
                    "machine": True,
                    "payload": payload,
                }, f, indent=2)

            logger.info(f"Context built for {app_name}: {payload['file_count']} files")
            return payload

        except Exception as e:
            logger.error(f"Failed to build context for {app_name}: {e}")
            raise

    def build_aggregated_context(self) -> Dict[str, Any]:
        """
        Build aggregated context for all apps in project

        Returns:
            Aggregated context dictionary
        """
        logger.info("Building aggregated context for all apps")

        all_apps_data = []
        total_files = 0
        apps_processed = []
        all_app_summaries = {}

        # Ensure memory directory exists
        if not self.config.memory_dir.exists():
            logger.warning(f"Memory directory does not exist: {self.config.memory_dir}")
            self.config.memory_dir.mkdir(parents=True, exist_ok=True)

        try:
            # Discover all apps in the project
            apps = self.scanner.discover_apps()
            logger.info(f"Discovered {len(apps)} apps to process")

            # Create fresh snapshots for all apps first with deep analysis
            for app_info in apps:
                app_name = app_info['name']
                try:
                    logger.debug(f"Creating snapshot for {app_name}")
                    # IMPORTANT: Always use deep_analysis=True for full code intelligence
                    self.create_snapshot(app_name, stage='start', deep_analysis=True)
                except Exception as e:
                    logger.error(f"Failed to create snapshot for {app_name}: {e}")
                    continue

            # Now build context from the fresh snapshots
            for app_info in apps:
                app_name = app_info['name']
                try:
                    logger.debug(f"Building context for {app_name}")

                    # Build individual app context
                    app_payload = self.build_app_context(app_name)

                    all_apps_data.append({
                        "app": app_name,
                        "stage": app_payload.get("stage", "unknown"),
                        "timestamp": app_payload.get("generated_at"),
                        "file_count": app_payload.get("file_count", 0),
                        "summary": app_payload.get("summary", {})
                    })

                    # Store summary for cross-app analysis
                    all_app_summaries[app_name] = app_payload.get("summary", {})

                    total_files += app_payload.get("file_count", 0)
                    apps_processed.append(app_name)

                except Exception as e:
                    logger.error(f"Error processing {app_name}: {e}")
                    continue

            # Build global project summary
            global_summary = self._build_global_summary(all_app_summaries, apps_processed)

            # Create aggregated context
            aggregated_payload = {
                "type": "aggregated_context",
                "generated_at": datetime.utcnow().isoformat(),
                "project": self.config.project_name,
                "total_apps": len(apps_processed),
                "total_files": total_files,
                "apps_included": apps_processed,
                "apps": all_apps_data,
                "global_summary": global_summary,
            }

            # Save to root of memory directory
            aggregated_file = self.config.memory_dir / "aggregated_context.json"
            with open(aggregated_file, 'w', encoding='utf-8') as f:
                json.dump(aggregated_payload, f, indent=2)

            # Save machine-readable version for Claude
            claude_aggregated_file = self.config.memory_dir / "claude_aggregated_context.json"
            with open(claude_aggregated_file, 'w', encoding='utf-8') as f:
                json.dump({
                    "type": "claude_aggregated_context",
                    "machine": True,
                    "payload": aggregated_payload,
                }, f, indent=2)

            logger.info(f"Aggregated context built: {len(apps_processed)} apps, {total_files} files")
            return aggregated_payload

        except Exception as e:
            logger.error(f"Failed to build aggregated context: {e}")
            raise

    def _build_context_summary(self, files: List[Dict], app_name: str) -> Dict[str, Any]:
        """Build comprehensive summary of app context"""
        summary = {
            "models": [],
            "views": [],
            "url_patterns": [],
            "forms": [],
            "admin_classes": [],
            "serializers": [],
            "all_classes": [],
            "all_functions": [],
            "dependencies": {
                "django_apps": set(),
                "third_party": set(),
                "local_apps": set(),
                "standard_library": set()
            },
            "file_types": {},
            "constants": []
        }

        for file_info in files:
            file_type = file_info.get("type", "unknown")
            summary["file_types"][file_type] = summary["file_types"].get(file_type, 0) + 1

            # Extract models
            if "models" in file_info:
                for model in file_info["models"]:
                    summary["models"].append({
                        "name": model["name"],
                        "file": file_info["path"],
                        "fields": [f["name"] + ": " + f["type"] for f in model["fields"]],
                        "field_count": len(model["fields"]),
                        "methods": model["methods"]
                    })

            # Extract views
            if "views" in file_info:
                for view in file_info["views"]:
                    summary["views"].append({
                        "name": view["name"],
                        "type": view["type"],
                        "file": file_info["path"]
                    })

            # Extract URL patterns
            if "url_patterns" in file_info:
                for pattern in file_info["url_patterns"]:
                    summary["url_patterns"].append({
                        "route": pattern.get("route", ""),
                        "view": pattern.get("view", ""),
                        "name": pattern.get("name", ""),
                        "file": file_info["path"]
                    })

            # Extract forms
            if "forms" in file_info:
                for form in file_info["forms"]:
                    summary["forms"].append({
                        "name": form["name"],
                        "type": form["type"],
                        "fields": [f["name"] for f in form["fields"]],
                        "file": file_info["path"]
                    })

            # Extract admin classes
            if "admin_classes" in file_info:
                for admin in file_info["admin_classes"]:
                    summary["admin_classes"].append({
                        "name": admin["name"],
                        "file": file_info["path"]
                    })

            # Extract serializers
            if "serializers" in file_info:
                for serializer in file_info["serializers"]:
                    summary["serializers"].append({
                        "name": serializer["name"],
                        "type": serializer["type"],
                        "fields": [f["name"] for f in serializer["fields"]],
                        "file": file_info["path"]
                    })

            # Aggregate all classes
            if "classes" in file_info:
                for cls in file_info["classes"]:
                    summary["all_classes"].append({
                        "name": cls["name"],
                        "file": file_info["path"],
                        "bases": cls["bases"],
                        "methods": [m["name"] for m in cls["methods"]]
                    })

            # Aggregate all functions
            if "functions" in file_info:
                for func in file_info["functions"]:
                    summary["all_functions"].append({
                        "name": func["name"],
                        "file": file_info["path"],
                        "params": [p["name"] for p in func["params"]],
                        "decorators": func["decorators"]
                    })

            # Aggregate dependencies
            if "imports" in file_info:
                imports = file_info["imports"]
                if isinstance(imports, dict):
                    summary["dependencies"]["django_apps"].update(imports.get("django", []))
                    summary["dependencies"]["third_party"].update(imports.get("third_party", []))
                    summary["dependencies"]["local_apps"].update(imports.get("local_apps", []))
                    summary["dependencies"]["standard_library"].update(imports.get("standard_library", []))

            # Aggregate constants
            if "constants" in file_info:
                for const in file_info["constants"]:
                    summary["constants"].append({
                        "name": const["name"],
                        "value": const["value"],
                        "file": file_info["path"]
                    })

        # Convert sets to sorted lists
        summary["dependencies"] = {
            key: sorted(list(value)) for key, value in summary["dependencies"].items()
        }

        return summary

    def _build_global_summary(self, all_app_summaries: Dict, apps_processed: List) -> Dict[str, Any]:
        """Build global project summary with cross-app analysis"""
        global_summary = {
            "all_models": [],
            "all_views": [],
            "all_url_patterns": [],
            "all_forms": [],
            "cross_app_imports": {},
            "technology_stack": {
                "django_components": set(),
                "third_party_packages": set(),
            },
            "app_relationships": {},
            "statistics": {
                "total_models": 0,
                "total_views": 0,
                "total_url_patterns": 0,
                "total_forms": 0,
                "total_classes": 0,
                "total_functions": 0,
            }
        }

        # Aggregate across all apps
        for app_name, summary in all_app_summaries.items():
            for model in summary.get("models", []):
                global_summary["all_models"].append({
                    "app": app_name,
                    "name": model["name"],
                    "fields": model["fields"],
                    "field_count": model["field_count"]
                })
                global_summary["statistics"]["total_models"] += 1

            for view in summary.get("views", []):
                global_summary["all_views"].append({
                    "app": app_name,
                    "name": view["name"],
                    "type": view["type"]
                })
                global_summary["statistics"]["total_views"] += 1

            for pattern in summary.get("url_patterns", []):
                global_summary["all_url_patterns"].append({
                    "app": app_name,
                    "route": pattern["route"],
                    "view": pattern["view"],
                    "name": pattern.get("name", "")
                })
                global_summary["statistics"]["total_url_patterns"] += 1

            for form in summary.get("forms", []):
                global_summary["all_forms"].append({
                    "app": app_name,
                    "name": form["name"],
                    "type": form["type"]
                })
                global_summary["statistics"]["total_forms"] += 1

            global_summary["statistics"]["total_classes"] += len(summary.get("all_classes", []))
            global_summary["statistics"]["total_functions"] += len(summary.get("all_functions", []))

            deps = summary.get("dependencies", {})
            local_imports = deps.get("local_apps", [])
            if local_imports:
                global_summary["cross_app_imports"][app_name] = local_imports

            global_summary["technology_stack"]["django_components"].update(deps.get("django_apps", []))
            global_summary["technology_stack"]["third_party_packages"].update(deps.get("third_party", []))

        # Analyze app relationships
        for app_name, imports in global_summary["cross_app_imports"].items():
            relationships = []
            for import_str in imports:
                for other_app in apps_processed:
                    if other_app in import_str and other_app != app_name:
                        relationships.append(other_app)
            if relationships:
                global_summary["app_relationships"][app_name] = list(set(relationships))

        # Convert sets to sorted lists
        global_summary["technology_stack"] = {
            key: sorted(list(value)) for key, value in global_summary["technology_stack"].items()
        }

        return global_summary

    def _save_memory(self, app_name: str, payload: Dict, app_memory_file: Path):
        """Save memory with versioning (previous + latest)"""
        memory = {"previous": None, "latest": None}

        if app_memory_file.exists():
            try:
                with open(app_memory_file, 'r') as f:
                    memory = json.load(f)
            except Exception:
                pass

        memory["previous"] = memory["latest"]
        memory["latest"] = payload

        with open(app_memory_file, 'w') as f:
            json.dump(memory, f, indent=2)

    def clean_context(self, app_name: Optional[str] = None):
        """
        Clean generated context files

        Args:
            app_name: Optional app name to clean (cleans all if None)
        """
        if app_name:
            app_dir = self.config.memory_dir / app_name
            if app_dir.exists():
                import shutil
                shutil.rmtree(app_dir)
                print(f"Cleaned context for {app_name}")
        else:
            if self.config.memory_dir.exists():
                import shutil
                shutil.rmtree(self.config.memory_dir)
                self.config.memory_dir.mkdir()
                print("Cleaned all context files")

    def get_status(self) -> Dict[str, Any]:
        """
        Get current context status

        Returns:
            Status dictionary with build info
        """
        status = {
            "project": self.config.project_name,
            "memory_dir": str(self.config.memory_dir),
            "apps": []
        }

        if not self.config.memory_dir.exists():
            status["message"] = "No context built yet"
            return status

        # Check aggregated context
        aggregated_file = self.config.memory_dir / "claude_aggregated_context.json"
        if aggregated_file.exists():
            try:
                with open(aggregated_file, 'r') as f:
                    agg = json.load(f)
                    payload = agg.get("payload", {})
                    status["aggregated"] = {
                        "exists": True,
                        "generated_at": payload.get("generated_at"),
                        "total_apps": payload.get("total_apps"),
                        "total_files": payload.get("total_files")
                    }
            except Exception:
                status["aggregated"] = {"exists": False}
        else:
            status["aggregated"] = {"exists": False}

        # Check per-app status
        for app_dir in self.config.memory_dir.iterdir():
            if app_dir.is_dir():
                app_status = {
                    "name": app_dir.name,
                    "snapshot": (app_dir / "snapshot.json").exists(),
                    "context": (app_dir / "claude_context.json").exists(),
                }
                status["apps"].append(app_status)

        return status
