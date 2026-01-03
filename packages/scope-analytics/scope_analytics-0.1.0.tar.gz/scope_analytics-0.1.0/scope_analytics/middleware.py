"""
HTTP Middleware for Scope Analytics SDK

Automatically extracts session ID from X-Scope-Session-ID header
and sets it in the context for all LLM calls to be linked.

Also tracks ALL incoming HTTP requests to enable analysis of
API call patterns (e.g., "what did users do before cancelling?").

Auto-JWT Extraction (Identity Stitching):
- Automatically extracts user_id from JWT tokens in Authorization header
- Enables identity stitching WITHOUT any user code changes
- Works with standard JWT claims: sub, user_id, uid, id
- Manual ScopeContext.set_user_id() takes priority if set

Supports:
- FastAPI (ASGI middleware)
- Flask (WSGI middleware)
- Django middleware
- Generic ASGI/WSGI applications
"""

import logging
import time
import base64
import json
from typing import Optional, Callable, Any
from .context import ScopeContext

logger = logging.getLogger("scope_analytics.middleware")


def _get_sdk():
    """
    Get the global SDK instance for HTTP request tracking.
    Imported lazily to avoid circular imports.
    """
    try:
        from . import get_sdk_instance
        return get_sdk_instance()
    except ImportError:
        return None


def _track_http_request(
    method: str,
    path: str,
    status_code: int,
    latency_ms: float,
    query_params: Optional[dict] = None,
    client_ip: Optional[str] = None,
    user_agent: Optional[str] = None,
    content_type: Optional[str] = None,
    content_length: Optional[int] = None,
):
    """
    Track an HTTP request event via the global SDK instance.
    """
    sdk = _get_sdk()
    if sdk is None:
        return

    try:
        event = sdk.event_formatter.format_http_request(
            method=method,
            path=path,
            status_code=status_code,
            latency_ms=latency_ms,
            query_params=query_params,
            client_ip=client_ip,
            user_agent=user_agent,
            content_type=content_type,
            content_length=content_length,
        )
        sdk.queue.enqueue(event)
        sdk.config.log(f"Captured HTTP request: {method} {path} -> {status_code}")
    except Exception as e:
        logger.warning(f"Failed to track HTTP request: {e}")

# Header name for session ID (case-insensitive in HTTP)
SESSION_HEADER = "X-Scope-Session-ID"
SESSION_HEADER_LOWER = "x-scope-session-id"

# Standard JWT claims that may contain user ID
JWT_USER_ID_CLAIMS = ["sub", "user_id", "uid", "id", "userId", "user"]


def _extract_user_id_from_jwt(auth_header: Optional[str]) -> Optional[str]:
    """
    Extract user_id from JWT token in Authorization header.

    This enables automatic identity stitching without any user code changes.
    Works with standard JWT claims: sub, user_id, uid, id, userId, user

    Args:
        auth_header: Authorization header value (e.g., "Bearer eyJhbG...")

    Returns:
        User ID if found in JWT, None otherwise
    """
    if not auth_header:
        return None

    # Check for Bearer token
    if not auth_header.startswith("Bearer "):
        return None

    token = auth_header[7:]  # Remove "Bearer " prefix

    try:
        # JWT format: header.payload.signature
        parts = token.split(".")
        if len(parts) != 3:
            return None

        # Decode payload (middle part)
        # Add padding if needed (JWT base64url doesn't include padding)
        payload_b64 = parts[1]
        padding = 4 - len(payload_b64) % 4
        if padding != 4:
            payload_b64 += "=" * padding

        # Use base64url decoding (replace - with + and _ with /)
        payload_b64 = payload_b64.replace("-", "+").replace("_", "/")
        payload_bytes = base64.b64decode(payload_b64)
        payload = json.loads(payload_bytes.decode("utf-8"))

        # Look for user ID in standard claims
        for claim in JWT_USER_ID_CLAIMS:
            if claim in payload:
                user_id = payload[claim]
                # Convert to string if needed
                if user_id is not None:
                    return str(user_id)

        return None

    except Exception as e:
        # Not a valid JWT or couldn't decode - silently skip
        # This is expected for non-JWT auth or malformed tokens
        logger.debug(f"Could not extract user_id from JWT: {e}")
        return None


def _auto_set_user_id_from_headers(headers: dict) -> None:
    """
    Automatically extract and set user_id from JWT in headers.

    Only sets user_id if:
    1. User hasn't manually set it via ScopeContext.set_user_id()
    2. Authorization header contains a valid JWT with user ID claim

    Args:
        headers: Dictionary of HTTP headers (case-insensitive keys)
    """
    # Skip if user_id already set manually
    if ScopeContext.get_user_id() is not None:
        return

    # Try to find Authorization header (case-insensitive)
    auth_header = None
    for key, value in headers.items():
        if key.lower() == "authorization":
            auth_header = value
            break

    if auth_header:
        user_id = _extract_user_id_from_jwt(auth_header)
        if user_id:
            ScopeContext.set_user_id(user_id)
            logger.debug(f"Auto-extracted user_id from JWT: {user_id}")


