"""Pydantic models for Graedin Cline SDK."""

from typing import Optional

from pydantic import BaseModel, Field


class ClassificationRequest(BaseModel):
    """Request model for classification."""

    prompt: str = Field(..., description="The prompt to classify")
    metadata: Optional[dict] = Field(default=None, description="Optional metadata")

    model_config = {"extra": "forbid"}


class ClassificationResult(BaseModel):
    """Result of prompt classification."""

    is_safe: bool = Field(..., description="Whether the prompt is safe to process")
    attack_type: str = Field(..., description="Type of attack detected or 'safe'")
    reason: str = Field(..., description="Explanation of the classification")
    confidence: float = Field(..., description="Confidence score (0.0 to 1.0)", ge=0.0, le=1.0)

    model_config = {"extra": "allow"}  # Allow extra fields for future compatibility
