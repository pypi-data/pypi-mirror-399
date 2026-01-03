#!/usr/bin/env python
"""
scope-run: No-code instrumentation CLI for Scope Analytics

Usage:
    scope-run python app.py
    scope-run uvicorn main:app --reload
    scope-run gunicorn app:app -w 4
    scope-run flask run --port 5000
    scope-run celery -A tasks worker

This CLI wrapper automatically instruments your Python application
with Scope Analytics tracking - no code changes required.

Environment Variables:
    SCOPE_API_KEY: Required. Your Scope Analytics API key
    SCOPE_ENDPOINT: Optional. Custom API endpoint
    SCOPE_DEBUG: Optional. Set to 'true' for debug logging
    SCOPE_ENVIRONMENT: Optional. Environment name (default: production)
"""

import os
import sys
import subprocess
import argparse
import tempfile
import atexit
from typing import List, Optional

# Track temp files for cleanup
_temp_files: List[str] = []


def _cleanup_temp_files():
    """Clean up temporary bootstrap files on exit"""
    for path in _temp_files:
        try:
            os.unlink(path)
        except (OSError, FileNotFoundError):
            pass


atexit.register(_cleanup_temp_files)


def _create_bootstrap_file() -> str:
    """
    Create a temporary bootstrap file that imports scope_analytics.auto

    This file is used for PYTHONSTARTUP to ensure instrumentation
    happens before the user's code runs.
    """
    bootstrap_code = '''# Scope Analytics Auto-Bootstrap
import os
if os.environ.get('SCOPE_AUTO_INSTRUMENT') == 'true':
    try:
        import scope_analytics.auto
    except Exception as e:
        import sys
        print(f"[Scope SDK] Warning: Auto-instrumentation failed: {e}", file=sys.stderr)
'''

    fd, path = tempfile.mkstemp(suffix='.py', prefix='scope_bootstrap_')
    with os.fdopen(fd, 'w') as f:
        f.write(bootstrap_code)

    _temp_files.append(path)
    return path


def _create_sitecustomize_dir() -> str:
    """
    Create a temporary directory with sitecustomize.py for auto-instrumentation.

    sitecustomize.py is automatically imported by Python at startup,
    making it ideal for pre-application instrumentation.
    """
    import tempfile

    # Create temp directory
    temp_dir = tempfile.mkdtemp(prefix='scope_site_')
    _temp_files.append(temp_dir)

    # Create sitecustomize.py
    sitecustomize_path = os.path.join(temp_dir, 'sitecustomize.py')
    sitecustomize_code = '''# Scope Analytics Sitecustomize
import os
if os.environ.get('SCOPE_AUTO_INSTRUMENT') == 'true':
    try:
        import scope_analytics.auto
    except ImportError:
        pass  # scope-analytics not installed, skip silently
    except Exception as e:
        import sys
        print(f"[Scope SDK] Warning: Auto-instrumentation failed: {e}", file=sys.stderr)
'''

    with open(sitecustomize_path, 'w') as f:
        f.write(sitecustomize_code)

    return temp_dir


def _get_version() -> str:
    """Get the SDK version"""
    try:
        from scope_analytics import __version__
        return __version__
    except ImportError:
        return "unknown"


def main(argv: Optional[List[str]] = None) -> int:
    """
    Main entry point for scope-run CLI

    Args:
        argv: Command line arguments (defaults to sys.argv[1:])

    Returns:
        Exit code from the wrapped command
    """
    parser = argparse.ArgumentParser(
        prog='scope-run',
        description='Run Python application with Scope Analytics auto-instrumentation',
        epilog='''
Examples:
  scope-run python app.py              # Run a Python script
  scope-run uvicorn main:app --reload  # Run uvicorn server
  scope-run gunicorn app:app -w 4      # Run gunicorn server
  scope-run flask run --port 5000      # Run Flask dev server
  scope-run python -m mypackage        # Run a module

Environment Variables:
  SCOPE_API_KEY      Your Scope Analytics API key (required)
  SCOPE_ENDPOINT     Custom API endpoint (optional)
  SCOPE_DEBUG        Set to 'true' for debug logging
  SCOPE_ENVIRONMENT  Environment name (default: production)
''',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument(
        '--version', '-v',
        action='store_true',
        help='Show version and exit'
    )

    parser.add_argument(
        '--debug', '-d',
        action='store_true',
        help='Enable debug logging'
    )

    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be executed without running'
    )

    parser.add_argument(
        'command',
        nargs=argparse.REMAINDER,
        help='Command to run (e.g., python app.py, uvicorn main:app)'
    )

    args = parser.parse_args(argv)

    # Handle --version
    if args.version:
        print(f"scope-analytics {_get_version()}")
        return 0

    # Require a command
    if not args.command:
        parser.print_help()
        print("\nError: No command specified. Usage: scope-run python app.py", file=sys.stderr)
        return 1

    # Check for API key
    api_key = os.environ.get('SCOPE_API_KEY')
    if not api_key:
        print("[Scope SDK] Warning: SCOPE_API_KEY not set. Instrumentation will be disabled.", file=sys.stderr)
        print("[Scope SDK] Set your API key: export SCOPE_API_KEY='sk_live_...'", file=sys.stderr)

    # Set up environment for auto-instrumentation
    env = os.environ.copy()
    env['SCOPE_AUTO_INSTRUMENT'] = 'true'

    if args.debug:
        env['SCOPE_DEBUG'] = 'true'

    # Determine the best injection strategy based on the command
    command = args.command
    executable = command[0] if command else ''

    # Use sitecustomize approach - works with all Python programs
    site_dir = _create_sitecustomize_dir()

    # Prepend to PYTHONPATH so sitecustomize.py is found
    existing_path = env.get('PYTHONPATH', '')
    if existing_path:
        env['PYTHONPATH'] = f"{site_dir}{os.pathsep}{existing_path}"
    else:
        env['PYTHONPATH'] = site_dir

    # Build the final command
    final_command = command

    if args.dry_run:
        print("[Scope SDK] Dry run - would execute:")
        print(f"  SCOPE_AUTO_INSTRUMENT=true")
        print(f"  PYTHONPATH={env['PYTHONPATH']}")
        if args.debug:
            print(f"  SCOPE_DEBUG=true")
        print(f"  {' '.join(final_command)}")
        return 0

    # Print startup message if debug enabled
    if args.debug or env.get('SCOPE_DEBUG', '').lower() == 'true':
        print(f"[Scope SDK] Starting with auto-instrumentation...")
        print(f"[Scope SDK] Command: {' '.join(final_command)}")

    # Execute the wrapped command
    try:
        result = subprocess.run(final_command, env=env)
        return result.returncode
    except FileNotFoundError:
        print(f"[Scope SDK] Error: Command not found: {executable}", file=sys.stderr)
        return 127
    except KeyboardInterrupt:
        print("\n[Scope SDK] Interrupted")
        return 130
    except Exception as e:
        print(f"[Scope SDK] Error executing command: {e}", file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
