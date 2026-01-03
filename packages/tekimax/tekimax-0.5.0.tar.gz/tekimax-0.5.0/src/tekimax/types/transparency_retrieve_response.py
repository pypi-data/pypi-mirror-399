# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel

__all__ = ["TransparencyRetrieveResponse"]


class TransparencyRetrieveResponse(BaseModel):
    adjustment_reason: Optional[str] = None
    """Why the adjustment was made"""

    c2pa_verified: Optional[bool] = None

    confidence_score: Optional[float] = None
    """Model confidence in the output (0.0-1.0)"""

    dark_pattern_check: Optional[str] = None

    interaction_id: Optional[str] = None
    """The queried interaction ID"""

    modality_adjustment: Optional[str] = None
    """How content modality was changed (e.g., "visual -> textual")"""

    supervisory_agent_status: Optional[str] = None

    transparency_badge: Optional[str] = None
