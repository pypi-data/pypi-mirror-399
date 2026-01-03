# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel

__all__ = ["TransparencyRetrieveResponse"]


class TransparencyRetrieveResponse(BaseModel):
    adjustment_reason: Optional[str] = None

    c2pa_verified: Optional[bool] = None

    confidence_score: Optional[float] = None

    dark_pattern_check: Optional[str] = None

    interaction_id: Optional[str] = None

    modality_adjustment: Optional[str] = None

    supervisory_agent_status: Optional[str] = None

    transparency_badge: Optional[str] = None
