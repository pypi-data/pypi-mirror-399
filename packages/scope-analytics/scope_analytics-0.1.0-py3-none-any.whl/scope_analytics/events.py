"""
Event schema and formatters for Scope Analytics
Defines the structure of events captured by the backend SDK
"""

from datetime import datetime, timezone
from typing import Optional, Dict, Any, List
import re

from .context import ScopeContext


class EventFormatter:
    """Formats and validates events before shipping to API"""

    def __init__(self, config):
        self.config = config

    def format_llm_call(
        self,
        provider: str,
        model: str,
        messages: List[Dict[str, str]],
        response: str,
        tokens: Optional[Dict[str, int]] = None,
        latency_ms: Optional[float] = None,
        error: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, Any]:
        """
        Format an LLM call event

        Args:
            provider: LLM provider (openai, anthropic, etc.)
            model: Model name (gpt-4, claude-3-opus, etc.)
            messages: List of message dicts with role/content
            response: LLM response text
            tokens: Token usage (prompt_tokens, completion_tokens, total_tokens)
            latency_ms: Request latency in milliseconds
            error: Error message if call failed
            metadata: Additional metadata

        Returns:
            Formatted event dictionary
        """
        session_id = ScopeContext.get_session_id()
        user_id = ScopeContext.get_user_id()

        # Determine if this is a user-facing LLM call
        # If we have a session_id from frontend (not temp_), it's user-facing
        is_user_facing = session_id and not session_id.startswith("temp_")

        # Extract prompt and response for easy access
        prompt = self._extract_prompt(messages)

        # Redact sensitive information
        prompt = self._redact_sensitive_data(prompt)
        response = self._redact_sensitive_data(response)

        event = {
            "event_type": "llm_call",
            "source": self.config.sdk_source,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session_id": session_id or ScopeContext.ensure_session_id(),
            "user_id": user_id,

            # LLM call specific fields
            "provider": provider,
            "model": model,
            "prompt": prompt,
            "response": response,
            "messages": messages,  # Full message history
            "tokens": tokens or {},
            "latency_ms": latency_ms,
            "is_user_facing": is_user_facing,

            # Error handling
            "error": error,
            "success": error is None,

            # Server metadata
            "environment": self.config.environment,
            "sdk_version": self.config.sdk_version,
            "server_timestamp": datetime.now(timezone.utc).isoformat(),
        }

        # Add custom metadata
        if metadata:
            event["metadata"] = metadata

        return event

    def format_http_request(
        self,
        method: str,
        path: str,
        status_code: int,
        latency_ms: float,
        query_params: Optional[Dict[str, str]] = None,
        client_ip: Optional[str] = None,
        user_agent: Optional[str] = None,
        content_type: Optional[str] = None,
        content_length: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Format an incoming HTTP request event.

        This tracks ALL incoming HTTP requests to the user's backend,
        allowing AI agents to answer questions like "what patterns lead to cancellation?"
        by analyzing API call sequences.

        Args:
            method: HTTP method (GET, POST, PUT, DELETE, etc.)
            path: Request path (e.g., /api/users/123)
            status_code: HTTP response status code
            latency_ms: Request processing time in milliseconds
            query_params: Query string parameters
            client_ip: Client IP address
            user_agent: User-Agent header
            content_type: Content-Type header
            content_length: Content-Length header

        Returns:
            Formatted event dictionary
        """
        session_id = ScopeContext.get_session_id()
        user_id = ScopeContext.get_user_id()

        # Determine if this is a user-facing request
        # If we have a session_id from frontend (not temp_), it's user-initiated
        is_user_facing = session_id and not session_id.startswith("temp_")

        event = {
            "event_type": "http_request",
            "source": self.config.sdk_source,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session_id": session_id or ScopeContext.ensure_session_id(),
            "user_id": user_id,

            # HTTP request specific fields
            "method": method,
            "path": path,
            "status_code": status_code,
            "latency_ms": latency_ms,
            "query_params": query_params or {},
            "client_ip": client_ip,
            "user_agent": user_agent,
            "content_type": content_type,
            "content_length": content_length,

            # Derived fields for AI agent analysis
            "is_user_facing": is_user_facing,
            "success": 200 <= status_code < 400,
            "is_error": status_code >= 400,
            "is_client_error": 400 <= status_code < 500,
            "is_server_error": status_code >= 500,

            # Server metadata
            "environment": self.config.environment,
            "sdk_version": self.config.sdk_version,
            "server_timestamp": datetime.now(timezone.utc).isoformat(),
        }

        return event

    def format_external_api_call(
        self,
        method: str,
        url: str,
        status_code: int,
        latency_ms: float,
        request_body: Optional[str] = None,
        response_body: Optional[str] = None,
        error: Optional[str] = None,
    ) -> Dict[str, Any]:
        """
        Format an external API call event (Stripe, Twilio, etc.)

        Args:
            method: HTTP method (GET, POST, etc.)
            url: API endpoint URL
            status_code: HTTP status code
            latency_ms: Request latency in milliseconds
            request_body: Request body (optional)
            response_body: Response body (optional)
            error: Error message if call failed

        Returns:
            Formatted event dictionary
        """
        session_id = ScopeContext.get_session_id()
        user_id = ScopeContext.get_user_id()

        # Redact sensitive data from bodies
        if request_body:
            request_body = self._redact_sensitive_data(request_body)
        if response_body:
            response_body = self._redact_sensitive_data(response_body)

        event = {
            "event_type": "external_api_call",
            "source": self.config.sdk_source,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "session_id": session_id or ScopeContext.ensure_session_id(),
            "user_id": user_id,

            # API call specific fields
            "method": method,
            "url": url,
            "status_code": status_code,
            "latency_ms": latency_ms,
            "request_body": request_body,
            "response_body": response_body,

            # Error handling
            "error": error,
            "success": 200 <= status_code < 300 and error is None,

            # Server metadata
            "environment": self.config.environment,
            "sdk_version": self.config.sdk_version,
            "server_timestamp": datetime.now(timezone.utc).isoformat(),
        }

        return event

    def _extract_prompt(self, messages: List[Dict[str, str]]) -> str:
        """Extract the user prompt from messages list"""
        if not messages:
            return ""

        # Get the last user message as the prompt
        user_messages = [m for m in messages if m.get("role") == "user"]
        if user_messages:
            return user_messages[-1].get("content", "")

        return ""

    def _redact_sensitive_data(self, text: str) -> str:
        """
        Redact sensitive information from text using configured patterns

        Args:
            text: Text to redact

        Returns:
            Redacted text
        """
        if not text:
            return text

        redacted = text
        for pattern in self.config.redact_patterns:
            redacted = re.sub(pattern, r"\1***REDACTED***", redacted, flags=re.IGNORECASE)

        return redacted

    def validate_event(self, event: Dict[str, Any]) -> bool:
        """
        Validate event structure

        Args:
            event: Event dictionary

        Returns:
            True if valid, False otherwise
        """
        required_fields = ["event_type", "source", "timestamp", "session_id"]

        for field in required_fields:
            if field not in event:
                self.config.log(f"Invalid event: missing field '{field}'")
                return False

        return True