def extract_session_from_headers(headers: dict) -> Optional[str]:
    """
    Extract session ID from HTTP headers (case-insensitive)

    Args:
        headers: Dictionary of HTTP headers

    Returns:
        Session ID if found, None otherwise
    """
    # Try exact case first
    session_id = headers.get(SESSION_HEADER)
    if session_id:
        return session_id

    # Try lowercase
    session_id = headers.get(SESSION_HEADER_LOWER)
    if session_id:
        return session_id

    # Try case-insensitive search
    for key, value in headers.items():
        if key.lower() == SESSION_HEADER_LOWER:
            return value

    return None


# =============================================================================
# FastAPI / Starlette Middleware (ASGI)
# =============================================================================

class ScopeSessionMiddleware:
    """
    ASGI Middleware for FastAPI/Starlette applications

    Extracts X-Scope-Session-ID header and sets it in ScopeContext
    for the duration of the request.

    Usage:
        from fastapi import FastAPI
        from scope_analytics.middleware import ScopeSessionMiddleware

        app = FastAPI()
        app.add_middleware(ScopeSessionMiddleware)

        # Or with options:
        app.add_middleware(
            ScopeSessionMiddleware,
            generate_temp_session=True,  # Generate temp session if no header
            log_missing_session=True,    # Log warning when no session header
        )
    """

    def __init__(
        self,
        app,
        generate_temp_session: bool = True,
        log_missing_session: bool = False,
    ):
        """
        Initialize middleware

        Args:
            app: ASGI application
            generate_temp_session: Generate temp session ID if header missing (default: True)
            log_missing_session: Log warning when no session header (default: False)
        """
        self.app = app
        self.generate_temp_session = generate_temp_session
        self.log_missing_session = log_missing_session

    async def __call__(self, scope, receive, send):
        if scope["type"] != "http":
            # Pass through non-HTTP requests (websocket, lifespan, etc.)
            await self.app(scope, receive, send)
            return

        # Start timing
        start_time = time.time()

        # Extract headers from ASGI scope
        headers = {}
        for key, value in scope.get("headers", []):
            # ASGI headers are bytes
            headers[key.decode("latin-1")] = value.decode("latin-1")

        # Extract session ID from headers
        session_id = extract_session_from_headers(headers)

        if session_id:
            ScopeContext.set_session_id(session_id)
        elif self.generate_temp_session:
            # Generate temporary session for backend-only requests
            session_id = ScopeContext.generate_temp_session_id()
            ScopeContext.set_session_id(session_id)
            if self.log_missing_session:
                logger.debug(f"No X-Scope-Session-ID header, generated temp: {session_id}")
        elif self.log_missing_session:
            logger.warning("No X-Scope-Session-ID header and temp generation disabled")

        # Auto-extract user_id from JWT (for identity stitching)
        _auto_set_user_id_from_headers(headers)

        # Extract request details for tracking
        method = scope.get("method", "GET")
        path = scope.get("path", "/")
        query_string = scope.get("query_string", b"").decode("utf-8", errors="ignore")
        query_params = dict(pair.split("=", 1) for pair in query_string.split("&") if "=" in pair) if query_string else {}

        # Extract useful headers
        client_ip = None
        if scope.get("client"):
            client_ip = scope["client"][0]
        user_agent = headers.get("user-agent")
        content_type = headers.get("content-type")
        content_length = None
        if headers.get("content-length"):
            try:
                content_length = int(headers["content-length"])
            except ValueError:
                pass

        # Capture response status code
        response_status = [200]  # Default, will be updated by send wrapper

        original_send = send

        async def send_wrapper(message):
            if message["type"] == "http.response.start":
                response_status[0] = message.get("status", 200)
            await original_send(message)

        try:
            await self.app(scope, receive, send_wrapper)
        finally:
            # Calculate latency
            latency_ms = (time.time() - start_time) * 1000

            # Track HTTP request
            _track_http_request(
                method=method,
                path=path,
                status_code=response_status[0],
                latency_ms=latency_ms,
                query_params=query_params,
                client_ip=client_ip,
                user_agent=user_agent,
                content_type=content_type,
                content_length=content_length,
            )

            # Always clear context after request to prevent leaks
            ScopeContext.clear()


# =============================================================================
# Flask Middleware (WSGI)
# =============================================================================

