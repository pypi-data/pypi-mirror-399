# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel

__all__ = ["SignoffCreateResponse"]


class SignoffCreateResponse(BaseModel):
    action: Optional[str] = None

    compliance_status: Optional[str] = None

    human_signoff_id: Optional[str] = None

    interaction_id: Optional[str] = None

    logged_at: Optional[str] = None
