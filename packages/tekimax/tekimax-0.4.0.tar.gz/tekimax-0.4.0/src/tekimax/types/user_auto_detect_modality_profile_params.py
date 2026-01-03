# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Literal, Required, TypedDict

__all__ = ["UserAutoDetectModalityProfileParams", "InteractionHistory"]


class UserAutoDetectModalityProfileParams(TypedDict, total=False):
    interaction_history: Required[Iterable[InteractionHistory]]

    user_id: Required[str]

    preferred_modality_override: Literal["visual", "auditory", "textual"]
    """Optional manual override by the user"""


class InteractionHistory(TypedDict, total=False):
    completion_status: str

    content_type_offered: str

    engagement_duration: int

    interaction_id: str

    user_feedback_rating: int
