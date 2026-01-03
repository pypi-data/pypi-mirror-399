"""
Anthropic library patching for Scope Analytics
Supports multiple Anthropic versions and usage patterns
"""

import time
import functools
from typing import Optional, Any

from ..context import ScopeContext


class AnthropicPatcher:
    """
    Patches Anthropic library to automatically capture LLM calls

    Supports:
    - Anthropic SDK (client.messages.create)
    - Sync and async calls
    - Streaming and non-streaming responses
    """

    def __init__(self, scope_sdk):
        """
        Initialize Anthropic patcher

        Args:
            scope_sdk: Reference to main ScopeAnalytics instance
        """
        self.scope_sdk = scope_sdk
        self.config = scope_sdk.config
        self.event_formatter = scope_sdk.event_formatter
        self.queue = scope_sdk.queue

        self.original_methods = {}
        self.is_patched = False
        self.anthropic_version = None

    def patch(self) -> bool:
        """
        Apply Anthropic patches

        Returns:
            True if patching succeeded, False otherwise
        """
        try:
            import anthropic

            # Detect Anthropic version
            self.anthropic_version = self._detect_version(anthropic)
            self.config.log(f"Detected Anthropic version: {self.anthropic_version}")

            # Patch sync client
            if hasattr(anthropic, 'Anthropic'):
                self._patch_client_class(anthropic.Anthropic, 'Anthropic')

            # Patch async client
            if hasattr(anthropic, 'AsyncAnthropic'):
                self._patch_async_client_class(anthropic.AsyncAnthropic, 'AsyncAnthropic')

            self.is_patched = True
            self.config.log("✅ Anthropic patching successful")
            return True

        except ImportError:
            self.config.log("Anthropic library not installed - skipping patch")
            return False
        except Exception as e:
            self.config.log(f"⚠️ Failed to patch Anthropic: {e}")
            return False

    def unpatch(self):
        """Remove Anthropic patches"""
        if not self.is_patched:
            return

        try:
            import anthropic

            # Restore original methods
            for key, original in self.original_methods.items():
                parts = key.split('.')
                obj = anthropic
                for part in parts[:-1]:
                    obj = getattr(obj, part)
                setattr(obj, parts[-1], original)

            self.is_patched = False
            self.config.log("Anthropic patches removed")

        except Exception as e:
            self.config.log(f"⚠️ Failed to unpatch Anthropic: {e}")

    def _detect_version(self, anthropic) -> str:
        """Detect Anthropic library version"""
        if hasattr(anthropic, '__version__'):
            return anthropic.__version__
        else:
            return "unknown"

    def _patch_client_class(self, client_class, class_name: str):
        """Patch Anthropic sync client class"""
        original_init = client_class.__init__

        def wrapped_init(instance, *args, **kwargs):
            # Call original init
            original_init(instance, *args, **kwargs)

            # Patch messages.create on this instance
            if hasattr(instance, 'messages') and hasattr(instance.messages, 'create'):
                original_create = instance.messages.create
                instance.messages.create = self._wrap_create(original_create)

                # Also patch stream if available
                if hasattr(instance.messages, 'stream'):
                    original_stream = instance.messages.stream
                    instance.messages.stream = self._wrap_stream(original_stream)

        client_class.__init__ = wrapped_init
        self.original_methods[f'{class_name}.__init__'] = original_init

    def _patch_async_client_class(self, client_class, class_name: str):
        """Patch Anthropic async client class"""
        original_init = client_class.__init__

        def wrapped_init(instance, *args, **kwargs):
            # Call original init
            original_init(instance, *args, **kwargs)

            # Patch async messages.create
            if hasattr(instance, 'messages') and hasattr(instance.messages, 'create'):
                original_create = instance.messages.create
                instance.messages.create = self._wrap_async_create(original_create)

                # Also patch async stream if available
                if hasattr(instance.messages, 'stream'):
                    original_stream = instance.messages.stream
                    instance.messages.stream = self._wrap_async_stream(original_stream)

        client_class.__init__ = wrapped_init
        self.original_methods[f'{class_name}.__init__'] = original_init

    def _wrap_create(self, original_func):
        """Wrap sync messages.create method"""
        @functools.wraps(original_func)
        def wrapper(*args, **kwargs):
            # RECURSION GUARD: Skip capture if inside Scope internal code
            if ScopeContext.is_in_scope_context():
                return original_func(*args, **kwargs)

            start_time = time.time()

            try:
                # Check for streaming
                if kwargs.get('stream', False):
                    # Handle streaming response
                    response = original_func(*args, **kwargs)
                    return self._wrap_streaming_response(response, start_time, kwargs)
                else:
                    # Normal response
                    response = original_func(*args, **kwargs)
                    latency_ms = (time.time() - start_time) * 1000
                    self._capture_response(response, kwargs, latency_ms)
                    return response

            except Exception as e:
                latency_ms = (time.time() - start_time) * 1000
                self._capture_error(kwargs, str(e), latency_ms)
                raise

        return wrapper

    def _wrap_async_create(self, original_func):
        """Wrap async messages.create method"""
        @functools.wraps(original_func)
        async def wrapper(*args, **kwargs):
            # RECURSION GUARD: Skip capture if inside Scope internal code
            if ScopeContext.is_in_scope_context():
                return await original_func(*args, **kwargs)

            start_time = time.time()

            try:
                if kwargs.get('stream', False):
                    # Handle async streaming
                    response = await original_func(*args, **kwargs)
                    return self._wrap_async_streaming_response(response, start_time, kwargs)
                else:
                    # Normal async response
                    response = await original_func(*args, **kwargs)
                    latency_ms = (time.time() - start_time) * 1000
                    self._capture_response(response, kwargs, latency_ms)
                    return response

            except Exception as e:
                latency_ms = (time.time() - start_time) * 1000
                self._capture_error(kwargs, str(e), latency_ms)
                raise

        return wrapper

    def _wrap_stream(self, original_func):
        """Wrap sync stream method (context manager)"""
        patcher = self

        @functools.wraps(original_func)
        def wrapper(*args, **kwargs):
            start_time = time.time()

            # Get the stream context manager
            stream_cm = original_func(*args, **kwargs)

            # Wrap the context manager
            class WrappedStream:
                def __init__(self, cm):
                    self._cm = cm
                    self._chunks = []
                    self._response = None

                def __enter__(self):
                    self._stream = self._cm.__enter__()
                    return self

                def __exit__(self, *args):
                    result = self._cm.__exit__(*args)
                    # Capture after streaming completes
                    latency_ms = (time.time() - start_time) * 1000
                    patcher._capture_streaming_response(self._chunks, kwargs, latency_ms, self._response)
                    return result

                def __iter__(self):
                    return self

                def __next__(self):
                    try:
                        event = next(self._stream)
                        self._chunks.append(event)
                        return event
                    except StopIteration:
                        raise

                def get_final_message(self):
                    if hasattr(self._stream, 'get_final_message'):
                        self._response = self._stream.get_final_message()
                        return self._response
                    return None

            return WrappedStream(stream_cm)

        return wrapper

    def _wrap_async_stream(self, original_func):
        """Wrap async stream method"""
        patcher = self

        @functools.wraps(original_func)
        def wrapper(*args, **kwargs):
            start_time = time.time()
            stream_cm = original_func(*args, **kwargs)

            class WrappedAsyncStream:
                def __init__(self, cm):
                    self._cm = cm
                    self._chunks = []
                    self._response = None

                async def __aenter__(self):
                    self._stream = await self._cm.__aenter__()
                    return self

                async def __aexit__(self, *args):
                    result = await self._cm.__aexit__(*args)
                    latency_ms = (time.time() - start_time) * 1000
                    patcher._capture_streaming_response(self._chunks, kwargs, latency_ms, self._response)
                    return result

                def __aiter__(self):
                    return self

                async def __anext__(self):
                    try:
                        event = await self._stream.__anext__()
                        self._chunks.append(event)
                        return event
                    except StopAsyncIteration:
                        raise

                async def get_final_message(self):
                    if hasattr(self._stream, 'get_final_message'):
                        self._response = await self._stream.get_final_message()
                        return self._response
                    return None

            return WrappedAsyncStream(stream_cm)

        return wrapper

    def _wrap_streaming_response(self, response, start_time, kwargs):
        """Wrap sync streaming response"""
        chunks = []

        for chunk in response:
            chunks.append(chunk)
            yield chunk

        # After streaming completes, capture event
        latency_ms = (time.time() - start_time) * 1000
        self._capture_streaming_response(chunks, kwargs, latency_ms, None)

    async def _wrap_async_streaming_response(self, response, start_time, kwargs):
        """Wrap async streaming response"""
        chunks = []

        async for chunk in response:
            chunks.append(chunk)
            yield chunk

        # After streaming completes, capture event
        latency_ms = (time.time() - start_time) * 1000
        self._capture_streaming_response(chunks, kwargs, latency_ms, None)

    def _capture_response(self, response, kwargs, latency_ms):
        """Capture non-streaming Anthropic response"""
        try:
            # Extract model
            model = kwargs.get('model', getattr(response, 'model', 'unknown'))
            messages = kwargs.get('messages', [])

            # Extract response content
            response_text = ""
            if hasattr(response, 'content') and len(response.content) > 0:
                for block in response.content:
                    if hasattr(block, 'text'):
                        response_text += block.text

            # Extract token usage
            tokens = {}
            if hasattr(response, 'usage'):
                tokens = {
                    'prompt_tokens': getattr(response.usage, 'input_tokens', 0),
                    'completion_tokens': getattr(response.usage, 'output_tokens', 0),
                    'total_tokens': getattr(response.usage, 'input_tokens', 0) + getattr(response.usage, 'output_tokens', 0),
                }

            # Format and queue event
            event = self.event_formatter.format_llm_call(
                provider='anthropic',
                model=model,
                messages=messages,
                response=response_text,
                tokens=tokens,
                latency_ms=latency_ms,
                error=None,
            )

            self.queue.enqueue(event)
            self.config.log(f"Captured Anthropic call: {model}")

        except Exception as e:
            self.config.log(f"⚠️ Failed to capture Anthropic response: {e}")

    def _capture_streaming_response(self, chunks, kwargs, latency_ms, final_response):
        """Capture streaming Anthropic response"""
        try:
            model = kwargs.get('model', 'unknown')
            messages = kwargs.get('messages', [])

            # Try to extract from final response first
            response_text = ""
            tokens = {}

            if final_response:
                if hasattr(final_response, 'content'):
                    for block in final_response.content:
                        if hasattr(block, 'text'):
                            response_text += block.text

                if hasattr(final_response, 'usage'):
                    tokens = {
                        'prompt_tokens': getattr(final_response.usage, 'input_tokens', 0),
                        'completion_tokens': getattr(final_response.usage, 'output_tokens', 0),
                        'total_tokens': getattr(final_response.usage, 'input_tokens', 0) + getattr(final_response.usage, 'output_tokens', 0),
                    }
            else:
                # Extract from chunks
                for chunk in chunks:
                    if hasattr(chunk, 'delta') and hasattr(chunk.delta, 'text'):
                        response_text += chunk.delta.text
                    elif hasattr(chunk, 'type') and chunk.type == 'content_block_delta':
                        if hasattr(chunk, 'delta') and hasattr(chunk.delta, 'text'):
                            response_text += chunk.delta.text

            # Format and queue event
            event = self.event_formatter.format_llm_call(
                provider='anthropic',
                model=model,
                messages=messages,
                response=response_text,
                tokens=tokens,
                latency_ms=latency_ms,
                error=None,
            )

            self.queue.enqueue(event)
            self.config.log(f"Captured Anthropic streaming call: {model}")

        except Exception as e:
            self.config.log(f"⚠️ Failed to capture Anthropic streaming response: {e}")

    def _capture_error(self, kwargs, error_message, latency_ms):
        """Capture failed LLM call"""
        try:
            model = kwargs.get('model', 'unknown')
            messages = kwargs.get('messages', [])

            event = self.event_formatter.format_llm_call(
                provider='anthropic',
                model=model,
                messages=messages,
                response="",
                tokens={},
                latency_ms=latency_ms,
                error=error_message,
            )

            self.queue.enqueue(event)
            self.config.log(f"Captured Anthropic error: {error_message}")

        except Exception as e:
            self.config.log(f"⚠️ Failed to capture Anthropic error: {e}")
