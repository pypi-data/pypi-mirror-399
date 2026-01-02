"""
Command-line interface for Django Context Memory
"""

import argparse
import sys
from pathlib import Path
from .config import Config
from .scanner import ProjectScanner
from .builder import ContextBuilder
from .doc_generator import DocumentationGenerator
from . import utils
from . import __version__


def get_project_root():
    """Get the current project root directory"""
    return Path.cwd()


def cmd_init(args):
    """Initialize context memory in project"""
    project_root = get_project_root()
    config = Config(project_root)

    print(f"Initializing Django Context Memory in: {project_root}")
    print()

    # Initialize configuration
    config.initialize()
    print(f"[OK] Created configuration at: {config.config_path}")

    # Create memory directory
    config.memory_dir.mkdir(exist_ok=True)
    print(f"[OK] Created memory directory: {config.memory_dir}")

    # Discover apps
    scanner = ProjectScanner(project_root, config)
    apps = scanner.discover_apps()
    print(f"[OK] Discovered {len(apps)} Django apps:")
    for app in apps:
        print(f"  - {app['name']}")

    # Generate documentation if enabled
    if config.auto_generate_docs:
        print("\n📝 Generating project documentation...")
        doc_gen = DocumentationGenerator(project_root, config)
        doc_gen.generate_all()
        print("[OK] Documentation generated")

    print("\n[SUCCESS] Initialization complete!")
    print("\nNext steps:")
    print("  1. Run: django-context scan-all")
    print("  2. Run: django-context build-all")
    print("  3. Your AI assistant can now read .app_memory/claude_aggregated_context.json")


def cmd_scan(args):
    """Scan a specific app"""
    project_root = get_project_root()
    config = Config(project_root)
    scanner = ProjectScanner(project_root, config)
    builder = ContextBuilder(project_root, config)

    app_name = args.app

    if getattr(args, 'dry_run', False):
        print(f"[DRY RUN] Would scan app: {app_name}")
        # Show what would be scanned
        apps = scanner.discover_apps()
        target_app = next((app for app in apps if app['name'] == app_name), None)
        if target_app:
            print(f"  App path: {target_app['path']}")
            print(f"  Deep analysis: {config.deep_analysis}")
        else:
            print(f"[ERROR] App '{app_name}' not found")
            sys.exit(1)
        return

    print(f"Scanning app: {app_name}")

    try:
        snapshot = builder.create_snapshot(app_name, stage="start")
        print(f"[OK] Created snapshot with {len(snapshot['files'])} files")
        print(f"  Deep analysis: {snapshot.get('deep_analysis', False)}")
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)


def cmd_scan_all(args):
    """Scan all apps in project"""
    project_root = get_project_root()
    config = Config(project_root)
    scanner = ProjectScanner(project_root, config)
    builder = ContextBuilder(project_root, config)

    apps = scanner.discover_apps()

    if getattr(args, 'dry_run', False):
        print(f"[DRY RUN] Would scan {len(apps)} apps:")
        print()
        for app_info in apps:
            print(f"  - {app_info['name']}")
            print(f"    Path: {app_info['path']}")
        print(f"\nDeep analysis: {config.deep_analysis}")
        return

    print(f"Scanning {len(apps)} apps...")
    print()

    for app_info in apps:
        app_name = app_info['name']
        print(f"  Scanning {app_name}...", end=" ")
        try:
            snapshot = builder.create_snapshot(app_name, stage="start")
            print(f"[OK] ({len(snapshot['files'])} files)")
        except Exception as e:
            print(f"[ERROR] {e}")

    print("\n[SUCCESS] Scan complete!")


def cmd_build(args):
    """Build context for a specific app"""
    project_root = get_project_root()
    config = Config(project_root)
    builder = ContextBuilder(project_root, config)

    app_name = args.app
    print(f"Building context for: {app_name}")

    try:
        context = builder.build_app_context(app_name)
        summary = context.get("summary", {})

        print(f"[OK] Context built successfully")
        print(f"  Files: {context['file_count']}")
        print(f"  Models: {len(summary.get('models', []))}")
        print(f"  Views: {len(summary.get('views', []))}")
        print(f"  URL patterns: {len(summary.get('url_patterns', []))}")
    except Exception as e:
        print(f"[ERROR] {e}")
        sys.exit(1)


