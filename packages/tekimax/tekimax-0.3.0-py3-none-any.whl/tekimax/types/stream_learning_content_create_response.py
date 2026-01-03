# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel

__all__ = ["StreamLearningContentCreateResponse", "Metadata", "MetadataSupervisoryCheck"]


class MetadataSupervisoryCheck(BaseModel):
    """Safety verification by secondary AI model"""

    checked_by: Optional[str] = None

    status: Optional[str] = None

    timestamp: Optional[str] = None


class Metadata(BaseModel):
    c2pa: Optional[str] = None

    source: Optional[str] = None

    supervisory_check: Optional[MetadataSupervisoryCheck] = None
    """Safety verification by secondary AI model"""


class StreamLearningContentCreateResponse(BaseModel):
    chunk: Optional[str] = None
    """Generated content"""

    metadata: Optional[Metadata] = None
