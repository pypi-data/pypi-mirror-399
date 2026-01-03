"""
Auto-instrumentation module for Scope Analytics

Import this module to automatically initialize Scope Analytics
with configuration from environment variables.

Usage:
    import scope_analytics.auto  # That's it!

Or via CLI:
    scope-run python app.py

Environment Variables:
    SCOPE_API_KEY: Required. Your Scope Analytics API key
    SCOPE_ENDPOINT: Optional. Custom API endpoint
    SCOPE_DEBUG: Optional. Set to 'true' for debug logging
    SCOPE_ENVIRONMENT: Optional. Environment name (default: production)
"""

import os
import sys
import warnings
import atexit

# Only initialize once
_initialized = False
_scope_instance = None


def _log(message: str) -> None:
    """Log a message if debug mode is enabled"""
    if os.environ.get('SCOPE_DEBUG', '').lower() == 'true':
        print(f"[Scope SDK] {message}", file=sys.stderr)


def _auto_init():
    """
    Automatically initialize Scope Analytics from environment variables.

    This function:
    1. Reads configuration from environment variables
    2. Initializes ScopeAnalytics with auto-patching enabled
    3. Sets up auto-middleware injection for known frameworks
    """
    global _initialized, _scope_instance

    if _initialized:
        return _scope_instance

    _initialized = True  # Set early to prevent re-entry

    api_key = os.environ.get('SCOPE_API_KEY')

    if not api_key:
        # No API key - skip initialization with a warning
        warnings.warn(
            "SCOPE_API_KEY not set - Scope Analytics disabled. "
            "Set SCOPE_API_KEY environment variable to enable tracking.",
            UserWarning,
            stacklevel=2
        )
        _log("No API key found - instrumentation disabled")
        return None

    try:
        from scope_analytics import ScopeAnalytics

        _log("Initializing Scope Analytics...")

        _scope_instance = ScopeAnalytics(
            api_key=api_key,
            endpoint=os.environ.get('SCOPE_ENDPOINT'),
            debug=os.environ.get('SCOPE_DEBUG', '').lower() == 'true',
            environment=os.environ.get('SCOPE_ENVIRONMENT', 'production'),
            auto_patch=True,  # Always auto-patch in auto mode
        )

        _log("Scope Analytics initialized successfully")

        # Auto-inject session middleware for known frameworks
        _auto_inject_middleware()

        return _scope_instance

    except ValueError as e:
        # Invalid API key format or missing required config
        warnings.warn(
            f"Scope Analytics initialization failed: {e}",
            UserWarning,
            stacklevel=2
        )
        _log(f"Initialization failed: {e}")
        return None

    except Exception as e:
        # Unexpected error - don't crash the user's app
        warnings.warn(
            f"Scope Analytics initialization failed unexpectedly: {e}",
            UserWarning,
            stacklevel=2
        )
        _log(f"Unexpected error during initialization: {e}")
        return None


def _auto_inject_middleware():
    """
    Automatically inject session middleware for known frameworks.
    This happens at RUNTIME - no user code changes required.

    Supports: FastAPI/Starlette, Flask, Django

    The middleware extracts X-Scope-Session-ID headers and makes
    session correlation work automatically between frontend and backend.
    """
    _log("Setting up auto-middleware injection...")

    injected = False

    # Try FastAPI/Starlette
    if _try_inject_fastapi():
        _log("Prepared session middleware injection for FastAPI/Starlette")
        injected = True

    # Try Flask
    if _try_inject_flask():
        _log("Prepared session hooks injection for Flask")
        injected = True

    # Try Django
    if _try_inject_django():
        _log("Prepared session middleware injection for Django")
        injected = True

    if not injected:
        _log(
            "No known framework detected - session middleware not auto-injected. "
            "LLM tracking still works. For session correlation with custom frameworks, "
            "see docs on manual ScopeContext.set_session_id()"
        )


