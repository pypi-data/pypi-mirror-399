# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel

__all__ = ["ActivityLogListResponse", "Entry"]


class Entry(BaseModel):
    details: Optional[object] = None

    event_id: Optional[str] = None

    event_type: Optional[str] = None

    interaction_id: Optional[str] = None

    timestamp: Optional[str] = None

    user_id: Optional[str] = None


class ActivityLogListResponse(BaseModel):
    entries: Optional[List[Entry]] = None

    page: Optional[int] = None

    page_size: Optional[int] = None

    total_count: Optional[int] = None
