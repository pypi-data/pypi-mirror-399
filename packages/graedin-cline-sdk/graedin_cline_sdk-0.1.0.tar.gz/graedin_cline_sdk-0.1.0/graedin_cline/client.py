"""Synchronous client for Graedin Cline API."""

import logging
import time
from typing import Optional

import requests

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


class GraedinClient:
    """Synchronous client for Graedin Cline API with retry logic and fail-secure mode."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "http://localhost:8000",
        timeout: float = 10.0,
        max_retries: int = 3,
        fail_secure: bool = True,
    ):
        """
        Initialize the Graedin client.

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

        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {api_key}",
                "User-Agent": f"graedin-cline-sdk/{__version__}",
                "Content-Type": "application/json",
            }
        )

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    def close(self):
        """Close the session."""
        self.session.close()

    def check_prompt(self, prompt: str, metadata: Optional[dict] = None) -> ClassificationResult:
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
        url = f"{self.base_url}/v1/check_prompt"

        # Retry logic with exponential backoff
        for attempt in range(1, self.max_retries + 1):
            try:
                response = self.session.post(
                    url,
                    json=request_data.model_dump(exclude_none=True),
                    timeout=self.timeout,
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
                        time.sleep(min(2**attempt, 10))  # Exponential backoff
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

            except requests.exceptions.Timeout:
                last_exception = GraedinTimeoutError(f"Request timed out after {self.timeout}s")
                logger.warning(f"Attempt {attempt}/{self.max_retries} timed out")
                if attempt < self.max_retries:
                    time.sleep(min(2**attempt, 10))
                    continue
                break

            except requests.exceptions.HTTPError:
                # Already handled above
                raise

            except requests.exceptions.RequestException as e:
                last_exception = APIError(f"HTTP error: {str(e)}")
                logger.warning(f"Attempt {attempt}/{self.max_retries} failed: {e}")
                if attempt < self.max_retries:
                    time.sleep(min(2**attempt, 10))
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

    def health_check(self) -> dict:
        """
        Check API health status.

        Returns:
            Health status dictionary

        Raises:
            APIError: If health check fails
        """
        try:
            response = self.session.get(f"{self.base_url}/health", timeout=self.timeout)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            raise APIError(f"Health check failed: {str(e)}") from e
