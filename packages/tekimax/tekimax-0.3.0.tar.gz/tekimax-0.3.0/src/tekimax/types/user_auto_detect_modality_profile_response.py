# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["UserAutoDetectModalityProfileResponse"]


class UserAutoDetectModalityProfileResponse(BaseModel):
    adaptation_reasoning: Optional[str] = None

    confidence_score: Optional[float] = None

    recommended_modality: Optional[Literal["visual", "auditory", "textual"]] = None

    user_id: Optional[str] = None
