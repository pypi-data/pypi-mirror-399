# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["ContestOutcomeCreateResponse"]


class ContestOutcomeCreateResponse(BaseModel):
    resolution_eta: Optional[str] = None
    """Estimated time for resolution (e.g., "24 hours")"""

    status: Optional[Literal["logged", "escalated_to_human", "auto_resolved"]] = None
    """
    **logged** - Recorded for review
    **escalated_to_human** - Sent to human reviewer
    **auto_resolved** - Automatically corrected
    """

    ticket_id: Optional[str] = None
    """Unique ticket ID for tracking this contestation"""
