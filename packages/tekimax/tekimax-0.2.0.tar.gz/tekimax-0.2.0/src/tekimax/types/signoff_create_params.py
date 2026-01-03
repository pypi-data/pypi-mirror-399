# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["SignoffCreateParams"]


class SignoffCreateParams(TypedDict, total=False):
    action: Required[Literal["verify_and_accept", "reject"]]

    interaction_id: Required[str]

    attestation_comment: str
