# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["ContestOutcomeCreateParams"]


class ContestOutcomeCreateParams(TypedDict, total=False):
    contestation_reason: Required[Literal["factual_error", "bias_detected", "modality_mismatch", "hallucination"]]

    correction_text: Required[str]
    """User's proposed correction"""

    interaction_id: Required[str]
    """ID of the AI response being contested"""
