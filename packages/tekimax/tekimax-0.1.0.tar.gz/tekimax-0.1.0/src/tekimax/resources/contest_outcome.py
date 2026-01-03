# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal

import httpx

from ..types import contest_outcome_create_params
from .._types import Body, Query, Headers, NotGiven, not_given
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
from ..types.contest_outcome_create_response import ContestOutcomeCreateResponse

__all__ = ["ContestOutcomeResource", "AsyncContestOutcomeResource"]


class ContestOutcomeResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ContestOutcomeResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TEKIMAX/tekimax-python#accessing-raw-response-data-eg-headers
        """
        return ContestOutcomeResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ContestOutcomeResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TEKIMAX/tekimax-python#with_streaming_response
        """
        return ContestOutcomeResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        contestation_reason: Literal["factual_error", "bias_detected", "modality_mismatch", "hallucination"],
        correction_text: str,
        interaction_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ContestOutcomeCreateResponse:
        """
        Contestability flow for users to flag/correct AI outputs (M-25-21 mandate).

        Args:
          correction_text: User's proposed correction

          interaction_id: ID of the AI response being contested

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v1/contest-outcome",
            body=maybe_transform(
                {
                    "contestation_reason": contestation_reason,
                    "correction_text": correction_text,
                    "interaction_id": interaction_id,
                },
                contest_outcome_create_params.ContestOutcomeCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ContestOutcomeCreateResponse,
        )


class AsyncContestOutcomeResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncContestOutcomeResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TEKIMAX/tekimax-python#accessing-raw-response-data-eg-headers
        """
        return AsyncContestOutcomeResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncContestOutcomeResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TEKIMAX/tekimax-python#with_streaming_response
        """
        return AsyncContestOutcomeResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        contestation_reason: Literal["factual_error", "bias_detected", "modality_mismatch", "hallucination"],
        correction_text: str,
        interaction_id: str,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> ContestOutcomeCreateResponse:
        """
        Contestability flow for users to flag/correct AI outputs (M-25-21 mandate).

        Args:
          correction_text: User's proposed correction

          interaction_id: ID of the AI response being contested

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v1/contest-outcome",
            body=await async_maybe_transform(
                {
                    "contestation_reason": contestation_reason,
                    "correction_text": correction_text,
                    "interaction_id": interaction_id,
                },
                contest_outcome_create_params.ContestOutcomeCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ContestOutcomeCreateResponse,
        )


class ContestOutcomeResourceWithRawResponse:
    def __init__(self, contest_outcome: ContestOutcomeResource) -> None:
        self._contest_outcome = contest_outcome

        self.create = to_raw_response_wrapper(
            contest_outcome.create,
        )


class AsyncContestOutcomeResourceWithRawResponse:
    def __init__(self, contest_outcome: AsyncContestOutcomeResource) -> None:
        self._contest_outcome = contest_outcome

        self.create = async_to_raw_response_wrapper(
            contest_outcome.create,
        )


class ContestOutcomeResourceWithStreamingResponse:
    def __init__(self, contest_outcome: ContestOutcomeResource) -> None:
        self._contest_outcome = contest_outcome

        self.create = to_streamed_response_wrapper(
            contest_outcome.create,
        )


class AsyncContestOutcomeResourceWithStreamingResponse:
    def __init__(self, contest_outcome: AsyncContestOutcomeResource) -> None:
        self._contest_outcome = contest_outcome

        self.create = async_to_streamed_response_wrapper(
            contest_outcome.create,
        )
