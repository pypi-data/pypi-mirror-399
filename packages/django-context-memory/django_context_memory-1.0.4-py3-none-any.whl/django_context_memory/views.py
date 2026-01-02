"""
Django views for Context Memory web interface

This module provides a web UI for the django_context_memory library.
When the library is added to INSTALLED_APPS, these views provide a dashboard
for visualizing and managing context memory.
"""

import json
from pathlib import Path
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from .config import Config
from .scanner import ProjectScanner
from .builder import ContextBuilder


def index(request):
    """Render the main context memory dashboard"""
    # Get project root from Django settings
    from django.conf import settings
    project_root = Path(settings.BASE_DIR)

    # Initialize library components
    config = Config(project_root)
    scanner = ProjectScanner(project_root, config)

    apps = scanner.discover_apps()

    # Load aggregated context if it exists
    aggregated_file = config.memory_dir / "claude_aggregated_context.json"
    aggregated_data = None
    if aggregated_file.exists():
        try:
            aggregated_data = json.loads(aggregated_file.read_text(encoding='utf-8'))
        except Exception:
            pass  # Use default None

    context = {
        'project_name': config.project_name,
        'apps': apps,
        'aggregated': aggregated_data,
    }
    return render(request, 'django_context_memory/index.html', context)


@require_http_methods(["POST"])
def action_start(request):
    """Handle START action - create initial snapshot"""
    try:
        from django.conf import settings
        project_root = Path(settings.BASE_DIR)
        config = Config(project_root)
        builder = ContextBuilder(project_root, config)

        data = json.loads(request.body)
        app_name = data.get('app')

        if not app_name:
            return JsonResponse({
                'status': 'error',
                'message': 'App name is required'
            }, status=400)

        # Use library method
        snapshot = builder.create_snapshot(app_name, stage='start')

        return JsonResponse({
            'status': 'success',
            'message': f'START snapshot created for {app_name}',
            'timestamp': snapshot['timestamp'],
            'file_count': len(snapshot['files'])
        })
    except FileNotFoundError as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Failed to create snapshot: {str(e)}'
        }, status=500)


@require_http_methods(["POST"])
def action_end(request):
    """Handle END action - create final snapshot"""
    try:
        from django.conf import settings
        project_root = Path(settings.BASE_DIR)
        config = Config(project_root)
        builder = ContextBuilder(project_root, config)

        data = json.loads(request.body)
        app_name = data.get('app')

        if not app_name:
            return JsonResponse({
                'status': 'error',
                'message': 'App name is required'
            }, status=400)

        # Use library method
        snapshot = builder.create_snapshot(app_name, stage='end')

        return JsonResponse({
            'status': 'success',
            'message': f'END snapshot created for {app_name}',
            'timestamp': snapshot['timestamp'],
            'file_count': len(snapshot['files'])
        })
    except FileNotFoundError as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=404)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Failed to create snapshot: {str(e)}'
        }, status=500)


@require_http_methods(["POST"])
def action_build(request):
    """Handle BUILD CONTEXT action"""
    try:
        from django.conf import settings
        project_root = Path(settings.BASE_DIR)
        config = Config(project_root)
        builder = ContextBuilder(project_root, config)

        data = json.loads(request.body)
        app_name = data.get('app')

        if not app_name:
            return JsonResponse({
                'status': 'error',
                'message': 'App name is required'
            }, status=400)

        # Use library method
        payload = builder.build_app_context(app_name)

        return JsonResponse({
            'status': 'success',
            'message': f'Context built for {app_name} - {payload["file_count"]} files processed',
            'timestamp': payload["generated_at"],
            'file_count': payload["file_count"],
            'app': app_name,
            'stage': payload.get("stage", "unknown"),
            'summary': payload.get("summary", {})
        })
    except FileNotFoundError as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=404)
    except ValueError as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Build failed: {str(e)}'
        }, status=500)


@require_http_methods(["POST"])
def action_build_all(request):
    """Handle BUILD ALL APPS action"""
    try:
        from django.conf import settings
        project_root = Path(settings.BASE_DIR)
        config = Config(project_root)
        builder = ContextBuilder(project_root, config)

        # Use library method
        aggregated_payload = builder.build_aggregated_context()

        return JsonResponse({
            'status': 'success',
            'message': f'Built context for ALL apps: {aggregated_payload["total_apps"]} apps, {aggregated_payload["total_files"]} files',
            'timestamp': aggregated_payload["generated_at"],
            'total_apps': aggregated_payload["total_apps"],
            'total_files': aggregated_payload["total_files"],
            'apps_included': aggregated_payload["apps_included"],
            'global_summary': aggregated_payload.get("global_summary", {})
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Build all failed: {str(e)}'
        }, status=500)


@require_http_methods(["GET"])
def get_status(request):
    """Get current status and memory info"""
    try:
        from django.conf import settings
        project_root = Path(settings.BASE_DIR)
        config = Config(project_root)

        app_name = request.GET.get('app')

        if not app_name:
            return JsonResponse({
                'status': 'error',
                'message': 'App name is required'
            }, status=400)

        # Get status from library
        memory_dir = config.memory_dir / app_name
        snapshot_file = memory_dir / "snapshot.json"
        app_memory_file = memory_dir / "app_memory.json"

        app_status = {
            'app': app_name,
            'has_snapshot': snapshot_file.exists(),
            'has_memory': app_memory_file.exists(),
            'memory_dir': str(memory_dir)
        }

        # Load snapshot info if exists
        if snapshot_file.exists():
            try:
                with open(snapshot_file, 'r', encoding='utf-8') as f:
                    snap = json.load(f)
                app_status['snapshot_timestamp'] = snap.get('timestamp')
                app_status['snapshot_stage'] = snap.get('stage')
                app_status['file_count'] = len(snap.get('files', []))
            except Exception:
                pass

        # Check for aggregated context
        aggregated_file = config.memory_dir / "claude_aggregated_context.json"
        aggregated = {
            'exists': aggregated_file.exists(),
            'path': str(aggregated_file)
        }

        if aggregated_file.exists():
            try:
                with open(aggregated_file, 'r', encoding='utf-8') as f:
                    agg_data = json.load(f)
                payload = agg_data.get('payload', {})
                aggregated['timestamp'] = payload.get('generated_at')
                aggregated['total_apps'] = payload.get('total_apps')
                aggregated['total_files'] = payload.get('total_files')
            except Exception:
                pass

        return JsonResponse({
            'status': 'success',
            'app_status': app_status,
            'aggregated': aggregated,
            'memory_dir': str(config.memory_dir)
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)
