# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import List, Optional

from .._models import BaseModel

__all__ = ["AgentListToolsResponse", "Tool"]


class Tool(BaseModel):
    description: Optional[str] = None

    name: Optional[str] = None

    parameters: Optional[object] = None

    required: Optional[List[str]] = None


class AgentListToolsResponse(BaseModel):
    count: Optional[int] = None

    tools: Optional[List[Tool]] = None
