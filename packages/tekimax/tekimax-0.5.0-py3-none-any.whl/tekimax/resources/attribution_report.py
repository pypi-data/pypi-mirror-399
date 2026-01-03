# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal

import httpx

from ..types import attribution_report_retrieve_params
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
from ..types.attribution_report_retrieve_response import AttributionReportRetrieveResponse

__all__ = ["AttributionReportResource", "AsyncAttributionReportResource"]


class AttributionReportResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AttributionReportResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TEKIMAX/tekimax-python#accessing-raw-response-data-eg-headers
        """
        return AttributionReportResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AttributionReportResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TEKIMAX/tekimax-python#with_streaming_response
        """
        return AttributionReportResourceWithStreamingResponse(self)

    def retrieve(
        self,
        *,
        period: Literal["weekly", "monthly"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AttributionReportRetrieveResponse:
        """
        Generates AI Attribution report showing Human-to-AI Ratio.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/v1/attribution-report",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {"period": period}, attribution_report_retrieve_params.AttributionReportRetrieveParams
                ),
            ),
            cast_to=AttributionReportRetrieveResponse,
        )


class AsyncAttributionReportResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncAttributionReportResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TEKIMAX/tekimax-python#accessing-raw-response-data-eg-headers
        """
        return AsyncAttributionReportResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncAttributionReportResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TEKIMAX/tekimax-python#with_streaming_response
        """
        return AsyncAttributionReportResourceWithStreamingResponse(self)

    async def retrieve(
        self,
        *,
        period: Literal["weekly", "monthly"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> AttributionReportRetrieveResponse:
        """
        Generates AI Attribution report showing Human-to-AI Ratio.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/v1/attribution-report",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {"period": period}, attribution_report_retrieve_params.AttributionReportRetrieveParams
                ),
            ),
            cast_to=AttributionReportRetrieveResponse,
        )


class AttributionReportResourceWithRawResponse:
    def __init__(self, attribution_report: AttributionReportResource) -> None:
        self._attribution_report = attribution_report

        self.retrieve = to_raw_response_wrapper(
            attribution_report.retrieve,
        )


class AsyncAttributionReportResourceWithRawResponse:
    def __init__(self, attribution_report: AsyncAttributionReportResource) -> None:
        self._attribution_report = attribution_report

        self.retrieve = async_to_raw_response_wrapper(
            attribution_report.retrieve,
        )


class AttributionReportResourceWithStreamingResponse:
    def __init__(self, attribution_report: AttributionReportResource) -> None:
        self._attribution_report = attribution_report

        self.retrieve = to_streamed_response_wrapper(
            attribution_report.retrieve,
        )


class AsyncAttributionReportResourceWithStreamingResponse:
    def __init__(self, attribution_report: AsyncAttributionReportResource) -> None:
        self._attribution_report = attribution_report

        self.retrieve = async_to_streamed_response_wrapper(
            attribution_report.retrieve,
        )
