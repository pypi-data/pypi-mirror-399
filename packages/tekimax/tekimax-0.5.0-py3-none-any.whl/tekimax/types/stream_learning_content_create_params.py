# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["StreamLearningContentCreateParams", "ModalityContext"]


class StreamLearningContentCreateParams(TypedDict, total=False):
    modality_context: Required[ModalityContext]
    """Cognitive modality preferences for content adaptation"""

    prompt: Required[str]
    """The learning query or topic to generate content for"""

    provenance_enabled: bool
    """Enable C2PA cryptographic provenance signing for the generated content"""

    session_depth: int
    """Number of interactions in current session.

    Used for Dynamic Complexity Adjustment:

    - **depth > 5**: Unlocks advanced technical content
    - **depth ≤ 5**: Standard complexity level
    """


class ModalityContext(TypedDict, total=False):
    """Cognitive modality preferences for content adaptation"""

    support_level: Literal["standard", "high_support"]
    """
    **standard** - Full technical detail and complexity
    **high_support** - Simplified language, bullet points, 2-sentence summaries
    """

    type: Literal["visual", "auditory", "textual"]
    """
    **visual** - Diagrams, charts, spatial representations
    **auditory** - Audio descriptions, conversational tone
    **textual** - Traditional text with structured formatting
    """
