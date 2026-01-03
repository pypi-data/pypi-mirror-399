# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal

import httpx

from ..types import agent_orchestrate_params
from .._types import Body, Omit, Query, Headers, NotGiven, omit, not_given
from .._utils import maybe_transform, async_maybe_transform
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.agent_list_tools_response import AgentListToolsResponse
from ..types.agent_orchestrate_response import AgentOrchestrateResponse

__all__ = ["AgentResource", "AsyncAgentResource"]


class AgentResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AgentResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TEKIMAX/tekimax-python#accessing-raw-response-data-eg-headers
        """
        return AgentResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AgentResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TEKIMAX/tekimax-python#with_streaming_response
        """
        return AgentResourceWithStreamingResponse(self)

    def list_tools(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AgentListToolsResponse:
        """Returns all available tools that the agent orchestrator can invoke."""
        return self._get(
            "/v1/agent/tools",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AgentListToolsResponse,
        )

    def orchestrate(
        self,
        *,
        query: str,
        organization_id: str | Omit = omit,
        preferred_modality: Literal["visual", "auditory", "textual"] | Omit = omit,
        user_context: object | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AgentOrchestrateResponse:
        """
        FunctionGemma-style intelligent orchestrator that analyzes user queries and
        automatically selects and invokes the appropriate API endpoint. Organizations
        can use this as a single entry point for all platform capabilities.

        Args:
          query: Natural language query from the user

          organization_id: Optional organization identifier for multi-tenant routing

          user_context: Optional context about the user's session

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v1/agent/orchestrate",
            body=maybe_transform(
                {
                    "query": query,
                    "organization_id": organization_id,
                    "preferred_modality": preferred_modality,
                    "user_context": user_context,
                },
                agent_orchestrate_params.AgentOrchestrateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AgentOrchestrateResponse,
        )


class AsyncAgentResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncAgentResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TEKIMAX/tekimax-python#accessing-raw-response-data-eg-headers
        """
        return AsyncAgentResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncAgentResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TEKIMAX/tekimax-python#with_streaming_response
        """
        return AsyncAgentResourceWithStreamingResponse(self)

    async def list_tools(
        self,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AgentListToolsResponse:
        """Returns all available tools that the agent orchestrator can invoke."""
        return await self._get(
            "/v1/agent/tools",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AgentListToolsResponse,
        )

    async def orchestrate(
        self,
        *,
        query: str,
        organization_id: str | Omit = omit,
        preferred_modality: Literal["visual", "auditory", "textual"] | Omit = omit,
        user_context: object | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AgentOrchestrateResponse:
        """
        FunctionGemma-style intelligent orchestrator that analyzes user queries and
        automatically selects and invokes the appropriate API endpoint. Organizations
        can use this as a single entry point for all platform capabilities.

        Args:
          query: Natural language query from the user

          organization_id: Optional organization identifier for multi-tenant routing

          user_context: Optional context about the user's session

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v1/agent/orchestrate",
            body=await async_maybe_transform(
                {
                    "query": query,
                    "organization_id": organization_id,
                    "preferred_modality": preferred_modality,
                    "user_context": user_context,
                },
                agent_orchestrate_params.AgentOrchestrateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=AgentOrchestrateResponse,
        )


class AgentResourceWithRawResponse:
    def __init__(self, agent: AgentResource) -> None:
        self._agent = agent

        self.list_tools = to_raw_response_wrapper(
            agent.list_tools,
        )
        self.orchestrate = to_raw_response_wrapper(
            agent.orchestrate,
        )


class AsyncAgentResourceWithRawResponse:
    def __init__(self, agent: AsyncAgentResource) -> None:
        self._agent = agent

        self.list_tools = async_to_raw_response_wrapper(
            agent.list_tools,
        )
        self.orchestrate = async_to_raw_response_wrapper(
            agent.orchestrate,
        )


class AgentResourceWithStreamingResponse:
    def __init__(self, agent: AgentResource) -> None:
        self._agent = agent

        self.list_tools = to_streamed_response_wrapper(
            agent.list_tools,
        )
        self.orchestrate = to_streamed_response_wrapper(
            agent.orchestrate,
        )


class AsyncAgentResourceWithStreamingResponse:
    def __init__(self, agent: AsyncAgentResource) -> None:
        self._agent = agent

        self.list_tools = async_to_streamed_response_wrapper(
            agent.list_tools,
        )
        self.orchestrate = async_to_streamed_response_wrapper(
            agent.orchestrate,
        )
