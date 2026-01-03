# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["StreamLearningContentCreateParams", "ModalityContext"]


class StreamLearningContentCreateParams(TypedDict, total=False):
    modality_context: Required[ModalityContext]

    prompt: Required[str]
    """The learning query or topic"""

    provenance_enabled: bool


class ModalityContext(TypedDict, total=False):
    support_level: Literal["standard", "high_support"]
    """Level of accommodation/simplification"""

    type: Literal["visual", "auditory", "textual"]
    """Cognitive modality preference"""
