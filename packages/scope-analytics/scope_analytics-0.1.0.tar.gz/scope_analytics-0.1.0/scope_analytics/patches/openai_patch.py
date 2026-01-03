"""
OpenAI library patching for Scope Analytics
Supports multiple OpenAI versions and usage patterns
"""

import time
import functools
from typing import Optional, Any, Iterator
import sys

from ..context import ScopeContext


class OpenAIPatcher:
    """
    Patches OpenAI library to automatically capture LLM calls

    Supports:
    - OpenAI v0.x (old API: openai.ChatCompletion.create)
    - OpenAI v1.0+ (new API: client.chat.completions.create)
    - Sync and async calls
    - Streaming and non-streaming responses
    """

    def __init__(self, scope_sdk):
        """
        Initialize OpenAI patcher

        Args:
            scope_sdk: Reference to main ScopeAnalytics instance
        """
        self.scope_sdk = scope_sdk
        self.config = scope_sdk.config
        self.event_formatter = scope_sdk.event_formatter
        self.queue = scope_sdk.queue

        self.original_methods = {}
        self.is_patched = False
        self.openai_version = None

    def patch(self) -> bool:
        """
        Apply OpenAI patches

        Returns:
            True if patching succeeded, False otherwise
        """
        try:
            import openai

            # Detect OpenAI version
            self.openai_version = self._detect_version(openai)
            self.config.log(f"Detected OpenAI version: {self.openai_version}")

            if self.openai_version.startswith("1."):
                # Patch new API (v1.0+)
                self._patch_v1(openai)
            else:
                # Patch old API (v0.x)
                self._patch_v0(openai)

            self.is_patched = True
            self.config.log("✅ OpenAI patching successful")
            return True

        except ImportError:
            self.config.log("OpenAI library not installed - skipping patch")
            return False
        except Exception as e:
            self.config.log(f"⚠️ Failed to patch OpenAI: {e}")
            return False

    def unpatch(self):
        """Remove OpenAI patches"""
        if not self.is_patched:
            return

        try:
            import openai

            # Restore original methods
            for key, original in self.original_methods.items():
                parts = key.split('.')
                obj = openai
                for part in parts[:-1]:
                    obj = getattr(obj, part)
                setattr(obj, parts[-1], original)

            self.is_patched = False
            self.config.log("OpenAI patches removed")

        except Exception as e:
            self.config.log(f"⚠️ Failed to unpatch OpenAI: {e}")

    def _detect_version(self, openai) -> str:
        """Detect OpenAI library version"""
        if hasattr(openai, '__version__'):
            return openai.__version__
        elif hasattr(openai, 'version'):
            return openai.version.VERSION
        else:
            # Default to v1 if can't detect
            return "1.0.0"

    def _patch_v1(self, openai):
        """Patch OpenAI v1.0+ API"""
        self.config.log("Patching OpenAI v1.0+ API...")

        # Patch sync client
        if hasattr(openai, 'OpenAI'):
            self._patch_client_class(openai.OpenAI, 'OpenAI')

        # Patch async client
        if hasattr(openai, 'AsyncOpenAI'):
            self._patch_async_client_class(openai.AsyncOpenAI, 'AsyncOpenAI')

    def _patch_v0(self, openai):
        """Patch OpenAI v0.x API"""
        self.config.log("Patching OpenAI v0.x API...")

        # Patch ChatCompletion.create
        if hasattr(openai, 'ChatCompletion'):
            original = openai.ChatCompletion.create
            self.original_methods['ChatCompletion.create'] = original
            openai.ChatCompletion.create = self._wrap_v0_create(original)

        # Patch ChatCompletion.acreate (async)
        if hasattr(openai, 'ChatCompletion') and hasattr(openai.ChatCompletion, 'acreate'):
            original = openai.ChatCompletion.acreate
            self.original_methods['ChatCompletion.acreate'] = original
            openai.ChatCompletion.acreate = self._wrap_v0_async_create(original)

    def _patch_client_class(self, client_class, class_name: str):
        """Patch OpenAI v1+ client class"""
        # We need to patch the instance method, not the class method
        # This is tricky - we'll patch at the resources level

        # Store original __init__ and wrap it to patch instance methods
        original_init = client_class.__init__

        def wrapped_init(instance, *args, **kwargs):
            # Call original init
            original_init(instance, *args, **kwargs)

            # Patch chat completions on this instance
            if hasattr(instance, 'chat') and hasattr(instance.chat, 'completions'):
                original_create = instance.chat.completions.create
                instance.chat.completions.create = self._wrap_v1_create(original_create)

        client_class.__init__ = wrapped_init
        self.original_methods[f'{class_name}.__init__'] = original_init

    def _patch_async_client_class(self, client_class, class_name: str):
        """Patch OpenAI v1+ async client class"""
        original_init = client_class.__init__

        def wrapped_init(instance, *args, **kwargs):
            # Call original init
            original_init(instance, *args, **kwargs)

            # Patch async chat completions
            if hasattr(instance, 'chat') and hasattr(instance.chat, 'completions'):
                original_create = instance.chat.completions.create
                instance.chat.completions.create = self._wrap_v1_async_create(original_create)

        client_class.__init__ = wrapped_init
        self.original_methods[f'{class_name}.__init__'] = original_init

    def _wrap_v1_create(self, original_func):
        """Wrap OpenAI v1+ sync create method"""
        @functools.wraps(original_func)
        def wrapper(*args, **kwargs):
            # RECURSION GUARD: Skip capture if inside Scope internal code
            # This prevents infinite loops when Scope backend tracks itself
            if ScopeContext.is_in_scope_context():
                return original_func(*args, **kwargs)

            start_time = time.time()

            try:
                # Call original function
                response = original_func(*args, **kwargs)

                # Handle streaming vs non-streaming
                if kwargs.get('stream', False):
                    # Return streaming wrapper
                    return self._wrap_streaming_response(response, start_time, kwargs)
                else:
                    # Capture non-streaming response
                    latency_ms = (time.time() - start_time) * 1000
                    self._capture_v1_response(response, kwargs, latency_ms)
                    return response

            except Exception as e:
                # Capture error
                latency_ms = (time.time() - start_time) * 1000
                self._capture_error(kwargs, str(e), latency_ms)
                raise

        return wrapper

    def _wrap_v1_async_create(self, original_func):
        """Wrap OpenAI v1+ async create method"""
        @functools.wraps(original_func)
        async def wrapper(*args, **kwargs):
            # RECURSION GUARD: Skip capture if inside Scope internal code
            if ScopeContext.is_in_scope_context():
                return await original_func(*args, **kwargs)

            start_time = time.time()

            try:
                # Call original async function
                response = await original_func(*args, **kwargs)

                # Handle streaming vs non-streaming
                if kwargs.get('stream', False):
                    # Return async streaming wrapper
                    return self._wrap_async_streaming_response(response, start_time, kwargs)
                else:
                    # Capture non-streaming response
                    latency_ms = (time.time() - start_time) * 1000
                    self._capture_v1_response(response, kwargs, latency_ms)
                    return response

            except Exception as e:
                # Capture error
                latency_ms = (time.time() - start_time) * 1000
                self._capture_error(kwargs, str(e), latency_ms)
                raise

        return wrapper

    def _wrap_v0_create(self, original_func):
        """Wrap OpenAI v0.x sync create method"""
        @functools.wraps(original_func)
        def wrapper(*args, **kwargs):
            # RECURSION GUARD: Skip capture if inside Scope internal code
            if ScopeContext.is_in_scope_context():
                return original_func(*args, **kwargs)

            start_time = time.time()

            try:
                response = original_func(*args, **kwargs)
                latency_ms = (time.time() - start_time) * 1000

                # Handle streaming
                if kwargs.get('stream', False):
                    return self._wrap_v0_streaming_response(response, start_time, kwargs)
                else:
                    self._capture_v0_response(response, kwargs, latency_ms)
                    return response

            except Exception as e:
                latency_ms = (time.time() - start_time) * 1000
                self._capture_error(kwargs, str(e), latency_ms)
                raise

        return wrapper

    def _wrap_v0_async_create(self, original_func):
        """Wrap OpenAI v0.x async create method"""
        @functools.wraps(original_func)
        async def wrapper(*args, **kwargs):
            # RECURSION GUARD: Skip capture if inside Scope internal code
            if ScopeContext.is_in_scope_context():
                return await original_func(*args, **kwargs)

            start_time = time.time()

            try:
                response = await original_func(*args, **kwargs)
                latency_ms = (time.time() - start_time) * 1000
                self._capture_v0_response(response, kwargs, latency_ms)
                return response

            except Exception as e:
                latency_ms = (time.time() - start_time) * 1000
                self._capture_error(kwargs, str(e), latency_ms)
                raise

        return wrapper

    def _wrap_streaming_response(self, response, start_time, kwargs):
        """Wrap v1+ streaming response to capture chunks"""
        chunks = []

        for chunk in response:
            chunks.append(chunk)
            yield chunk

        # After streaming completes, capture event
        latency_ms = (time.time() - start_time) * 1000
        self._capture_v1_streaming_response(chunks, kwargs, latency_ms)

    async def _wrap_async_streaming_response(self, response, start_time, kwargs):
        """Wrap v1+ async streaming response"""
        chunks = []

        async for chunk in response:
            chunks.append(chunk)
            yield chunk

        # After streaming completes, capture event
        latency_ms = (time.time() - start_time) * 1000
        self._capture_v1_streaming_response(chunks, kwargs, latency_ms)

    def _wrap_v0_streaming_response(self, response, start_time, kwargs):
        """Wrap v0.x streaming response"""
        chunks = []

        for chunk in response:
            chunks.append(chunk)
            yield chunk

        # After streaming completes, capture event
        latency_ms = (time.time() - start_time) * 1000
        self._capture_v0_streaming_response(chunks, kwargs, latency_ms)

    def _capture_v1_response(self, response, kwargs, latency_ms):
        """Capture OpenAI v1+ non-streaming response"""
        try:
            # Extract data from response
            model = kwargs.get('model', response.model if hasattr(response, 'model') else 'unknown')
            messages = kwargs.get('messages', [])

            # Extract response content
            response_text = ""
            if hasattr(response, 'choices') and len(response.choices) > 0:
                choice = response.choices[0]
                if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
                    response_text = choice.message.content or ""

            # Extract token usage
            tokens = {}
            if hasattr(response, 'usage'):
                tokens = {
                    'prompt_tokens': response.usage.prompt_tokens,
                    'completion_tokens': response.usage.completion_tokens,
                    'total_tokens': response.usage.total_tokens,
                }

            # Format and queue event
            event = self.event_formatter.format_llm_call(
                provider='openai',
                model=model,
                messages=messages,
                response=response_text,
                tokens=tokens,
                latency_ms=latency_ms,
                error=None,
            )

            self.queue.enqueue(event)
            self.config.log(f"Captured OpenAI call: {model}")

        except Exception as e:
            self.config.log(f"⚠️ Failed to capture OpenAI response: {e}")

    def _capture_v1_streaming_response(self, chunks, kwargs, latency_ms):
        """Capture OpenAI v1+ streaming response"""
        try:
            # Reconstruct response from chunks
            model = kwargs.get('model', 'unknown')
            messages = kwargs.get('messages', [])

            # Combine streaming chunks
            response_text = ""
            for chunk in chunks:
                if hasattr(chunk, 'choices') and len(chunk.choices) > 0:
                    delta = chunk.choices[0].delta
                    if hasattr(delta, 'content') and delta.content:
                        response_text += delta.content

            # Format and queue event
            event = self.event_formatter.format_llm_call(
                provider='openai',
                model=model,
                messages=messages,
                response=response_text,
                tokens={},  # Streaming usually doesn't include tokens
                latency_ms=latency_ms,
                error=None,
            )

            self.queue.enqueue(event)
            self.config.log(f"Captured OpenAI streaming call: {model}")

        except Exception as e:
            self.config.log(f"⚠️ Failed to capture OpenAI streaming response: {e}")

    def _capture_v0_response(self, response, kwargs, latency_ms):
        """Capture OpenAI v0.x response"""
        try:
            model = kwargs.get('model', response.get('model', 'unknown'))
            messages = kwargs.get('messages', [])

            # Extract response
            response_text = ""
            if 'choices' in response and len(response['choices']) > 0:
                choice = response['choices'][0]
                if 'message' in choice and 'content' in choice['message']:
                    response_text = choice['message']['content'] or ""

            # Extract tokens
            tokens = {}
            if 'usage' in response:
                tokens = {
                    'prompt_tokens': response['usage'].get('prompt_tokens', 0),
                    'completion_tokens': response['usage'].get('completion_tokens', 0),
                    'total_tokens': response['usage'].get('total_tokens', 0),
                }

            # Format and queue event
            event = self.event_formatter.format_llm_call(
                provider='openai',
                model=model,
                messages=messages,
                response=response_text,
                tokens=tokens,
                latency_ms=latency_ms,
                error=None,
            )

            self.queue.enqueue(event)
            self.config.log(f"Captured OpenAI call: {model}")

        except Exception as e:
            self.config.log(f"⚠️ Failed to capture OpenAI v0 response: {e}")

    def _capture_v0_streaming_response(self, chunks, kwargs, latency_ms):
        """Capture OpenAI v0.x streaming response"""
        try:
            model = kwargs.get('model', 'unknown')
            messages = kwargs.get('messages', [])

            # Combine streaming chunks
            response_text = ""
            for chunk in chunks:
                if 'choices' in chunk and len(chunk['choices']) > 0:
                    delta = chunk['choices'][0].get('delta', {})
                    if 'content' in delta:
                        response_text += delta['content']

            # Format and queue event
            event = self.event_formatter.format_llm_call(
                provider='openai',
                model=model,
                messages=messages,
                response=response_text,
                tokens={},
                latency_ms=latency_ms,
                error=None,
            )

            self.queue.enqueue(event)
            self.config.log(f"Captured OpenAI v0 streaming call: {model}")

        except Exception as e:
            self.config.log(f"⚠️ Failed to capture OpenAI v0 streaming response: {e}")

    def _capture_error(self, kwargs, error_message, latency_ms):
        """Capture failed LLM call"""
        try:
            model = kwargs.get('model', 'unknown')
            messages = kwargs.get('messages', [])

            event = self.event_formatter.format_llm_call(
                provider='openai',
                model=model,
                messages=messages,
                response="",
                tokens={},
                latency_ms=latency_ms,
                error=error_message,
            )

            self.queue.enqueue(event)
            self.config.log(f"Captured OpenAI error: {error_message}")

        except Exception as e:
            self.config.log(f"⚠️ Failed to capture OpenAI error: {e}")
