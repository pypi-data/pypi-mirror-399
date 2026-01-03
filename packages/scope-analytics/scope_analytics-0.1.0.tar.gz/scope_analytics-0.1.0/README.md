# Scope Analytics - Backend SDK

AI-powered analytics for backend applications with **zero-code LLM conversation tracking**.

## Features

- **Automatic LLM Tracking**: Captures OpenAI, Anthropic, and Gemini calls automatically
- **Session Correlation**: Links backend events to frontend user sessions via `X-Scope-Session-ID` header
- **Conversation Intelligence**: Classifies LLM calls as user-facing vs background jobs
- **Zero Code Changes**: Drop-in integration with automatic monkey-patching
- **Async & Non-Blocking**: Events shipped in background without affecting performance

## Installation

```bash
pip install scope-analytics
```

## Quick Start

Choose your installation method:

### Option A: No-Code Installation (Recommended)

Zero code changes required - just change how you run your app.

**Step 1: Set your API key**
```bash
export SCOPE_API_KEY="sk_live_..."
```

**Step 2: Run with scope-run**
```bash
# Instead of:   python app.py
# Run:          scope-run python app.py

# Instead of:   uvicorn main:app --reload
# Run:          scope-run uvicorn main:app --reload

# Instead of:   gunicorn app:app -w 4
# Run:          scope-run gunicorn app:app -w 4

# Instead of:   flask run --port 5000
# Run:          scope-run flask run --port 5000
```

That's it! Your LLM calls are now automatically tracked AND correlated
with frontend sessions (for FastAPI, Flask, Django).

### Option B: Code-Based Installation

Add 2 lines to your app for more control.

```python
from scope_analytics import ScopeAnalytics
scope = ScopeAnalytics(api_key="sk_live_...")
```

For session correlation with frontend, add middleware:

**FastAPI:**
```python
from fastapi import FastAPI
from scope_analytics import ScopeAnalytics, ScopeSessionMiddleware

app = FastAPI()
app.add_middleware(ScopeSessionMiddleware)
scope = ScopeAnalytics(api_key="sk_live_...")
```

**Flask:**
```python
from flask import Flask
from scope_analytics import ScopeAnalytics, init_flask_session_tracking

app = Flask(__name__)
init_flask_session_tracking(app)
scope = ScopeAnalytics(api_key="sk_live_...")
```

**Django:**
```python
# settings.py
MIDDLEWARE = [
    'scope_analytics.middleware.DjangoScopeMiddleware',
    # ... other middleware
]
```

## Installation Comparison

| Feature | No-Code (`scope-run`) | Code-Based |
|---------|----------------------|------------|
| Code changes required | **None** | 2 lines minimum |
| LLM tracking | ✅ Automatic | ✅ Automatic |
| Session correlation | ✅ Automatic (FastAPI/Flask/Django) | Manual middleware |
| Custom configuration | Via env vars | Full Python API |
| Best for | Quick start, CI/CD, ops teams | Developers wanting control |

## CLI Usage

```bash
# Show version
scope-run --version

# Show help
scope-run --help

# Run with debug logging
scope-run --debug python app.py

# Dry run (show what would be executed)
scope-run --dry-run uvicorn main:app
```

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SCOPE_API_KEY` | Yes | Your Scope Analytics API key |
| `SCOPE_ENDPOINT` | No | Custom API endpoint |
| `SCOPE_DEBUG` | No | Set to 'true' for debug logging |
| `SCOPE_ENVIRONMENT` | No | Environment name (default: production) |

## Configuration (Code-Based)

```python
scope = ScopeAnalytics(
    api_key="sk_live_...",              # Required: Your secret API key
    endpoint="https://api.scopeai.dev", # Optional: API endpoint
    auto_patch=True,                    # Optional: Auto-patch LLM libraries (default: True)
    batch_size=10,                      # Optional: Events per batch (default: 10)
    batch_timeout_seconds=5,            # Optional: Max wait time (default: 5)
    debug=False,                        # Optional: Enable debug logging
    environment="production",           # Optional: Environment name
)
```

## Framework Support Matrix

| Framework | Auto-Injection | Session Correlation | How |
|-----------|----------------|---------------------|-----|
| FastAPI | ✅ Automatic | ✅ Full | Patches `FastAPI.__init__` |
| Starlette | ✅ Automatic | ✅ Full | Patches `Starlette.__init__` |
| Flask | ✅ Automatic | ✅ Full | Patches `Flask.__init__` |
| Django | ✅ Automatic | ✅ Full | Modifies `settings.MIDDLEWARE` |
| Other ASGI | ⚠️ Manual | ✅ With 1 line | Add `ScopeSessionMiddleware` |
| Other WSGI | ⚠️ Manual | ✅ With 1 line | Call `ScopeContext.set_session_id()` |
| No framework | ⚠️ Manual | ✅ With 1 line | Call `ScopeContext.set_session_id()` |

## Manual Session Correlation (For Other Frameworks)

```python
# Option A: ASGI middleware (for ASGI frameworks)
from scope_analytics import ScopeSessionMiddleware
app = ScopeSessionMiddleware(app)

# Option B: Manual context (for any framework)
from scope_analytics import ScopeContext

def my_request_handler(request):
    # Extract session from header and set context
    ScopeContext.set_session_id(request.headers.get('X-Scope-Session-ID'))

    # Your code - LLM calls will now have session_id attached
    response = openai.chat.completions.create(...)
```

**Key Point:** Even without middleware, LLM tracking STILL WORKS. The middleware is only needed for correlating backend events with frontend sessions via `X-Scope-Session-ID`.

## Frontend SDK

Add the frontend SDK to link user interactions with backend LLM calls:

```html
<script src="https://cdn.scopeai.dev/v1/sdk.js"
        data-api-key="pk_live_your_public_key"></script>
```

The frontend SDK automatically:
- Tracks clicks, page views, form submissions
- Generates session IDs (stored in localStorage)
- Sends `X-Scope-Session-ID` header with API requests

## Comparison with Industry Tools

| Feature | Scope (`scope-run`) | DataDog (`ddtrace-run`) | New Relic |
|---------|---------------------|-------------------------|-----------|
| No code changes | ✅ | ✅ | ✅ |
| Env var config | ✅ `SCOPE_API_KEY` | ✅ `DD_API_KEY` | ✅ `NEW_RELIC_LICENSE_KEY` |
| Works with uvicorn | ✅ | ✅ | ✅ |
| Works with gunicorn | ✅ | ✅ | ✅ |
| LLM call capture | ✅ | ❌ | ❌ |
| Session correlation | ✅ | ❌ | ❌ |
| Debug mode | ✅ `--debug` | ✅ `--info` | ✅ |

## Full Documentation

See [SDK Installation Guide](../docs/sdk-installation-guide.md) for complete documentation including:
- Detailed configuration options
- Troubleshooting guide
- Complete example applications
- Verification steps

## License

MIT
