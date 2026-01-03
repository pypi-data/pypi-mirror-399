# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["RedressTriggerResponse"]


class RedressTriggerResponse(BaseModel):
    action_taken: Optional[Literal["modality_pivot", "human_escalation"]] = None

    audit_tag: Optional[str] = None

    new_content_url: Optional[str] = None

    redress_status: Optional[Literal["completed", "failed"]] = None
