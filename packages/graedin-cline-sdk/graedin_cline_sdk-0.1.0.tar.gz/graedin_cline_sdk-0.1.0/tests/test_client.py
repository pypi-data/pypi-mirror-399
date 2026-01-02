"""Tests for synchronous client."""

from unittest.mock import MagicMock, patch

import pytest
import requests

from graedin_cline.client import GraedinClient
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
    return GraedinClient(api_key="test-key", base_url="http://test.local")


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


def test_client_initialization():
    """Test client initialization."""
    client = GraedinClient(api_key="test-key", base_url="http://test.local")
    assert client.api_key == "test-key"
    assert client.base_url == "http://test.local"
    assert client.timeout == 10.0
    assert client.max_retries == 3
    assert client.fail_secure is True


def test_client_initialization_no_api_key():
    """Test that API key is required."""
    with pytest.raises(ValidationError, match="API key is required"):
        GraedinClient(api_key="")


def test_context_manager(client):
    """Test client as context manager."""
    with client as c:
        assert c is client
    # Session should be closed after exit


def test_check_prompt_success(client, mock_response):
    """Test successful prompt check."""
    with patch.object(requests.Session, "post", return_value=mock_response):
        result = client.check_prompt("Test prompt")
        assert isinstance(result, ClassificationResult)
        assert result.is_safe is True
        assert result.attack_type == "safe"


def test_check_prompt_with_metadata(client, mock_response):
    """Test prompt check with metadata."""
    metadata = {"user_id": "123"}
    with patch.object(requests.Session, "post", return_value=mock_response):
        result = client.check_prompt("Test prompt", metadata=metadata)
        assert isinstance(result, ClassificationResult)


def test_check_prompt_empty_prompt(client):
    """Test that empty prompt raises error."""
    with pytest.raises(ValidationError, match="Prompt cannot be empty"):
        client.check_prompt("")


def test_check_prompt_authentication_error(client):
    """Test authentication error handling."""
    mock_response = MagicMock()
    mock_response.status_code = 401

    with patch.object(requests.Session, "post", return_value=mock_response):
        with pytest.raises(AuthenticationError, match="Invalid API key"):
            client.check_prompt("Test prompt")


def test_check_prompt_rate_limit_error(client):
    """Test rate limit error handling."""
    mock_response = MagicMock()
    mock_response.status_code = 429
    mock_response.headers = {"Retry-After": "60"}

    with patch.object(requests.Session, "post", return_value=mock_response):
        with pytest.raises(RateLimitError, match="Rate limit exceeded"):
            client.check_prompt("Test prompt")


def test_check_prompt_timeout_with_retries(client, mock_response):
    """Test timeout with successful retry."""
    # First two calls timeout, third succeeds
    with patch.object(
        requests.Session,
        "post",
        side_effect=[
            requests.exceptions.Timeout("Timeout"),
            requests.exceptions.Timeout("Timeout"),
            mock_response,
        ],
    ):
        result = client.check_prompt("Test prompt")
        assert isinstance(result, ClassificationResult)


def test_check_prompt_timeout_fail_secure(client):
    """Test timeout with fail-secure mode."""
    client.fail_secure = True

    with patch.object(requests.Session, "post", side_effect=requests.exceptions.Timeout("Timeout")):
        result = client.check_prompt("Test prompt")
        assert result.is_safe is False
        assert result.attack_type == "system.fail_secure"
        assert "timed out" in result.reason.lower()


def test_check_prompt_timeout_no_fail_secure(client):
    """Test timeout without fail-secure mode."""
    client.fail_secure = False

    with patch.object(requests.Session, "post", side_effect=requests.exceptions.Timeout("Timeout")):
        with pytest.raises(GraedinTimeoutError, match="timed out"):
            client.check_prompt("Test prompt")


def test_check_prompt_server_error_with_retry(client, mock_response):
    """Test server error with successful retry."""
    error_response = MagicMock()
    error_response.status_code = 503
    error_response.text = "Service unavailable"

    # First call fails, second succeeds
    with patch.object(requests.Session, "post", side_effect=[error_response, mock_response]):
        result = client.check_prompt("Test prompt")
        assert isinstance(result, ClassificationResult)


def test_check_prompt_server_error_fail_secure(client):
    """Test server error with fail-secure mode."""
    client.fail_secure = True
    error_response = MagicMock()
    error_response.status_code = 500
    error_response.text = "Internal server error"

    with patch.object(requests.Session, "post", return_value=error_response):
        result = client.check_prompt("Test prompt")
        assert result.is_safe is False
        assert result.attack_type == "system.fail_secure"


def test_check_prompt_client_error_no_retry(client):
    """Test that 4xx errors are not retried."""
    error_response = MagicMock()
    error_response.status_code = 400
    error_response.text = "Bad request"

    mock_post = MagicMock(return_value=error_response)

    with patch.object(requests.Session, "post", mock_post):
        with pytest.raises(APIError, match="API error 400"):
            client.check_prompt("Test prompt")

        # Should only be called once (no retries for 4xx)
        assert mock_post.call_count == 1


def test_health_check_success(client):
    """Test successful health check."""
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {"status": "healthy"}

    with patch.object(requests.Session, "get", return_value=mock_response):
        result = client.health_check()
        assert result["status"] == "healthy"


def test_health_check_failure(client):
    """Test health check failure."""
    with patch.object(
        requests.Session,
        "get",
        side_effect=requests.exceptions.RequestException("Connection failed"),
    ):
        with pytest.raises(APIError, match="Health check failed"):
            client.health_check()


def test_close(client):
    """Test closing the client."""
    client.close()
    # Session should be closed