class FlaskScopeMiddleware:
    """
    WSGI Middleware for Flask applications

    Extracts X-Scope-Session-ID header and sets it in ScopeContext
    for the duration of the request.

    Usage:
        from flask import Flask
        from scope_analytics.middleware import FlaskScopeMiddleware

        app = Flask(__name__)
        app.wsgi_app = FlaskScopeMiddleware(app.wsgi_app)

        # Or with options:
        app.wsgi_app = FlaskScopeMiddleware(
            app.wsgi_app,
            generate_temp_session=True,
            log_missing_session=True,
        )
    """

    def __init__(
        self,
        app,
        generate_temp_session: bool = True,
        log_missing_session: bool = False,
    ):
        """
        Initialize middleware

        Args:
            app: WSGI application
            generate_temp_session: Generate temp session ID if header missing (default: True)
            log_missing_session: Log warning when no session header (default: False)
        """
        self.app = app
        self.generate_temp_session = generate_temp_session
        self.log_missing_session = log_missing_session

    def __call__(self, environ, start_response):
        # Start timing
        start_time = time.time()

        # Extract headers from WSGI environ
        # WSGI headers are in format HTTP_X_SCOPE_SESSION_ID
        headers = {}
        for key, value in environ.items():
            if key.startswith("HTTP_"):
                # Convert HTTP_X_SCOPE_SESSION_ID to X-Scope-Session-Id
                header_name = key[5:].replace("_", "-").title()
                headers[header_name] = value

        # Also check for direct header (some servers)
        if SESSION_HEADER in environ:
            headers[SESSION_HEADER] = environ[SESSION_HEADER]

        # Extract session ID from headers
        session_id = extract_session_from_headers(headers)

        if session_id:
            ScopeContext.set_session_id(session_id)
        elif self.generate_temp_session:
            session_id = ScopeContext.generate_temp_session_id()
            ScopeContext.set_session_id(session_id)
            if self.log_missing_session:
                logger.debug(f"No X-Scope-Session-ID header, generated temp: {session_id}")
        elif self.log_missing_session:
            logger.warning("No X-Scope-Session-ID header and temp generation disabled")

        # Auto-extract user_id from JWT (for identity stitching)
        _auto_set_user_id_from_headers(headers)

        # Extract request details for tracking
        method = environ.get("REQUEST_METHOD", "GET")
        path = environ.get("PATH_INFO", "/")
        query_string = environ.get("QUERY_STRING", "")
        query_params = dict(pair.split("=", 1) for pair in query_string.split("&") if "=" in pair) if query_string else {}

        # Extract useful headers
        client_ip = environ.get("REMOTE_ADDR")
        user_agent = environ.get("HTTP_USER_AGENT")
        content_type = environ.get("CONTENT_TYPE")
        content_length = None
        if environ.get("CONTENT_LENGTH"):
            try:
                content_length = int(environ["CONTENT_LENGTH"])
            except ValueError:
                pass

        # Capture response status code
        response_status = [200]

        def start_response_wrapper(status, response_headers, exc_info=None):
            # Parse status code from "200 OK" format
            try:
                response_status[0] = int(status.split()[0])
            except (ValueError, IndexError):
                pass
            return start_response(status, response_headers, exc_info)

        try:
            return self.app(environ, start_response_wrapper)
        finally:
            # Calculate latency
            latency_ms = (time.time() - start_time) * 1000

            # Track HTTP request
            _track_http_request(
                method=method,
                path=path,
                status_code=response_status[0],
                latency_ms=latency_ms,
                query_params=query_params,
                client_ip=client_ip,
                user_agent=user_agent,
                content_type=content_type,
                content_length=content_length,
            )

            # Always clear context after request to prevent leaks
            ScopeContext.clear()


# =============================================================================
# Flask Blueprint/Before Request Hook (Alternative)
# =============================================================================

