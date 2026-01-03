# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel

__all__ = ["StreamLearningContentCreateResponse", "Metadata", "MetadataSupervisoryCheck"]


class MetadataSupervisoryCheck(BaseModel):
    """Results from the secondary AI model safety verification"""

    checked_by: Optional[str] = None
    """Model used for verification"""

    status: Optional[str] = None
    """Verification result ("verified" | "flagged" | "error")"""

    timestamp: Optional[str] = None
    """ISO 8601 timestamp of verification"""


class Metadata(BaseModel):
    """Content provenance and verification metadata"""

    c2pa: Optional[str] = None
    """C2PA signature status ("signed" | "unsigned")"""

    complexity_level: Optional[str] = None
    """Applied complexity level ("standard" | "simplified" | "advanced")"""

    source: Optional[str] = None
    """Model source identifier (e.g., "vertex-gemini-2.0-flash-exp")"""

    supervisory_check: Optional[MetadataSupervisoryCheck] = None
    """Results from the secondary AI model safety verification"""


class StreamLearningContentCreateResponse(BaseModel):
    chunk: Optional[str] = None
    """The generated content adapted to the requested modality"""

    metadata: Optional[Metadata] = None
    """Content provenance and verification metadata"""
