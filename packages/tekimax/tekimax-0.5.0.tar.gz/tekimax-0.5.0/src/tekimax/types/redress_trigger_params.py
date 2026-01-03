# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["RedressTriggerParams"]


class RedressTriggerParams(TypedDict, total=False):
    reason: Required[Literal["cognitive_overload", "hallucination", "tonal_incompatibility"]]
    """
    **cognitive_overload** - Content too complex for user
    **hallucination** - AI generated false information
    **tonal_incompatibility** - Tone doesn't match user needs
    """

    request_id: Required[str]
    """ID of the original content request to redress"""

    suggested_modality: Literal["visual", "auditory", "textual"]
    """User's preferred modality for regenerated content"""

    user_comment: str
    """Optional comment explaining the redress request"""
