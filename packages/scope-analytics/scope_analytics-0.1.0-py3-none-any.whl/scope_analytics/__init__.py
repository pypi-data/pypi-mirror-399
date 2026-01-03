"""
Scope Analytics - Backend SDK
AI-powered analytics with automatic LLM conversation tracking
"""

import atexit
from typing import Optional

from .config import ScopeConfig
from .context import ScopeContext
from .events import EventFormatter
from .queue import EventQueue
from .client import ScopeAPIClient
from .patches.openai_patch import OpenAIPatcher
from .patches.anthropic_patch import AnthropicPatcher
from .patches.gemini_patch import GeminiPatcher
from .middleware import (
    ScopeSessionMiddleware,
    FlaskScopeMiddleware,
    init_flask_session_tracking,
    DjangoScopeMiddleware,
)

__version__ = "0.1.0"
__all__ = [
    "ScopeAnalytics",
    "ScopeContext",
    "get_sdk_instance",
    # Middleware exports
    "ScopeSessionMiddleware",      # For FastAPI/Starlette
    "FlaskScopeMiddleware",        # For Flask (WSGI wrapper)
    "init_flask_session_tracking", # For Flask (hooks approach)
    "DjangoScopeMiddleware",       # For Django
]

# Global SDK instance reference for middleware access
# This allows middleware to capture HTTP request events without requiring
# explicit SDK reference in user code
_global_sdk_instance: Optional["ScopeAnalytics"] = None


def get_sdk_instance() -> Optional["ScopeAnalytics"]:
    """
    Get the global SDK instance.

    Returns:
        ScopeAnalytics instance if initialized, None otherwise
    """
    return _global_sdk_instance


def _set_sdk_instance(instance: "ScopeAnalytics") -> None:
    """
    Set the global SDK instance.
    Called internally when ScopeAnalytics is initialized.
    """
    global _global_sdk_instance
    _global_sdk_instance = instance


class ScopeAnalytics:
    """
    Main SDK class for Scope Analytics

    Usage:
        scope = ScopeAnalytics(api_key="sk_live_...")

        # SDK automatically patches OpenAI, Anthropic, LangChain
        # All LLM calls are captured and sent to Scope AI
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        endpoint: Optional[str] = None,
        auto_patch: bool = True,
        batch_size: int = 10,
        batch_timeout_seconds: int = 5,
        max_queue_size: int = 1000,
        debug: bool = False,
        environment: Optional[str] = None,
    ):
        """
        Initialize Scope Analytics SDK

        Args:
            api_key: Secret API key (sk_live_... or sk_test_...)
            endpoint: API endpoint URL (default: https://api.scopeai.dev)
            auto_patch: Automatically patch LLM libraries (default: True)
            batch_size: Events per batch (default: 10)
            batch_timeout_seconds: Max wait before sending partial batch (default: 5)
            max_queue_size: Max events to queue (default: 1000)
            debug: Enable debug logging (default: False)
            environment: Environment name (default: production)
        """
        # Initialize configuration
        self.config = ScopeConfig(
            api_key=api_key,
            endpoint=endpoint,
            auto_patch=auto_patch,
            batch_size=batch_size,
            batch_timeout_seconds=batch_timeout_seconds,
            max_queue_size=max_queue_size,
            debug=debug,
            environment=environment,
        )

        # Initialize components
        self.event_formatter = EventFormatter(self.config)
        self.client = ScopeAPIClient(self.config)
        self.queue = EventQueue(
            batch_size=self.config.batch_size,
            batch_timeout_seconds=self.config.batch_timeout_seconds,
            max_queue_size=self.config.max_queue_size,
            flush_callback=self._flush_events,
            config=self.config,
        )

        # Initialize patchers
        self.openai_patcher = OpenAIPatcher(self)
        self.anthropic_patcher = AnthropicPatcher(self)
        self.gemini_patcher = GeminiPatcher(self)
        self.patches = []  # List of successfully applied patches

        # Start queue background thread
        self.queue.start()

        # Register shutdown hook
        atexit.register(self.shutdown)

        self.config.log("Scope Analytics SDK initialized")
        self.config.log(f"Configuration: {self.config.to_dict()}")

        # Register as global instance for middleware access
        _set_sdk_instance(self)

        # Auto-patch LLM libraries if enabled
        if self.config.auto_patch:
            self._apply_patches()

    def _apply_patches(self):
        """Apply monkey patches to LLM libraries"""
        self.config.log("Auto-patching enabled - will patch LLM libraries")

        # Patch OpenAI
        try:
            import openai
            self.config.log("OpenAI library detected - patching...")
            if self.openai_patcher.patch():
                self.patches.append('openai')
        except ImportError:
            self.config.log("OpenAI library not installed - skipping patch")

        # Patch Anthropic
        try:
            import anthropic
            self.config.log("Anthropic library detected - patching...")
            if self.anthropic_patcher.patch():
                self.patches.append('anthropic')
        except ImportError:
            self.config.log("Anthropic library not installed - skipping patch")

        # Patch Google Gemini
        try:
            import google.generativeai
            self.config.log("Google Generative AI library detected - patching...")
            if self.gemini_patcher.patch():
                self.patches.append('gemini')
        except ImportError:
            self.config.log("Google Generative AI library not installed - skipping patch")

    def track_event(self, event_type: str, properties: dict):
        """
        Manually track an event

        Args:
            event_type: Type of event (e.g., "llm_call", "external_api_call")
            properties: Event properties
        """
        self.config.log(f"Tracking event: {event_type}")

        # Create event with standard fields
        event = {
            "event_type": event_type,
            "source": self.config.sdk_source,
            **properties
        }

        # Validate and enqueue
        if self.event_formatter.validate_event(event):
            self.queue.enqueue(event)

    def identify(self, user_id: str, traits: Optional[dict] = None):
        """
        Identify a user and optionally set traits

        Args:
            user_id: Unique user identifier
            traits: Optional user traits (e.g., email, name, plan)
        """
        ScopeContext.set_user_id(user_id)
        self.config.log(f"Identified user: {user_id}")

        # TODO: Send identify event to API
        if traits:
            self.config.log(f"User traits: {traits}")

    def _flush_events(self, events: list):
        """
        Callback for flushing events to API
        Called by event queue when batch is ready

        Args:
            events: List of events to flush
        """
        success = self.client.ship_events(events)

        if not success:
            self.config.log(f"⚠️ Failed to ship {len(events)} events")

    def shutdown(self):
        """
        Gracefully shutdown SDK
        Flushes remaining events and cleans up resources
        """
        self.config.log("Shutting down Scope Analytics SDK...")

        # Stop queue and flush remaining events
        if self.queue:
            self.queue.stop()

        # Close HTTP client
        if self.client:
            self.client.close()

        # Remove patches
        if 'openai' in self.patches:
            self.openai_patcher.unpatch()
        if 'anthropic' in self.patches:
            self.anthropic_patcher.unpatch()
        if 'gemini' in self.patches:
            self.gemini_patcher.unpatch()

        self.config.log("Scope Analytics SDK shutdown complete")