def cmd_build_all(args):
    """Build aggregated context for all apps"""
    project_root = get_project_root()
    config = Config(project_root)
    builder = ContextBuilder(project_root, config)

    print("Building aggregated context for all apps...")

    try:
        result = builder.build_aggregated_context()
        global_summary = result.get("global_summary", {})
        stats = global_summary.get("statistics", {})

        print(f"\n[SUCCESS] Aggregated context built successfully!")
        print(f"\nProject: {result['project']}")
        print(f"  Apps: {result['total_apps']}")
        print(f"  Files: {result['total_files']}")
        print(f"\nGlobal Statistics:")
        print(f"  Models: {stats.get('total_models', 0)}")
        print(f"  Views: {stats.get('total_views', 0)}")
        print(f"  URL patterns: {stats.get('total_url_patterns', 0)}")
        print(f"  Forms: {stats.get('total_forms', 0)}")
        print(f"  Classes: {stats.get('total_classes', 0)}")
        print(f"  Functions: {stats.get('total_functions', 0)}")

        print(f"\nContext saved to:")
        print(f"  {config.memory_dir / 'claude_aggregated_context.json'}")

    except Exception as e:
        print(f"[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


def cmd_status(args):
    """Show current context status"""
    project_root = get_project_root()
    config = Config(project_root)
    builder = ContextBuilder(project_root, config)

    status = builder.get_status()

    print(f"Project: {status['project']}")
    print(f"Memory directory: {status['memory_dir']}")
    print()

    if "message" in status:
        print(status["message"])
        return

    # Aggregated context status
    agg = status.get("aggregated", {})
    if agg.get("exists"):
        print("Aggregated Context:")
        print(f"  [OK] Generated at: {agg.get('generated_at')}")
        print(f"  [OK] Total apps: {agg.get('total_apps')}")
        print(f"  [OK] Total files: {agg.get('total_files')}")
    else:
        print("Aggregated Context: [NOT BUILT]")

    print()

    # Per-app status
    print(f"Apps ({len(status.get('apps', []))}):")
    for app in status.get("apps", []):
        snapshot_status = "[OK]" if app["snapshot"] else "[  ]"
        context_status = "[OK]" if app["context"] else "[  ]"
        print(f"  {app['name']}")
        print(f"    Snapshot: {snapshot_status}")
        print(f"    Context:  {context_status}")


def cmd_clean(args):
    """Clean generated context files"""
    project_root = get_project_root()
    config = Config(project_root)
    builder = ContextBuilder(project_root, config)

    if args.app:
        print(f"Cleaning context for: {args.app}")
        builder.clean_context(args.app)
    else:
        confirm = input("Clean all context files? (y/N): ")
        if confirm.lower() == 'y':
            builder.clean_context()
        else:
            print("Cancelled")


def cmd_validate(args):
    """Validate configuration and project setup"""
    project_root = get_project_root()

    print("Validating Django Context Memory setup...")
    print()

    # Check if Django project
    is_django = utils.validate_django_project(project_root)
    if is_django:
        print("[OK] Django project detected")
    else:
        print("[WARNING] Django project indicators not found (manage.py, settings.py, wsgi.py)")

    # Check configuration
    config = Config(project_root)
    if config.config_path.exists():
        print(f"[OK] Configuration file exists: {config.config_path}")
        try:
            config.validate()
            print("[OK] Configuration is valid")
        except ValueError as e:
            print(f"[ERROR] Configuration validation failed:")
            print(f"  {e}")
            sys.exit(1)
    else:
        print(f"[WARNING] No configuration file found at {config.config_path}")
        print("  Run 'django-context init' to create one")

    # Check memory directory
    if config.memory_dir.exists():
        print(f"[OK] Memory directory exists: {config.memory_dir}")
    else:
        print(f"[WARNING] Memory directory not found: {config.memory_dir}")

    # Discover apps
    scanner = ProjectScanner(project_root, config)
    apps = scanner.discover_apps()
    if apps:
        print(f"[OK] Found {len(apps)} Django apps:")
        for app in apps:
            print(f"  - {app['name']}")
    else:
        print("[WARNING] No Django apps discovered")

    print()
    print("[SUCCESS] Validation complete!")


def cmd_generate_docs(args):
    """Generate documentation without full initialization"""
    project_root = get_project_root()
    config = Config(project_root)

    print("Generating project documentation...")
    print()

    try:
        doc_gen = DocumentationGenerator(project_root, config)
        doc_gen.generate_all()

        print("[OK] Documentation generated:")
        print(f"  - {config.memory_dir / 'PROJECT_README.md'}")
        print(f"  - {config.memory_dir / 'CLAUDE_POLICY.md'}")
        print()
        print("[SUCCESS] Documentation generation complete!")

    except Exception as e:
        print(f"[ERROR] Failed to generate documentation: {e}")
        sys.exit(1)


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="Django Context Memory - Deep code intelligence for AI assistants",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  django-context init                  # Initialize in current project
  django-context scan infrastructure   # Scan single app
  django-context scan-all              # Scan all apps
  django-context build infrastructure  # Build context for app
  django-context build-all             # Build aggregated context
  django-context status                # Show status
  django-context clean                 # Clean all context files
  django-context validate              # Validate setup
  django-context generate-docs         # Generate documentation
        """
    )

    # Global flags
    parser.add_argument('--version', action='version', version=f'django-context-memory {__version__}')
    parser.add_argument('--verbose', '-v', action='store_true', help='Enable verbose output')
    parser.add_argument('--config', type=str, help='Path to configuration file')

    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # Init command
    parser_init = subparsers.add_parser('init', help='Initialize context memory in project')
    parser_init.set_defaults(func=cmd_init)

    # Scan command
    parser_scan = subparsers.add_parser('scan', help='Scan a specific app')
    parser_scan.add_argument('app', help='App name to scan')
    parser_scan.add_argument('--dry-run', action='store_true', help='Show what would be scanned without scanning')
    parser_scan.set_defaults(func=cmd_scan)

    # Scan-all command
    parser_scan_all = subparsers.add_parser('scan-all', help='Scan all apps')
    parser_scan_all.add_argument('--dry-run', action='store_true', help='Show what would be scanned without scanning')
    parser_scan_all.set_defaults(func=cmd_scan_all)

    # Build command
    parser_build = subparsers.add_parser('build', help='Build context for a specific app')
    parser_build.add_argument('app', help='App name to build context for')
    parser_build.set_defaults(func=cmd_build)

    # Build-all command
    parser_build_all = subparsers.add_parser('build-all', help='Build aggregated context')
    parser_build_all.set_defaults(func=cmd_build_all)

    # Status command
    parser_status = subparsers.add_parser('status', help='Show context status')
    parser_status.set_defaults(func=cmd_status)

    # Clean command
    parser_clean = subparsers.add_parser('clean', help='Clean generated context files')
    parser_clean.add_argument('--app', help='Specific app to clean (cleans all if omitted)')
    parser_clean.set_defaults(func=cmd_clean)

    # Validate command
    parser_validate = subparsers.add_parser('validate', help='Validate configuration and project setup')
    parser_validate.set_defaults(func=cmd_validate)

    # Generate-docs command
    parser_generate_docs = subparsers.add_parser('generate-docs', help='Generate documentation')
    parser_generate_docs.set_defaults(func=cmd_generate_docs)

    # Parse arguments
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Setup verbose logging if requested
    if hasattr(args, 'verbose') and args.verbose:
        utils.setup_logging(verbose=True)

    # Execute command
    args.func(args)


if __name__ == "__main__":
    main()