def init_flask_session_tracking(app, generate_temp_session: bool = True):
    """
    Initialize session tracking for Flask using before/after request hooks

    Alternative to middleware approach - uses Flask's request lifecycle.
    Also tracks HTTP requests for analytics.

    Usage:
        from flask import Flask
        from scope_analytics.middleware import init_flask_session_tracking

        app = Flask(__name__)
        init_flask_session_tracking(app)

    Args:
        app: Flask application instance
        generate_temp_session: Generate temp session if header missing
    """
    from flask import request, g

    @app.before_request
    def extract_scope_session():
        # Start timing
        g.scope_start_time = time.time()

        session_id = request.headers.get(SESSION_HEADER)
        if session_id:
            ScopeContext.set_session_id(session_id)
            g.scope_session_id = session_id
        elif generate_temp_session:
            session_id = ScopeContext.generate_temp_session_id()
            ScopeContext.set_session_id(session_id)
            g.scope_session_id = session_id

        # Auto-extract user_id from JWT (for identity stitching)
        flask_headers = dict(request.headers)
        _auto_set_user_id_from_headers(flask_headers)

    @app.after_request
    def track_http_request_and_clear_context(response):
        # Track HTTP request
        if hasattr(g, 'scope_start_time'):
            latency_ms = (time.time() - g.scope_start_time) * 1000

            # Extract query params
            query_params = dict(request.args.items()) if request.args else {}

            # Extract content length
            content_length = None
            if request.content_length:
                content_length = request.content_length

            _track_http_request(
                method=request.method,
                path=request.path,
                status_code=response.status_code,
                latency_ms=latency_ms,
                query_params=query_params,
                client_ip=request.remote_addr,
                user_agent=request.user_agent.string if request.user_agent else None,
                content_type=request.content_type,
                content_length=content_length,
            )

        ScopeContext.clear()
        return response

    @app.teardown_request
    def teardown_scope_context(exception=None):
        # Ensure cleanup even if after_request doesn't run
        ScopeContext.clear()


# =============================================================================
# FastAPI Dependency (Alternative)
# =============================================================================

def get_scope_session():
    """
    FastAPI dependency for extracting session ID

    Usage:
        from fastapi import FastAPI, Depends, Request
        from scope_analytics.middleware import get_scope_session

        app = FastAPI()

        @app.get("/api/chat")
        async def chat(request: Request, session_id: str = Depends(get_scope_session)):
            # session_id is automatically extracted and set in context
            return {"session_id": session_id}
    """
    from fastapi import Request

    async def dependency(request: Request) -> str:
        session_id = request.headers.get(SESSION_HEADER)
        if session_id:
            ScopeContext.set_session_id(session_id)
        else:
            session_id = ScopeContext.ensure_session_id()
        return session_id

    return dependency


# =============================================================================
# Django Middleware
# =============================================================================

class DjangoScopeMiddleware:
    """
    Django middleware for session tracking

    Extracts X-Scope-Session-ID header and sets it in ScopeContext
    for the duration of the request.

    Usage:
        # settings.py
        MIDDLEWARE = [
            'scope_analytics.middleware.DjangoScopeMiddleware',
            # ... other middleware
        ]

    Or for auto-injection (no code changes):
        scope-run python manage.py runserver
    """

    def __init__(self, get_response):
        """
        Initialize middleware

        Args:
            get_response: The next middleware or view in the chain
        """
        self.get_response = get_response
        self.generate_temp_session = True
        self.log_missing_session = False

    def __call__(self, request):
        # Start timing
        start_time = time.time()

        # Extract session ID from headers
        session_id = request.META.get('HTTP_X_SCOPE_SESSION_ID')

        # Also check for direct header (some configurations)
        if not session_id:
            session_id = request.headers.get(SESSION_HEADER)

        if session_id:
            ScopeContext.set_session_id(session_id)
        elif self.generate_temp_session:
            session_id = ScopeContext.generate_temp_session_id()
            ScopeContext.set_session_id(session_id)
            if self.log_missing_session:
                logger.debug(f"No X-Scope-Session-ID header, generated temp: {session_id}")
        elif self.log_missing_session:
            logger.warning("No X-Scope-Session-ID header and temp generation disabled")

        # Auto-extract user_id from JWT (for identity stitching)
        # Django stores headers in META with HTTP_ prefix
        django_headers = {}
        for key, value in request.META.items():
            if key.startswith("HTTP_"):
                # Convert HTTP_AUTHORIZATION to authorization
                header_name = key[5:].replace("_", "-").lower()
                django_headers[header_name] = value
        _auto_set_user_id_from_headers(django_headers)

        # Extract request details for tracking
        method = request.method
        path = request.path
        query_params = dict(request.GET.items()) if hasattr(request, 'GET') else {}

        # Extract useful headers
        client_ip = request.META.get('REMOTE_ADDR')
        user_agent = request.META.get('HTTP_USER_AGENT')
        content_type = request.content_type if hasattr(request, 'content_type') else None
        content_length = None
        if request.META.get('CONTENT_LENGTH'):
            try:
                content_length = int(request.META['CONTENT_LENGTH'])
            except ValueError:
                pass

        try:
            response = self.get_response(request)

            # Calculate latency
            latency_ms = (time.time() - start_time) * 1000

            # Track HTTP request
            _track_http_request(
                method=method,
                path=path,
                status_code=response.status_code,
                latency_ms=latency_ms,
                query_params=query_params,
                client_ip=client_ip,
                user_agent=user_agent,
                content_type=content_type,
                content_length=content_length,
            )

            return response
        finally:
            # Always clear context after request to prevent leaks
            ScopeContext.clear()
