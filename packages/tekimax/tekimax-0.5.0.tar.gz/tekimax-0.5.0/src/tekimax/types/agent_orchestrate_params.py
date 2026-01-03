# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["AgentOrchestrateParams"]


class AgentOrchestrateParams(TypedDict, total=False):
    query: Required[str]
    """Natural language query from the user"""

    organization_id: str
    """Optional organization identifier for multi-tenant routing"""

    preferred_modality: Literal["visual", "auditory", "textual"]

    user_context: object
    """Optional context about the user's session"""
