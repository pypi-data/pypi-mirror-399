"""
Context management for Scope Analytics SDK using contextvars
Handles session ID propagation across async boundaries
"""

import contextvars
from typing import Optional
from contextlib import contextmanager
import uuid

# Context variables for tracking current request context
session_id_context: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    'scope_session_id', default=None
)

user_id_context: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar(
    'scope_user_id', default=None
)

# Recursion guard - prevents infinite loops when Scope tracks its own LLM calls
# This is critical when Scope AI backend uses Scope SDK to track itself
_in_scope_context: contextvars.ContextVar[bool] = contextvars.ContextVar(
    'scope_in_scope_context', default=False
)


class ScopeContext:
    """
    Manages request-scoped context using Python's contextvars.

    This ensures session IDs are properly isolated across concurrent requests
    and propagated through async operations.
    """

    @staticmethod
    def set_session_id(session_id: str) -> None:
        """
        Set the session ID for the current context

        Args:
            session_id: Session ID from X-Scope-Session-ID header
        """
        session_id_context.set(session_id)

    @staticmethod
    def get_session_id() -> Optional[str]:
        """
        Get the session ID from current context

        Returns:
            Session ID if set, None otherwise
        """
        return session_id_context.get()

    @staticmethod
    def set_user_id(user_id: str) -> None:
        """
        Set the user ID for the current context

        Args:
            user_id: User ID from backend application
        """
        user_id_context.set(user_id)

    @staticmethod
    def get_user_id() -> Optional[str]:
        """
        Get the user ID from current context

        Returns:
            User ID if set, None otherwise
        """
        return user_id_context.get()

    @staticmethod
    def clear() -> None:
        """
        Clear all context variables
        Should be called after request completes to prevent leaks
        """
        session_id_context.set(None)
        user_id_context.set(None)

    @staticmethod
    def generate_temp_session_id() -> str:
        """
        Generate a temporary session ID for requests without X-Scope-Session-ID header

        Returns:
            Temporary session ID with 'temp_' prefix
        """
        return f"temp_{uuid.uuid4().hex[:16]}"

    @staticmethod
    def ensure_session_id() -> str:
        """
        Get session ID from context, or generate temporary one if missing

        Returns:
            Session ID (either from context or temporary)
        """
        session_id = session_id_context.get()
        if not session_id:
            session_id = ScopeContext.generate_temp_session_id()
            session_id_context.set(session_id)
        return session_id

    @staticmethod
    def get_context_dict() -> dict:
        """
        Get all context variables as dictionary

        Returns:
            Dictionary with current context values
        """
        return {
            "session_id": session_id_context.get(),
            "user_id": user_id_context.get(),
        }

    # =========================================================================
    # Recursion Guard - Prevents infinite loops when Scope tracks itself
    # =========================================================================

    @staticmethod
    def is_in_scope_context() -> bool:
        """
        Check if we're currently inside Scope SDK code.

        This prevents infinite recursion when:
        1. Scope backend uses OpenAI for embeddings
        2. Scope backend has Scope SDK installed
        3. Without this guard, embedding calls would be captured → sent to API → trigger more embeddings

        Returns:
            True if inside Scope context, False otherwise
        """
        return _in_scope_context.get()

    @staticmethod
    def enter_scope_context() -> None:
        """
        Mark that we're entering Scope SDK internal code.
        LLM calls made while in this context will NOT be captured.
        """
        _in_scope_context.set(True)

    @staticmethod
    def exit_scope_context() -> None:
        """
        Mark that we're exiting Scope SDK internal code.
        """
        _in_scope_context.set(False)

    @staticmethod
    @contextmanager
    def scope_internal():
        """
        Context manager for Scope internal operations.

        Usage:
            with ScopeContext.scope_internal():
                # LLM calls here will NOT be tracked
                embedding = openai.embeddings.create(...)

        This is used by Scope's own backend to prevent recursion.
        """
        previous = _in_scope_context.get()
        _in_scope_context.set(True)
        try:
            yield
        finally:
            _in_scope_context.set(previous)
