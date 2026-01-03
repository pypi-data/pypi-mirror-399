# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel

__all__ = ["SignoffCreateResponse"]


class SignoffCreateResponse(BaseModel):
    action: Optional[str] = None
    """Action taken (verify_and_accept or reject)"""

    compliance_status: Optional[str] = None
    """Compliance status after signoff (compliant, pending_review, rejected)"""

    human_signoff_id: Optional[str] = None
    """Unique ID of this signoff record"""

    interaction_id: Optional[str] = None
    """The reviewed interaction ID"""

    logged_at: Optional[str] = None
    """ISO 8601 timestamp of the signoff"""
