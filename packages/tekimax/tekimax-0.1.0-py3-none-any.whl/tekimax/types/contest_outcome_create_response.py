# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["ContestOutcomeCreateResponse"]


class ContestOutcomeCreateResponse(BaseModel):
    resolution_eta: Optional[str] = None

    status: Optional[Literal["logged", "escalated_to_human", "auto_resolved"]] = None

    ticket_id: Optional[str] = None
