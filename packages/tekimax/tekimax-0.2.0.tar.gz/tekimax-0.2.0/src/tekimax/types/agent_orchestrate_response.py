# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from typing import Optional

from .._models import BaseModel

__all__ = ["AgentOrchestrateResponse"]


class AgentOrchestrateResponse(BaseModel):
    natural_response: Optional[str] = None

    query: Optional[str] = None

    reasoning: Optional[str] = None

    result: Optional[object] = None

    selected_tool: Optional[str] = None

    tool_parameters: Optional[object] = None
