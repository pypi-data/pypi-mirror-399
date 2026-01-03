# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel

__all__ = ["AttributionReportRetrieveResponse"]


class AttributionReportRetrieveResponse(BaseModel):
    ai_generated_tokens: Optional[int] = None

    automated_outputs: Optional[int] = None

    end_date: Optional[str] = None

    human_edited_tokens: Optional[int] = None

    human_signoffs: Optional[int] = None

    human_to_ai_ratio: Optional[float] = None

    modality_breakdown: Optional[object] = None

    period: Optional[str] = None

    start_date: Optional[str] = None

    total_outputs: Optional[int] = None
