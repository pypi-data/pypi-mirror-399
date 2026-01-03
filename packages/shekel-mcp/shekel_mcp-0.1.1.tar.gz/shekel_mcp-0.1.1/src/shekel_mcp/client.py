"""
Async HTTP client for Shekel Mobility APIs.

This module provides an async HTTP client that communicates with the
Shekel Mobility REST API endpoints and handles polling for async task completion.
"""

import asyncio
import logging
from typing import Any

import httpx

logger = logging.getLogger(__name__)


class ShekelAPIClient:
    """
    Async HTTP client for Shekel Mobility APIs.

    Handles authentication, request creation, and polling for completion.
    """

    # API endpoints
    ESTIMATE_ENDPOINT = "/api/v1/estimate/"
    CAPTION_ENDPOINT = "/api/v1/caption/"
    OPTIMIZER_ENDPOINT = "/api/v1/listing-optimize/"

    # Polling configuration
    DEFAULT_POLL_INTERVAL = 2  # seconds
    DEFAULT_MAX_ATTEMPTS = 180  # 6 minutes max (180 * 2 seconds)

    def __init__(self, base_url: str, api_key: str):
        """
        Initialize the API client.

        Args:
            base_url: Base URL of the Shekel Mobility API (e.g., https://example.com)
            api_key: API key for authentication
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self._client: httpx.AsyncClient | None = None

    @property
    def headers(self) -> dict[str, str]:
        """Get headers with API key authentication."""
        return {
            "Authorization": f"Api-Key {self.api_key}",
            "Content-Type": "application/json",
        }

    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create the async HTTP client."""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                headers=self.headers,
                timeout=30.0,
            )
        return self._client

    async def close(self):
        """Close the HTTP client."""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    async def create_request(self, endpoint: str, data: dict[str, Any]) -> dict[str, Any]:
        """
        Create a new request (POST).

        Args:
            endpoint: API endpoint (e.g., /api/v1/estimate/)
            data: Request payload

        Returns:
            Response data with request ID and status

        Raises:
            httpx.HTTPStatusError: If the request fails
        """
        client = await self._get_client()
        response = await client.post(endpoint, json=data)
        response.raise_for_status()
        return response.json()

    async def get_status(self, endpoint: str, request_id: str) -> dict[str, Any]:
        """
        Get request status (GET).

        Args:
            endpoint: API endpoint (e.g., /api/v1/estimate/)
            request_id: UUID of the request

        Returns:
            Response data with current status

        Raises:
            httpx.HTTPStatusError: If the request fails
        """
        client = await self._get_client()
        response = await client.get(f"{endpoint}{request_id}/")
        response.raise_for_status()
        return response.json()

    async def poll_until_complete(
        self,
        endpoint: str,
        request_id: str,
        poll_interval: int = DEFAULT_POLL_INTERVAL,
        max_attempts: int = DEFAULT_MAX_ATTEMPTS,
    ) -> dict[str, Any]:
        """
        Poll until request completes or times out.

        Args:
            endpoint: API endpoint
            request_id: UUID of the request
            poll_interval: Seconds between polls
            max_attempts: Maximum number of poll attempts

        Returns:
            Final response data (completed or failed)

        Raises:
            TimeoutError: If max attempts reached
        """
        for attempt in range(max_attempts):
            result = await self.get_status(endpoint, request_id)
            status = result.get("status", "").upper()

            if status in ("COMPLETED", "FAILED"):
                logger.info(f"Request {request_id} completed with status: {status}")
                return result

            logger.debug(f"Request {request_id} status: {status}, attempt {attempt + 1}/{max_attempts}")
            await asyncio.sleep(poll_interval)

        # Timeout - return last status with timeout info
        result = await self.get_status(endpoint, request_id)
        result["_timeout"] = True
        result["_message"] = f"Request timed out after {max_attempts * poll_interval} seconds. Request ID: {request_id}"
        return result

    async def estimate_vehicle(
        self,
        vehicle_name: str,
        year: int,
        condition: str,
        region: str = "Nigeria",
        mileage: int | None = None,
        description: str | None = None,
        source: str = "DEFAULT",
        hard_refresh: bool = False,
    ) -> dict[str, Any]:
        """
        Estimate vehicle price.

        Args:
            vehicle_name: Name of the vehicle (e.g., "Toyota Camry")
            year: Year of manufacture
            condition: "foreign_used" or "local_used"
            region: Region name (default: "Nigeria")
            mileage: Vehicle mileage in km (optional)
            description: Additional vehicle description (optional)
            source: "DEFAULT" or "AUCTION"
            hard_refresh: Bypass cache if True

        Returns:
            Estimation results including price estimates and comparable vehicles
        """
        data = {
            "vehicle_name": vehicle_name,
            "year": year,
            "condition": condition,
            "region": region,
            "source": source,
            "hard_refresh": hard_refresh,
        }

        if mileage is not None:
            data["mileage"] = mileage
        if description:
            data["description"] = description

        # Create request
        create_response = await self.create_request(self.ESTIMATE_ENDPOINT, data)
        request_id = create_response.get("id")

        if not request_id:
            return create_response  # Return immediately if cache hit (HTTP 200)

        # Poll until complete
        return await self.poll_until_complete(self.ESTIMATE_ENDPOINT, request_id)

    async def generate_caption(
        self,
        vehicle_name: str,
        year: int,
        platforms: list[str],
        tone: str = "professional",
        language: str = "English",
        make: str | None = None,
        model: str | None = None,
        condition: str | None = None,
        price: float | None = None,
        currency: str = "NGN",
        variations_per_platform: int = 1,
        hashtag_count: int = 5,
        context_suggestions: str | None = None,
        hard_refresh: bool = False,
    ) -> dict[str, Any]:
        """
        Generate social media captions.

        Args:
            vehicle_name: Name of the vehicle
            year: Year of manufacture
            platforms: List of platforms (facebook, instagram, tiktok, whatsapp)
            tone: Caption tone (professional, casual, urgent, luxury, budget)
            language: Language for captions
            make: Vehicle make (optional)
            model: Vehicle model (optional)
            condition: Vehicle condition (optional)
            price: Vehicle price (optional)
            currency: Currency code (default: NGN)
            variations_per_platform: Number of variations per platform
            hashtag_count: Number of hashtags to generate
            context_suggestions: Additional context for LLM (optional)
            hard_refresh: Bypass cache if True

        Returns:
            Generated captions and hashtags per platform
        """
        data = {
            "vehicle_name": vehicle_name,
            "year": year,
            "platforms": platforms,
            "tone": tone,
            "language": language,
            "currency": currency,
            "variations_per_platform": variations_per_platform,
            "hashtag_count": hashtag_count,
            "hard_refresh": hard_refresh,
        }

        if make:
            data["make"] = make
        if model:
            data["model"] = model
        if condition:
            data["condition"] = condition
        if price is not None:
            data["price"] = price
        if context_suggestions:
            data["context_suggestions"] = context_suggestions

        # Create request
        create_response = await self.create_request(self.CAPTION_ENDPOINT, data)
        request_id = create_response.get("id")

        if not request_id:
            return create_response  # Return immediately if cache hit

        # Poll until complete
        return await self.poll_until_complete(self.CAPTION_ENDPOINT, request_id)

    async def optimize_listing(
        self,
        vehicle_name: str,
        year: int,
        title_count: int = 3,
        include_seo_keywords: bool = True,
        language: str = "English",
        make: str | None = None,
        model: str | None = None,
        condition: str | None = None,
        price: float | None = None,
        currency: str = "NGN",
        description: str | None = None,
        context_suggestions: str | None = None,
        hard_refresh: bool = False,
    ) -> dict[str, Any]:
        """
        Optimize vehicle listing (without images).

        Note: Image upload is not supported via MCP. This will generate
        titles and SEO keywords without image analysis.

        Args:
            vehicle_name: Name of the vehicle
            year: Year of manufacture
            title_count: Number of title suggestions (1-5)
            include_seo_keywords: Whether to include SEO keywords
            language: Language for content
            make: Vehicle make (optional)
            model: Vehicle model (optional)
            condition: Vehicle condition (optional)
            price: Vehicle price (optional)
            currency: Currency code (default: NGN)
            description: Vehicle description (optional)
            context_suggestions: Additional context for LLM (optional)
            hard_refresh: Bypass cache if True

        Returns:
            Generated titles and SEO keywords
        """
        data = {
            "vehicle_name": vehicle_name,
            "year": year,
            "title_count": title_count,
            "include_seo_keywords": include_seo_keywords,
            "language": language,
            "currency": currency,
            "hard_refresh": hard_refresh,
        }

        if make:
            data["make"] = make
        if model:
            data["model"] = model
        if condition:
            data["condition"] = condition
        if price is not None:
            data["price"] = price
        if description:
            data["description"] = description
        if context_suggestions:
            data["context_suggestions"] = context_suggestions

        # Create request
        create_response = await self.create_request(self.OPTIMIZER_ENDPOINT, data)
        request_id = create_response.get("id")

        if not request_id:
            return create_response  # Return immediately if cache hit

        # Poll until complete
        return await self.poll_until_complete(self.OPTIMIZER_ENDPOINT, request_id)
