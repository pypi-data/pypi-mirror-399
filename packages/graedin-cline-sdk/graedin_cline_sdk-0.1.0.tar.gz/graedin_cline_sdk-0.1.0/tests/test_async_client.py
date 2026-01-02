"""Tests for async client."""

from unittest.mock import AsyncMock, MagicMock, patch

import httpx
import pytest

from graedin_cline.async_client import AsyncGraedinClient
from graedin_cline.exceptions import (
    APIError,
    AuthenticationError,
    RateLimitError,
    ValidationError,
)
from graedin_cline.exceptions import TimeoutError as GraedinTimeoutError
from graedin_cline.models import ClassificationResult


@pytest.fixture
def client():
    """Create a test client."""
    return AsyncGraedinClient(api_key="test-key", base_url="http://test.local")


@pytest.fixture
def mock_response():
    """Create a mock successful response."""
    response = MagicMock()
    response.status_code = 200
    response.json.return_value = {
        "is_safe": True,
        "attack_type": "safe",
        "reason": "No threat detected",
        "confidence": 0.95,
    }
    return response


@pytest.mark.asyncio
async def test_client_initialization():
    """Test client initialization."""
    client = AsyncGraedinClient(api_key="test-key", base_url="http://test.local")
    assert client.api_key == "test-key"
    assert client.base_url == "http://test.local"
    assert client.timeout == 10.0
    assert client.max_retries == 3
    assert client.fail_secure is True


@pytest.mark.asyncio
async def test_client_initialization_no_api_key():
    """Test that API key is required."""
    with pytest.raises(ValidationError, match="API key is required"):
        AsyncGraedinClient(api_key="")


@pytest.mark.asyncio
async def test_context_manager(client):
    """Test client as context manager."""
    async with client as c:
        assert c is client
    assert client._client is None  # Should be closed


@pytest.mark.asyncio
async def test_check_prompt_success(client, mock_response):
    """Test successful prompt check."""
    with patch.object(
        httpx.AsyncClient, "post", new_callable=AsyncMock, return_value=mock_response
    ):
        result = await client.check_prompt("Test prompt")
        assert isinstance(result, ClassificationResult)
        assert result.is_safe is True
        assert result.attack_type == "safe"


@pytest.mark.asyncio
async def test_check_prompt_with_metadata(client, mock_response):
    """Test prompt check with metadata."""
    metadata = {"user_id": "123"}
    with patch.object(
        httpx.AsyncClient, "post", new_callable=AsyncMock, return_value=mock_response
    ):
        result = await client.check_prompt("Test prompt", metadata=metadata)
        assert isinstance(result, ClassificationResult)


@pytest.mark.asyncio
async def test_check_prompt_empty_prompt(client):
    """Test that empty prompt raises error."""
    with pytest.raises(ValidationError, match="Prompt cannot be empty"):
        await client.check_prompt("")


@pytest.mark.asyncio
async def test_check_prompt_authentication_error(client):
    """Test authentication error handling."""
    mock_response = MagicMock()
    mock_response.status_code = 401

    with patch.object(
        httpx.AsyncClient, "post", new_callable=AsyncMock, return_value=mock_response
    ):
        with pytest.raises(AuthenticationError, match="Invalid API key"):
            await client.check_prompt("Test prompt")


@pytest.mark.asyncio
async def test_check_prompt_rate_limit_error(client):
    """Test rate limit error handling."""
    mock_response = MagicMock()
    mock_response.status_code = 429
    mock_response.headers = {"Retry-After": "60"}

    with patch.object(
        httpx.AsyncClient, "post", new_callable=AsyncMock, return_value=mock_response
    ):
        with pytest.raises(RateLimitError, match="Rate limit exceeded"):
            await client.check_prompt("Test prompt")


@pytest.mark.asyncio
async def test_check_prompt_timeout_with_retries(client, mock_response):
    """Test timeout with successful retry."""
    # First two calls timeout, third succeeds
    with patch.object(
        httpx.AsyncClient,
        "post",
        new_callable=AsyncMock,
        side_effect=[
            httpx.TimeoutException("Timeout"),
            httpx.TimeoutException("Timeout"),
            mock_response,
        ],
    ):
        result = await client.check_prompt("Test prompt")
        assert isinstance(result, ClassificationResult)


@pytest.mark.asyncio
async def test_check_prompt_timeout_fail_secure(client):
    """Test timeout with fail-secure mode."""
    client.fail_secure = True

    with patch.object(
        httpx.AsyncClient,
        "post",
        new_callable=AsyncMock,
        side_effect=httpx.TimeoutException("Timeout"),
    ):
        result = await client.check_prompt("Test prompt")
        assert result.is_safe is False
        assert result.attack_type == "system.fail_secure"
        assert "timed out" in result.reason.lower()


@pytest.mark.asyncio
async def test_check_prompt_timeout_no_fail_secure(client):
    """Test timeout without fail-secure mode."""
    client.fail_secure = False

    with patch.object(
        httpx.AsyncClient,
        "post",
        new_callable=AsyncMock,
        side_effect=httpx.TimeoutException("Timeout"),
    ):
        with pytest.raises(GraedinTimeoutError, match="timed out"):
            await client.check_prompt("Test prompt")


@pytest.mark.asyncio
async def test_check_prompt_server_error_with_retry(client, mock_response):
    """Test server error with successful retry."""
    error_response = MagicMock()
    error_response.status_code = 503
    error_response.text = "Service unavailable"

    # First call fails, second succeeds
    with patch.object(
        httpx.AsyncClient,
        "post",
        new_callable=AsyncMock,
        side_effect=[error_response, mock_response],
    ):
        result = await client.check_prompt("Test prompt")
        assert isinstance(result, ClassificationResult)


@pytest.mark.asyncio
async def test_check_prompt_server_error_fail_secure(client):
    """Test server error with fail-secure mode."""
    client.fail_secure = True
    error_response = MagicMock()
    error_response.status_code = 500
    error_response.text = "Internal server error"

    with patch.object(
        httpx.AsyncClient, "post", new_callable=AsyncMock, return_value=error_response
    ):
        result = await client.check_prompt("Test prompt")
        assert result.is_safe is False
        assert result.attack_type == "system.fail_secure"


@pytest.mark.asyncio
async def test_check_prompt_client_error_no_retry(client):
    """Test that 4xx errors are not retried."""
    error_response = MagicMock()
    error_response.status_code = 400
    error_response.text = "Bad request"

    mock_post = AsyncMock(return_value=error_response)

    with patch.object(httpx.AsyncClient, "post", new_callable=lambda: mock_post):
        with pytest.raises(APIError, match="API error 400"):
            await client.check_prompt("Test prompt")

        # Should only be called once (no retries for 4xx)
        assert mock_post.call_count == 1


@pytest.mark.asyncio
async def test_health_check_success(client):
    """Test successful health check."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "healthy"}

    with patch.object(httpx.AsyncClient, "get", new_callable=AsyncMock, return_value=mock_response):
        result = await client.health_check()
        assert result["status"] == "healthy"


@pytest.mark.asyncio
async def test_health_check_failure(client):
    """Test health check failure."""
    with patch.object(
        httpx.AsyncClient,
        "get",
        new_callable=AsyncMock,
        side_effect=httpx.HTTPError("Connection failed"),
    ):
        with pytest.raises(APIError, match="Health check failed"):
            await client.health_check()


@pytest.mark.asyncio
async def test_close(client):
    """Test closing the client."""
    # Create client to initialize httpx client
    _ = client._get_client()
    assert client._client is not None

    await client.close()
    assert client._client is None
