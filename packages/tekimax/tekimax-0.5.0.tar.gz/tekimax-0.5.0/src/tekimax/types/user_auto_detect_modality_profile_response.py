# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["UserAutoDetectModalityProfileResponse"]


class UserAutoDetectModalityProfileResponse(BaseModel):
    adaptation_reasoning: Optional[str] = None
    """Human-readable explanation of why this modality was chosen"""

    confidence_score: Optional[float] = None
    """Confidence in recommendation (0.0 to 1.0)"""

    recommended_modality: Optional[Literal["visual", "auditory", "textual"]] = None
    """AI-determined optimal modality for this user"""

    user_id: Optional[str] = None
    """User identifier from request"""
