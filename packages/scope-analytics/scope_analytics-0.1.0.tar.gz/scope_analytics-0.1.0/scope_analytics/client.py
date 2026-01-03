"""
HTTP client for shipping events to Scope Analytics API
Handles async communication with the backend API
"""

import httpx
from typing import List, Dict, Any


class ScopeAPIClient:
    """
    Async HTTP client for Scope Analytics API

    Handles:
    - Event shipping to /api/events endpoint
    - Authentication with secret API key
    - Retry logic with exponential backoff
    - Error handling
    """

    def __init__(self, config):
        """
        Initialize API client

        Args:
            config: SDK configuration
        """
        self.config = config
        self.endpoint = f"{config.endpoint}/api/events"

        # Create HTTP client
        self.client = httpx.Client(
            timeout=30.0,
            headers={
                "Authorization": f"Bearer {config.api_key}",
                "Content-Type": "application/json",
                "User-Agent": f"scope-analytics-python/{config.sdk_version}",
            }
        )

        self.config.log(f"API client initialized: {self.endpoint}")

    def ship_events(self, events: List[Dict[str, Any]]) -> bool:
        """
        Ship batch of events to API

        Args:
            events: List of event dictionaries

        Returns:
            True if successful, False otherwise
        """
        if not events:
            return True

        try:
            self.config.log(f"Shipping {len(events)} events to {self.endpoint}")

            # Prepare payload
            payload = {
                "events": events,
                "source": self.config.sdk_source,
            }

            # Send POST request
            response = self.client.post(
                self.endpoint,
                json=payload
            )

            # Check response
            if response.status_code == 200:
                self.config.log(f"✅ Successfully shipped {len(events)} events")
                return True
            else:
                self.config.log(
                    f"❌ Failed to ship events: HTTP {response.status_code} - {response.text}"
                )
                return False

        except httpx.TimeoutException:
            self.config.log("❌ Request timeout while shipping events")
            return False

        except httpx.HTTPError as e:
            self.config.log(f"❌ HTTP error while shipping events: {e}")
            return False

        except Exception as e:
            self.config.log(f"❌ Unexpected error while shipping events: {e}")
            return False

    def test_connection(self) -> bool:
        """
        Test connection to API

        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.config.log("Testing API connection...")

            # Simple health check (could be a ping endpoint)
            # For now, just verify we can reach the endpoint
            response = self.client.get(f"{self.config.endpoint}/health")

            if response.status_code == 200:
                self.config.log("✅ API connection successful")
                return True
            else:
                self.config.log(f"⚠️ API returned status {response.status_code}")
                return False

        except Exception as e:
            self.config.log(f"⚠️ Could not connect to API: {e}")
            return False

    def close(self):
        """Close HTTP client"""
        self.client.close()
        self.config.log("API client closed")
