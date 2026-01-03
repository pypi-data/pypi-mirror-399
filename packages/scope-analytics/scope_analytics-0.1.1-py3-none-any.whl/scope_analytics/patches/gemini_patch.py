"""
Google Gemini (Generative AI) library patching for Scope Analytics
Supports google-generativeai library
"""

import time
import functools
from typing import Optional, Any

from ..context import ScopeContext


class GeminiPatcher:
    """
    Patches Google Generative AI library to automatically capture LLM calls

    Supports:
    - GenerativeModel.generate_content()
    - ChatSession.send_message()
    - Sync and async calls
    - Streaming responses
    """

    def __init__(self, scope_sdk):
        """
        Initialize Gemini patcher

        Args:
            scope_sdk: Reference to main ScopeAnalytics instance
        """
        self.scope_sdk = scope_sdk
        self.config = scope_sdk.config
        self.event_formatter = scope_sdk.event_formatter
        self.queue = scope_sdk.queue

        self.original_methods = {}
        self.is_patched = False
        self.genai_version = None

    def patch(self) -> bool:
        """
        Apply Gemini patches

        Returns:
            True if patching succeeded, False otherwise
        """
        try:
            import google.generativeai as genai

            # Detect version
            self.genai_version = self._detect_version(genai)
            self.config.log(f"Detected Google Generative AI version: {self.genai_version}")

            # Patch GenerativeModel
            if hasattr(genai, 'GenerativeModel'):
                self._patch_generative_model(genai.GenerativeModel)

            self.is_patched = True
            self.config.log("✅ Gemini patching successful")
            return True

        except ImportError:
            self.config.log("Google Generative AI library not installed - skipping patch")
            return False
        except Exception as e:
            self.config.log(f"⚠️ Failed to patch Gemini: {e}")
            return False

    def unpatch(self):
        """Remove Gemini patches"""
        if not self.is_patched:
            return

        try:
            import google.generativeai as genai

            # Restore original methods
            for key, original in self.original_methods.items():
                if key == 'GenerativeModel.generate_content':
                    genai.GenerativeModel.generate_content = original
                elif key == 'GenerativeModel.generate_content_async':
                    genai.GenerativeModel.generate_content_async = original

            self.is_patched = False
            self.config.log("Gemini patches removed")

        except Exception as e:
            self.config.log(f"⚠️ Failed to unpatch Gemini: {e}")

    def _detect_version(self, genai) -> str:
        """Detect Google Generative AI library version"""
        try:
            import google.generativeai as genai_module
            if hasattr(genai_module, '__version__'):
                return genai_module.__version__
        except:
            pass
        return "unknown"

    def _patch_generative_model(self, model_class):
        """Patch GenerativeModel class"""

        # Patch generate_content (sync)
        if hasattr(model_class, 'generate_content'):
            original = model_class.generate_content
            self.original_methods['GenerativeModel.generate_content'] = original
            model_class.generate_content = self._wrap_generate_content(original)

        # Patch generate_content_async (async)
        if hasattr(model_class, 'generate_content_async'):
            original = model_class.generate_content_async
            self.original_methods['GenerativeModel.generate_content_async'] = original
            model_class.generate_content_async = self._wrap_generate_content_async(original)

        # Patch start_chat to wrap ChatSession
        if hasattr(model_class, 'start_chat'):
            original_start_chat = model_class.start_chat
            self.original_methods['GenerativeModel.start_chat'] = original_start_chat
            model_class.start_chat = self._wrap_start_chat(original_start_chat)

    def _wrap_generate_content(self, original_func):
        """Wrap sync generate_content method"""
        patcher = self

        @functools.wraps(original_func)
        def wrapper(self_model, *args, **kwargs):
            # RECURSION GUARD: Skip capture if inside Scope internal code
            if ScopeContext.is_in_scope_context():
                return original_func(self_model, *args, **kwargs)

            start_time = time.time()

            # Extract prompt from args or kwargs
            prompt = args[0] if args else kwargs.get('contents', '')

            try:
                # Check for streaming
                if kwargs.get('stream', False):
                    response = original_func(self_model, *args, **kwargs)
                    return patcher._wrap_streaming_response(response, start_time, self_model, prompt)
                else:
                    response = original_func(self_model, *args, **kwargs)
                    latency_ms = (time.time() - start_time) * 1000
                    patcher._capture_response(response, self_model, prompt, latency_ms)
                    return response

            except Exception as e:
                latency_ms = (time.time() - start_time) * 1000
                patcher._capture_error(self_model, prompt, str(e), latency_ms)
                raise

        return wrapper

    def _wrap_generate_content_async(self, original_func):
        """Wrap async generate_content method"""
        patcher = self

        @functools.wraps(original_func)
        async def wrapper(self_model, *args, **kwargs):
            # RECURSION GUARD: Skip capture if inside Scope internal code
            if ScopeContext.is_in_scope_context():
                return await original_func(self_model, *args, **kwargs)

            start_time = time.time()

            prompt = args[0] if args else kwargs.get('contents', '')

            try:
                if kwargs.get('stream', False):
                    response = await original_func(self_model, *args, **kwargs)
                    return patcher._wrap_async_streaming_response(response, start_time, self_model, prompt)
                else:
                    response = await original_func(self_model, *args, **kwargs)
                    latency_ms = (time.time() - start_time) * 1000
                    patcher._capture_response(response, self_model, prompt, latency_ms)
                    return response

            except Exception as e:
                latency_ms = (time.time() - start_time) * 1000
                patcher._capture_error(self_model, prompt, str(e), latency_ms)
                raise

        return wrapper

    def _wrap_start_chat(self, original_func):
        """Wrap start_chat to return wrapped ChatSession"""
        patcher = self

        @functools.wraps(original_func)
        def wrapper(self_model, *args, **kwargs):
            chat = original_func(self_model, *args, **kwargs)

            # Wrap send_message
            if hasattr(chat, 'send_message'):
                original_send = chat.send_message
                chat.send_message = patcher._wrap_send_message(original_send, self_model)

            # Wrap send_message_async
            if hasattr(chat, 'send_message_async'):
                original_send_async = chat.send_message_async
                chat.send_message_async = patcher._wrap_send_message_async(original_send_async, self_model)

            return chat

        return wrapper

    def _wrap_send_message(self, original_func, model):
        """Wrap ChatSession.send_message"""
        patcher = self

        @functools.wraps(original_func)
        def wrapper(*args, **kwargs):
            # RECURSION GUARD: Skip capture if inside Scope internal code
            if ScopeContext.is_in_scope_context():
                return original_func(*args, **kwargs)

            start_time = time.time()

            prompt = args[0] if args else kwargs.get('content', '')

            try:
                if kwargs.get('stream', False):
                    response = original_func(*args, **kwargs)
                    return patcher._wrap_streaming_response(response, start_time, model, prompt)
                else:
                    response = original_func(*args, **kwargs)
                    latency_ms = (time.time() - start_time) * 1000
                    patcher._capture_response(response, model, prompt, latency_ms)
                    return response

            except Exception as e:
                latency_ms = (time.time() - start_time) * 1000
                patcher._capture_error(model, prompt, str(e), latency_ms)
                raise

        return wrapper

    def _wrap_send_message_async(self, original_func, model):
        """Wrap ChatSession.send_message_async"""
        patcher = self

        @functools.wraps(original_func)
        async def wrapper(*args, **kwargs):
            # RECURSION GUARD: Skip capture if inside Scope internal code
            if ScopeContext.is_in_scope_context():
                return await original_func(*args, **kwargs)

            start_time = time.time()

            prompt = args[0] if args else kwargs.get('content', '')

            try:
                if kwargs.get('stream', False):
                    response = await original_func(*args, **kwargs)
                    return patcher._wrap_async_streaming_response(response, start_time, model, prompt)
                else:
                    response = await original_func(*args, **kwargs)
                    latency_ms = (time.time() - start_time) * 1000
                    patcher._capture_response(response, model, prompt, latency_ms)
                    return response

            except Exception as e:
                latency_ms = (time.time() - start_time) * 1000
                patcher._capture_error(model, prompt, str(e), latency_ms)
                raise

        return wrapper

    def _wrap_streaming_response(self, response, start_time, model, prompt):
        """Wrap sync streaming response"""
        chunks = []

        for chunk in response:
            chunks.append(chunk)
            yield chunk

        latency_ms = (time.time() - start_time) * 1000
        self._capture_streaming_response(chunks, model, prompt, latency_ms)

    async def _wrap_async_streaming_response(self, response, start_time, model, prompt):
        """Wrap async streaming response"""
        chunks = []

        async for chunk in response:
            chunks.append(chunk)
            yield chunk

        latency_ms = (time.time() - start_time) * 1000
        self._capture_streaming_response(chunks, model, prompt, latency_ms)

    def _capture_response(self, response, model, prompt, latency_ms):
        """Capture non-streaming Gemini response"""
        try:
            # Extract model name
            model_name = getattr(model, 'model_name', 'gemini')
            if model_name.startswith('models/'):
                model_name = model_name[7:]  # Remove 'models/' prefix

            # Format prompt as messages
            messages = self._format_prompt_as_messages(prompt)

            # Extract response text
            response_text = ""
            if hasattr(response, 'text'):
                response_text = response.text
            elif hasattr(response, 'candidates') and len(response.candidates) > 0:
                candidate = response.candidates[0]
                if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                    for part in candidate.content.parts:
                        if hasattr(part, 'text'):
                            response_text += part.text

            # Extract token usage
            tokens = {}
            if hasattr(response, 'usage_metadata'):
                usage = response.usage_metadata
                tokens = {
                    'prompt_tokens': getattr(usage, 'prompt_token_count', 0),
                    'completion_tokens': getattr(usage, 'candidates_token_count', 0),
                    'total_tokens': getattr(usage, 'total_token_count', 0),
                }

            # Format and queue event
            event = self.event_formatter.format_llm_call(
                provider='google',
                model=model_name,
                messages=messages,
                response=response_text,
                tokens=tokens,
                latency_ms=latency_ms,
                error=None,
            )

            self.queue.enqueue(event)
            self.config.log(f"Captured Gemini call: {model_name}")

        except Exception as e:
            self.config.log(f"⚠️ Failed to capture Gemini response: {e}")

    def _capture_streaming_response(self, chunks, model, prompt, latency_ms):
        """Capture streaming Gemini response"""
        try:
            model_name = getattr(model, 'model_name', 'gemini')
            if model_name.startswith('models/'):
                model_name = model_name[7:]

            messages = self._format_prompt_as_messages(prompt)

            # Combine chunks
            response_text = ""
            for chunk in chunks:
                if hasattr(chunk, 'text'):
                    response_text += chunk.text
                elif hasattr(chunk, 'candidates') and len(chunk.candidates) > 0:
                    candidate = chunk.candidates[0]
                    if hasattr(candidate, 'content') and hasattr(candidate.content, 'parts'):
                        for part in candidate.content.parts:
                            if hasattr(part, 'text'):
                                response_text += part.text

            # Format and queue event
            event = self.event_formatter.format_llm_call(
                provider='google',
                model=model_name,
                messages=messages,
                response=response_text,
                tokens={},
                latency_ms=latency_ms,
                error=None,
            )

            self.queue.enqueue(event)
            self.config.log(f"Captured Gemini streaming call: {model_name}")

        except Exception as e:
            self.config.log(f"⚠️ Failed to capture Gemini streaming response: {e}")

    def _capture_error(self, model, prompt, error_message, latency_ms):
        """Capture failed LLM call"""
        try:
            model_name = getattr(model, 'model_name', 'gemini')
            if model_name.startswith('models/'):
                model_name = model_name[7:]

            messages = self._format_prompt_as_messages(prompt)

            event = self.event_formatter.format_llm_call(
                provider='google',
                model=model_name,
                messages=messages,
                response="",
                tokens={},
                latency_ms=latency_ms,
                error=error_message,
            )

            self.queue.enqueue(event)
            self.config.log(f"Captured Gemini error: {error_message}")

        except Exception as e:
            self.config.log(f"⚠️ Failed to capture Gemini error: {e}")

    def _format_prompt_as_messages(self, prompt) -> list:
        """Format prompt into messages format for consistency"""
        if isinstance(prompt, str):
            return [{"role": "user", "content": prompt}]
        elif isinstance(prompt, list):
            # Handle list of content parts
            messages = []
            for item in prompt:
                if isinstance(item, str):
                    messages.append({"role": "user", "content": item})
                elif hasattr(item, 'text'):
                    messages.append({"role": "user", "content": item.text})
                elif isinstance(item, dict):
                    messages.append(item)
            return messages
        else:
            # Try to extract text
            if hasattr(prompt, 'text'):
                return [{"role": "user", "content": prompt.text}]
            return [{"role": "user", "content": str(prompt)}]
