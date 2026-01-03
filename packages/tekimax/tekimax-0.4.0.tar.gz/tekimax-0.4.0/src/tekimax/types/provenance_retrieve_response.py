# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel

__all__ = ["ProvenanceRetrieveResponse"]


class ProvenanceRetrieveResponse(BaseModel):
    c2pa_signature: Optional[str] = None

    created_at: Optional[str] = None

    human_agency_score: Optional[float] = None

    human_to_ai_ratio: Optional[float] = None

    interaction_id: Optional[str] = None

    origin_chain: Optional[List[str]] = None

    verified: Optional[bool] = None
