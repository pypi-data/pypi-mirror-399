# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["ContestOutcomeCreateParams"]


class ContestOutcomeCreateParams(TypedDict, total=False):
    contestation_reason: Required[Literal["factual_error", "bias_detected", "modality_mismatch", "hallucination"]]
    """
    **factual_error** - Incorrect information or facts
    **bias_detected** - Content shows unfair bias
    **modality_mismatch** - Wrong format for user's needs
    **hallucination** - AI fabricated information
    """

    correction_text: Required[str]
    """User's proposed correct version of the content"""

    interaction_id: Required[str]
    """The unique ID of the AI response being contested"""
