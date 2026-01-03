# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel

__all__ = ["ProvenanceRetrieveResponse"]


class ProvenanceRetrieveResponse(BaseModel):
    c2pa_signature: Optional[str] = None
    """C2PA cryptographic signature for content authenticity"""

    created_at: Optional[str] = None
    """ISO 8601 timestamp when content was created"""

    human_agency_score: Optional[float] = None
    """Human oversight score (0-100, higher = more human involvement)"""

    human_to_ai_ratio: Optional[float] = None
    """Ratio of human edits to AI generations (0.0-1.0)"""

    interaction_id: Optional[str] = None
    """The queried interaction ID"""

    origin_chain: Optional[List[str]] = None
    """Ordered list of content modifications and sources"""

    verified: Optional[bool] = None
    """Whether the provenance chain has been verified"""
