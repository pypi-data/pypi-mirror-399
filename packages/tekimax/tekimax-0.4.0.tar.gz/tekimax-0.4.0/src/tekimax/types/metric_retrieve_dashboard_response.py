# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional
from typing_extensions import Literal

from .._models import BaseModel

__all__ = ["MetricRetrieveDashboardResponse", "Metric"]


class Metric(BaseModel):
    name: Optional[str] = None

    status: Optional[Literal["ok", "warning", "critical"]] = None

    threshold: Optional[float] = None

    trend: Optional[Literal["up", "down", "stable"]] = None

    value: Optional[float] = None


class MetricRetrieveDashboardResponse(BaseModel):
    alerts: Optional[List[object]] = None

    metrics: Optional[List[Metric]] = None

    period: Optional[str] = None

    timestamp: Optional[str] = None
