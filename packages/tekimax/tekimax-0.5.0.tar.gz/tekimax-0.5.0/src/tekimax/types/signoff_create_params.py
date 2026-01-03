# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["SignoffCreateParams"]


class SignoffCreateParams(TypedDict, total=False):
    action: Required[Literal["verify_and_accept", "reject"]]
    """
    **verify_and_accept** - Human approves the AI output
    **reject** - Human rejects the AI output
    """

    interaction_id: Required[str]
    """ID of the AI interaction being reviewed"""

    attestation_comment: str
    """Optional comment explaining the decision"""
