"""
Configuration management for Scope Analytics SDK
"""

import os
from typing import Optional, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class ScopeConfig:
    """Configuration for Scope Analytics SDK"""

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
        redact_patterns: Optional[list] = None,
    ):
        """
        Initialize Scope SDK configuration

        Args:
            api_key: Secret API key (sk_live_... or sk_test_...)
            endpoint: API endpoint URL
            auto_patch: Whether to automatically patch LLM libraries
            batch_size: Number of events to batch before sending
            batch_timeout_seconds: Maximum time to wait before sending partial batch
            max_queue_size: Maximum events to queue (oldest dropped if exceeded)
            debug: Enable debug logging
            environment: Environment name (production, staging, development)
            redact_patterns: List of regex patterns to redact from events
        """
        # API Key - required
        self.api_key = api_key or os.getenv("SCOPE_API_KEY")
        if not self.api_key:
            raise ValueError(
                "API key is required. Pass api_key parameter or set SCOPE_API_KEY environment variable."
            )

        # Validate API key format
        if not (self.api_key.startswith("sk_live_") or self.api_key.startswith("sk_test_")):
            raise ValueError(
                "Invalid API key format. Backend SDK requires secret keys starting with 'sk_live_' or 'sk_test_'."
            )

        # Endpoint
        self.endpoint = endpoint or os.getenv(
            "SCOPE_ENDPOINT",
            "https://api.scopeai.dev"
        )

        # Patching
        self.auto_patch = auto_patch

        # Batching
        self.batch_size = batch_size
        self.batch_timeout_seconds = batch_timeout_seconds
        self.max_queue_size = max_queue_size

        # Environment
        self.debug = debug or os.getenv("SCOPE_DEBUG", "").lower() == "true"
        self.environment = environment or os.getenv("SCOPE_ENVIRONMENT", "production")

        # Privacy
        self.redact_patterns = redact_patterns or [
            r"password\s*=\s*['\"]?([^'\">\s]+)",
            r"api[_-]?key\s*=\s*['\"]?([^'\">\s]+)",
            r"token\s*=\s*['\"]?([^'\">\s]+)",
            r"secret\s*=\s*['\"]?([^'\">\s]+)",
        ]

        # SDK metadata
        self.sdk_version = "0.1.0"
        self.sdk_source = "backend_sdk"

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return {
            "endpoint": self.endpoint,
            "auto_patch": self.auto_patch,
            "batch_size": self.batch_size,
            "batch_timeout_seconds": self.batch_timeout_seconds,
            "max_queue_size": self.max_queue_size,
            "debug": self.debug,
            "environment": self.environment,
            "sdk_version": self.sdk_version,
        }

    def log(self, message: str):
        """Log debug message if debug mode enabled"""
        if self.debug:
            print(f"[Scope SDK] {message}")
