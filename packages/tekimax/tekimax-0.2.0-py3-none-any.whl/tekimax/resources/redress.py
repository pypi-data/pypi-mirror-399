# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal

import httpx

from ..types import redress_trigger_params
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
from ..types.redress_trigger_response import RedressTriggerResponse

__all__ = ["RedressResource", "AsyncRedressResource"]


class RedressResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> RedressResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TEKIMAX/tekimax-python#accessing-raw-response-data-eg-headers
        """
        return RedressResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> RedressResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TEKIMAX/tekimax-python#with_streaming_response
        """
        return RedressResourceWithStreamingResponse(self)

    def trigger(
        self,
        *,
        reason: Literal["cognitive_overload", "hallucination", "tonal_incompatibility"],
        request_id: str,
        suggested_modality: str | Omit = omit,
        user_comment: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RedressTriggerResponse:
        """
        Triggers modality pivot or redress action for cognitive accessibility.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v1/redress/trigger",
            body=maybe_transform(
                {
                    "reason": reason,
                    "request_id": request_id,
                    "suggested_modality": suggested_modality,
                    "user_comment": user_comment,
                },
                redress_trigger_params.RedressTriggerParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RedressTriggerResponse,
        )


class AsyncRedressResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncRedressResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TEKIMAX/tekimax-python#accessing-raw-response-data-eg-headers
        """
        return AsyncRedressResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncRedressResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TEKIMAX/tekimax-python#with_streaming_response
        """
        return AsyncRedressResourceWithStreamingResponse(self)

    async def trigger(
        self,
        *,
        reason: Literal["cognitive_overload", "hallucination", "tonal_incompatibility"],
        request_id: str,
        suggested_modality: str | Omit = omit,
        user_comment: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> RedressTriggerResponse:
        """
        Triggers modality pivot or redress action for cognitive accessibility.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v1/redress/trigger",
            body=await async_maybe_transform(
                {
                    "reason": reason,
                    "request_id": request_id,
                    "suggested_modality": suggested_modality,
                    "user_comment": user_comment,
                },
                redress_trigger_params.RedressTriggerParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=RedressTriggerResponse,
        )


class RedressResourceWithRawResponse:
    def __init__(self, redress: RedressResource) -> None:
        self._redress = redress

        self.trigger = to_raw_response_wrapper(
            redress.trigger,
        )


class AsyncRedressResourceWithRawResponse:
    def __init__(self, redress: AsyncRedressResource) -> None:
        self._redress = redress

        self.trigger = async_to_raw_response_wrapper(
            redress.trigger,
        )


class RedressResourceWithStreamingResponse:
    def __init__(self, redress: RedressResource) -> None:
        self._redress = redress

        self.trigger = to_streamed_response_wrapper(
            redress.trigger,
        )


class AsyncRedressResourceWithStreamingResponse:
    def __init__(self, redress: AsyncRedressResource) -> None:
        self._redress = redress

        self.trigger = async_to_streamed_response_wrapper(
            redress.trigger,
        )
