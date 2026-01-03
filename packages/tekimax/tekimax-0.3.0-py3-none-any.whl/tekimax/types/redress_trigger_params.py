# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal, Required, TypedDict

__all__ = ["RedressTriggerParams"]


class RedressTriggerParams(TypedDict, total=False):
    reason: Required[Literal["cognitive_overload", "hallucination", "tonal_incompatibility"]]

    request_id: Required[str]

    suggested_modality: str

    user_comment: str
