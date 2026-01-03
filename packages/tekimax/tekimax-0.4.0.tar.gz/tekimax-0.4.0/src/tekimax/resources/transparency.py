# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from .._types import Body, Query, Headers, NotGiven, not_given
from .._compat import cached_property
from .._resource import SyncAPIResource, AsyncAPIResource
from .._response import (
    to_raw_response_wrapper,
    to_streamed_response_wrapper,
    async_to_raw_response_wrapper,
    async_to_streamed_response_wrapper,
)
from .._base_client import make_request_options
from ..types.transparency_retrieve_response import TransparencyRetrieveResponse

__all__ = ["TransparencyResource", "AsyncTransparencyResource"]


class TransparencyResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> TransparencyResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TEKIMAX/tekimax-python#accessing-raw-response-data-eg-headers
        """
        return TransparencyResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> TransparencyResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TEKIMAX/tekimax-python#with_streaming_response
        """
        return TransparencyResourceWithStreamingResponse(self)

    def retrieve(
        self,
        interaction_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TransparencyRetrieveResponse:
        """
        Returns transparency metadata and dark pattern check for an AI output.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not interaction_id:
            raise ValueError(f"Expected a non-empty value for `interaction_id` but received {interaction_id!r}")
        return self._get(
            f"/v1/transparency/{interaction_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TransparencyRetrieveResponse,
        )


class AsyncTransparencyResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncTransparencyResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TEKIMAX/tekimax-python#accessing-raw-response-data-eg-headers
        """
        return AsyncTransparencyResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncTransparencyResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TEKIMAX/tekimax-python#with_streaming_response
        """
        return AsyncTransparencyResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        interaction_id: str,
        *,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> TransparencyRetrieveResponse:
        """
        Returns transparency metadata and dark pattern check for an AI output.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not interaction_id:
            raise ValueError(f"Expected a non-empty value for `interaction_id` but received {interaction_id!r}")
        return await self._get(
            f"/v1/transparency/{interaction_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=TransparencyRetrieveResponse,
        )


class TransparencyResourceWithRawResponse:
    def __init__(self, transparency: TransparencyResource) -> None:
        self._transparency = transparency

        self.retrieve = to_raw_response_wrapper(
            transparency.retrieve,
        )


class AsyncTransparencyResourceWithRawResponse:
    def __init__(self, transparency: AsyncTransparencyResource) -> None:
        self._transparency = transparency

        self.retrieve = async_to_raw_response_wrapper(
            transparency.retrieve,
        )


class TransparencyResourceWithStreamingResponse:
    def __init__(self, transparency: TransparencyResource) -> None:
        self._transparency = transparency

        self.retrieve = to_streamed_response_wrapper(
            transparency.retrieve,
        )


class AsyncTransparencyResourceWithStreamingResponse:
    def __init__(self, transparency: AsyncTransparencyResource) -> None:
        self._transparency = transparency

        self.retrieve = async_to_streamed_response_wrapper(
            transparency.retrieve,
        )
