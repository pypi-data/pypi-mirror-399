"""Async client for Graedin Cline API."""

import asyncio
import logging
from typing import Optional

import httpx

from graedin_cline.exceptions import (
    APIError,
    AuthenticationError,
    GraedinError,
    RateLimitError,
    ValidationError,
)
from graedin_cline.exceptions import TimeoutError as GraedinTimeoutError
from graedin_cline.models import ClassificationRequest, ClassificationResult
from graedin_cline.version import __version__

logger = logging.getLogger(__name__)


class AsyncGraedinClient:
    """Async client for Graedin Cline API with retry logic and fail-secure mode."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "http://localhost:8000",
        timeout: float = 10.0,
        max_retries: int = 3,
        fail_secure: bool = True,
    ):
        """
        Initialize the async Graedin client.

        Args:
            api_key: Your Graedin API key
            base_url: Base URL of the Graedin API
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            fail_secure: If True, return "block" response on errors instead of raising
        """
        if not api_key:
            raise ValidationError("API key is required")

        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.max_retries = max_retries
        self.fail_secure = fail_secure

        self._client: Optional[httpx.AsyncClient] = None

    def _get_client(self) -> httpx.AsyncClient:
        """Get or create HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "User-Agent": f"graedin-cline-sdk/{__version__}",
                    "Content-Type": "application/json",
                },
            )
        return self._client

    async def __aenter__(self):
        """Context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        await self.close()

    async def close(self):
        """Close the HTTP client."""
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def check_prompt(
        self, prompt: str, metadata: Optional[dict] = None
    ) -> ClassificationResult:
        """
        Check if a prompt is safe or contains malicious intent.

        Args:
            prompt: The prompt to classify
            metadata: Optional metadata for context

        Returns:
            ClassificationResult with safety determination

        Raises:
            ValidationError: Invalid input
            AuthenticationError: Invalid API key
            RateLimitError: Rate limit exceeded
            TimeoutError: Request timed out
            APIError: Other API errors
            GraedinError: General SDK errors
        """
        if not prompt or not prompt.strip():
            raise ValidationError("Prompt cannot be empty")

        request_data = ClassificationRequest(prompt=prompt, metadata=metadata)

        last_exception: Optional[Exception] = None
        client = self._get_client()

        # Retry logic with exponential backoff
        for attempt in range(1, self.max_retries + 1):
            try:
                response = await client.post(
                    "/v1/check_prompt",
                    json=request_data.model_dump(exclude_none=True),
                )

                # Handle different status codes
                if response.status_code == 401:
                    raise AuthenticationError("Invalid API key")
                elif response.status_code == 429:
                    retry_after = response.headers.get("Retry-After", "60")
                    raise RateLimitError(f"Rate limit exceeded. Retry after {retry_after} seconds")
                elif response.status_code >= 500:
                    error_detail = response.text[:200] if response.text else "Unknown error"
                    last_exception = APIError(f"API error {response.status_code}: {error_detail}")
                    logger.warning(
                        f"Attempt {attempt}/{self.max_retries} failed with status {response.status_code}"
                    )
                    if attempt < self.max_retries:
                        await asyncio.sleep(min(2**attempt, 10))  # Exponential backoff
                        continue
                    break
                elif response.status_code >= 400:
                    # Client error, don't retry
                    error_detail = response.text[:200] if response.text else "Unknown error"
                    raise APIError(f"API error {response.status_code}: {error_detail}")

                response.raise_for_status()

                # Parse and return successful response
                result_data = response.json()
                return ClassificationResult(**result_data)

            except httpx.TimeoutException:
                last_exception = GraedinTimeoutError(f"Request timed out after {self.timeout}s")
                logger.warning(f"Attempt {attempt}/{self.max_retries} timed out")
                if attempt < self.max_retries:
                    await asyncio.sleep(min(2**attempt, 10))
                    continue
                break

            except httpx.HTTPStatusError:
                # Already handled above
                raise

            except httpx.HTTPError as e:
                last_exception = APIError(f"HTTP error: {str(e)}")
                logger.warning(f"Attempt {attempt}/{self.max_retries} failed: {e}")
                if attempt < self.max_retries:
                    await asyncio.sleep(min(2**attempt, 10))
                    continue
                break

            except (AuthenticationError, RateLimitError, ValidationError, APIError):
                # Don't retry these errors
                raise

            except Exception as e:
                last_exception = GraedinError(f"Unexpected error: {str(e)}")
                logger.error(f"Unexpected error on attempt {attempt}: {e}")
                break

        # If we get here, all retries failed
        if self.fail_secure:
            logger.warning("Returning fail-secure response due to errors")
            return ClassificationResult(
                is_safe=False,
                attack_type="system.fail_secure",
                reason=f"Security check failed: {str(last_exception)}",
                confidence=1.0,
            )
        else:
            raise last_exception or GraedinError("All retry attempts failed")

    async def health_check(self) -> dict:
        """
        Check API health status.

        Returns:
            Health status dictionary

        Raises:
            APIError: If health check fails
        """
        client = self._get_client()
        try:
            response = await client.get("/health")
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            raise APIError(f"Health check failed: {str(e)}") from e
