"""Tests for SDK models."""

import pytest
from pydantic import ValidationError

from graedin_cline.models import ClassificationRequest, ClassificationResult


def test_classification_request_valid():
    """Test creating a valid classification request."""
    request = ClassificationRequest(prompt="Test prompt")
    assert request.prompt == "Test prompt"
    assert request.metadata is None


def test_classification_request_with_metadata():
    """Test classification request with metadata."""
    metadata = {"user_id": "123", "session_id": "abc"}
    request = ClassificationRequest(prompt="Test prompt", metadata=metadata)
    assert request.metadata == metadata


def test_classification_request_missing_prompt():
    """Test that prompt is required."""
    with pytest.raises(ValidationError):
        ClassificationRequest()


def test_classification_result_valid():
    """Test creating a valid classification result."""
    result = ClassificationResult(
        is_safe=True, attack_type="safe", reason="No threat detected", confidence=0.95
    )
    assert result.is_safe is True
    assert result.attack_type == "safe"
    assert result.confidence == 0.95


def test_classification_result_confidence_bounds():
    """Test confidence score validation."""
    # Valid confidence
    result = ClassificationResult(is_safe=True, attack_type="safe", reason="Test", confidence=0.5)
    assert result.confidence == 0.5

    # Test boundary values
    result = ClassificationResult(is_safe=True, attack_type="safe", reason="Test", confidence=0.0)
    assert result.confidence == 0.0

    result = ClassificationResult(is_safe=True, attack_type="safe", reason="Test", confidence=1.0)
    assert result.confidence == 1.0

    # Invalid confidence - too low
    with pytest.raises(ValidationError):
        ClassificationResult(is_safe=True, attack_type="safe", reason="Test", confidence=-0.1)

    # Invalid confidence - too high
    with pytest.raises(ValidationError):
        ClassificationResult(is_safe=True, attack_type="safe", reason="Test", confidence=1.1)


def test_classification_result_extra_fields():
    """Test that extra fields are allowed in results."""
    result = ClassificationResult(
        is_safe=True,
        attack_type="safe",
        reason="Test",
        confidence=0.95,
        extra_field="allowed",
    )
    assert result.is_safe is True