def _try_inject_fastapi() -> bool:
    """
    Inject session middleware into FastAPI/Starlette apps at runtime.

    We patch the __init__ method of FastAPI and Starlette classes
    so that when the user creates an app, our middleware is automatically added.
    """
    patched = False

    # Try patching Starlette first (FastAPI extends it)
    try:
        from starlette.applications import Starlette

        if not hasattr(Starlette.__init__, '_scope_patched'):
            original_starlette_init = Starlette.__init__

            def patched_starlette_init(self, *args, **kwargs):
                original_starlette_init(self, *args, **kwargs)
                # Add our middleware after app is initialized
                try:
                    from scope_analytics.middleware import ScopeSessionMiddleware
                    self.add_middleware(ScopeSessionMiddleware)
                    _log(f"Auto-injected ScopeSessionMiddleware into Starlette app")
                except Exception as e:
                    _log(f"Failed to inject middleware into Starlette: {e}")

            patched_starlette_init._scope_patched = True
            Starlette.__init__ = patched_starlette_init
            patched = True
            _log("Patched Starlette.__init__ for auto-middleware injection")

    except ImportError:
        pass

    # Also patch FastAPI specifically (more common)
    try:
        from fastapi import FastAPI

        if not hasattr(FastAPI.__init__, '_scope_patched'):
            original_fastapi_init = FastAPI.__init__

            def patched_fastapi_init(self, *args, **kwargs):
                original_fastapi_init(self, *args, **kwargs)
                # Add our middleware after app is initialized
                try:
                    from scope_analytics.middleware import ScopeSessionMiddleware
                    # Check if middleware already added (from Starlette patch)
                    has_scope_middleware = any(
                        getattr(m, 'cls', None) == ScopeSessionMiddleware
                        for m in getattr(self, 'user_middleware', [])
                    )
                    if not has_scope_middleware:
                        self.add_middleware(ScopeSessionMiddleware)
                        _log(f"Auto-injected ScopeSessionMiddleware into FastAPI app")
                except Exception as e:
                    _log(f"Failed to inject middleware into FastAPI: {e}")

            patched_fastapi_init._scope_patched = True
            FastAPI.__init__ = patched_fastapi_init
            patched = True
            _log("Patched FastAPI.__init__ for auto-middleware injection")

    except ImportError:
        pass

    return patched


def _try_inject_flask() -> bool:
    """
    Inject session hooks into Flask apps at runtime.

    We patch Flask's __init__ to register before/after request hooks
    that handle session ID extraction.
    """
    try:
        from flask import Flask

        if hasattr(Flask.__init__, '_scope_patched'):
            return True

        original_flask_init = Flask.__init__

        def patched_flask_init(self, *args, **kwargs):
            original_flask_init(self, *args, **kwargs)
            # Register session tracking hooks after app is created
            try:
                from scope_analytics.middleware import init_flask_session_tracking
                init_flask_session_tracking(self)
                _log(f"Auto-injected session hooks into Flask app")
            except Exception as e:
                _log(f"Failed to inject session hooks into Flask: {e}")

        patched_flask_init._scope_patched = True
        Flask.__init__ = patched_flask_init
        _log("Patched Flask.__init__ for auto-middleware injection")
        return True

    except ImportError:
        return False


def _try_inject_django() -> bool:
    """
    Inject session middleware into Django apps at runtime.

    Django is trickier - middleware is configured in settings.py.
    We hook into Django's setup to add our middleware.
    """
    try:
        import django
        from django.conf import settings

        # Check if Django is configured
        if not settings.configured:
            # Django not configured yet - set up a hook for when it is
            _log("Django detected but not configured - deferring middleware injection")

            # We can hook into django.setup() to add middleware when called
            if not hasattr(django.setup, '_scope_patched'):
                original_setup = django.setup

                def patched_setup(*args, **kwargs):
                    result = original_setup(*args, **kwargs)
                    _inject_django_middleware()
                    return result

                patched_setup._scope_patched = True
                django.setup = patched_setup
                _log("Patched django.setup() for deferred middleware injection")

            return True

        # Django is already configured - inject middleware now
        return _inject_django_middleware()

    except ImportError:
        return False
    except Exception as e:
        _log(f"Error setting up Django middleware injection: {e}")
        return False


def _inject_django_middleware() -> bool:
    """
    Actually inject the middleware into Django's MIDDLEWARE setting.
    """
    try:
        from django.conf import settings

        if not settings.configured:
            return False

        middleware_class = 'scope_analytics.middleware.DjangoScopeMiddleware'

        if hasattr(settings, 'MIDDLEWARE'):
            middleware_list = list(settings.MIDDLEWARE)
            if middleware_class not in middleware_list:
                # Insert at the beginning for earliest access to request
                middleware_list.insert(0, middleware_class)
                settings.MIDDLEWARE = middleware_list
                _log(f"Auto-injected {middleware_class} into Django MIDDLEWARE")
            return True

        return False

    except Exception as e:
        _log(f"Failed to inject Django middleware: {e}")
        return False


def get_instance():
    """
    Get the auto-initialized ScopeAnalytics instance.

    Returns:
        ScopeAnalytics instance or None if not initialized
    """
    return _scope_instance


def is_initialized() -> bool:
    """
    Check if auto-instrumentation has been initialized.

    Returns:
        True if initialized, False otherwise
    """
    return _initialized and _scope_instance is not None


# Auto-initialize on import
_auto_init()
