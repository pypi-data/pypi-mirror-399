# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Literal, Required, TypedDict

__all__ = ["UserAutoDetectModalityProfileParams", "InteractionHistory"]


class UserAutoDetectModalityProfileParams(TypedDict, total=False):
    interaction_history: Required[Iterable[InteractionHistory]]
    """Array of past interactions used for modality detection"""

    user_id: Required[str]
    """Unique identifier for the user"""

    preferred_modality_override: Literal["visual", "auditory", "textual"]
    """Optional manual override by the user.

    When provided, this takes precedence over algorithmic recommendations. Used for
    accessibility preferences or user-stated preferences.
    """


class InteractionHistory(TypedDict, total=False):
    completion_status: str
    """Whether user completed the content (completed, abandoned, skipped)"""

    content_type_offered: str
    """Type of content shown (visual, auditory, textual)"""

    engagement_duration: int
    """Time in seconds user engaged with content"""

    interaction_id: str
    """Unique ID of the past interaction"""

    user_feedback_rating: int
    """User rating 1-5 (optional)"""
