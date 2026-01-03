# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import activity_log_list_params
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
from ..types.activity_log_list_response import ActivityLogListResponse

__all__ = ["ActivityLogResource", "AsyncActivityLogResource"]


class ActivityLogResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ActivityLogResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TEKIMAX/tekimax-python#accessing-raw-response-data-eg-headers
        """
        return ActivityLogResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ActivityLogResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TEKIMAX/tekimax-python#with_streaming_response
        """
        return ActivityLogResourceWithStreamingResponse(self)

    def list(
        self,
        *,
        end_date: str | Omit = omit,
        page: int | Omit = omit,
        page_size: int | Omit = omit,
        start_date: str | Omit = omit,
        user_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ActivityLogListResponse:
        """
        Returns audit trail entries for compliance reporting.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._get(
            "/v1/activity-log",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=maybe_transform(
                    {
                        "end_date": end_date,
                        "page": page,
                        "page_size": page_size,
                        "start_date": start_date,
                        "user_id": user_id,
                    },
                    activity_log_list_params.ActivityLogListParams,
                ),
            ),
            cast_to=ActivityLogListResponse,
        )


class AsyncActivityLogResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncActivityLogResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TEKIMAX/tekimax-python#accessing-raw-response-data-eg-headers
        """
        return AsyncActivityLogResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncActivityLogResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TEKIMAX/tekimax-python#with_streaming_response
        """
        return AsyncActivityLogResourceWithStreamingResponse(self)

    async def list(
        self,
        *,
        end_date: str | Omit = omit,
        page: int | Omit = omit,
        page_size: int | Omit = omit,
        start_date: str | Omit = omit,
        user_id: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ActivityLogListResponse:
        """
        Returns audit trail entries for compliance reporting.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._get(
            "/v1/activity-log",
            options=make_request_options(
                extra_headers=extra_headers,
                extra_query=extra_query,
                extra_body=extra_body,
                timeout=timeout,
                query=await async_maybe_transform(
                    {
                        "end_date": end_date,
                        "page": page,
                        "page_size": page_size,
                        "start_date": start_date,
                        "user_id": user_id,
                    },
                    activity_log_list_params.ActivityLogListParams,
                ),
            ),
            cast_to=ActivityLogListResponse,
        )


class ActivityLogResourceWithRawResponse:
    def __init__(self, activity_log: ActivityLogResource) -> None:
        self._activity_log = activity_log

        self.list = to_raw_response_wrapper(
            activity_log.list,
        )


class AsyncActivityLogResourceWithRawResponse:
    def __init__(self, activity_log: AsyncActivityLogResource) -> None:
        self._activity_log = activity_log

        self.list = async_to_raw_response_wrapper(
            activity_log.list,
        )


class ActivityLogResourceWithStreamingResponse:
    def __init__(self, activity_log: ActivityLogResource) -> None:
        self._activity_log = activity_log

        self.list = to_streamed_response_wrapper(
            activity_log.list,
        )


class AsyncActivityLogResourceWithStreamingResponse:
    def __init__(self, activity_log: AsyncActivityLogResource) -> None:
        self._activity_log = activity_log

        self.list = async_to_streamed_response_wrapper(
            activity_log.list,
        )
