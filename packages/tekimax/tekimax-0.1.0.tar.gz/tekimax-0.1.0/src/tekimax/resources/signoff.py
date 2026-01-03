# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing_extensions import Literal

import httpx

from ..types import signoff_create_params
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
from ..types.signoff_create_response import SignoffCreateResponse

__all__ = ["SignoffResource", "AsyncSignoffResource"]


class SignoffResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> SignoffResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TEKIMAX/tekimax-python#accessing-raw-response-data-eg-headers
        """
        return SignoffResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> SignoffResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TEKIMAX/tekimax-python#with_streaming_response
        """
        return SignoffResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        action: Literal["verify_and_accept", "reject"],
        interaction_id: str,
        attestation_comment: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SignoffCreateResponse:
        """
        Logs human attestation/verification of AI output (HITL mandate).

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v1/signoff",
            body=maybe_transform(
                {
                    "action": action,
                    "interaction_id": interaction_id,
                    "attestation_comment": attestation_comment,
                },
                signoff_create_params.SignoffCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SignoffCreateResponse,
        )


class AsyncSignoffResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncSignoffResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TEKIMAX/tekimax-python#accessing-raw-response-data-eg-headers
        """
        return AsyncSignoffResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncSignoffResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TEKIMAX/tekimax-python#with_streaming_response
        """
        return AsyncSignoffResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        action: Literal["verify_and_accept", "reject"],
        interaction_id: str,
        attestation_comment: str | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> SignoffCreateResponse:
        """
        Logs human attestation/verification of AI output (HITL mandate).

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v1/signoff",
            body=await async_maybe_transform(
                {
                    "action": action,
                    "interaction_id": interaction_id,
                    "attestation_comment": attestation_comment,
                },
                signoff_create_params.SignoffCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=SignoffCreateResponse,
        )


class SignoffResourceWithRawResponse:
    def __init__(self, signoff: SignoffResource) -> None:
        self._signoff = signoff

        self.create = to_raw_response_wrapper(
            signoff.create,
        )


class AsyncSignoffResourceWithRawResponse:
    def __init__(self, signoff: AsyncSignoffResource) -> None:
        self._signoff = signoff

        self.create = async_to_raw_response_wrapper(
            signoff.create,
        )


class SignoffResourceWithStreamingResponse:
    def __init__(self, signoff: SignoffResource) -> None:
        self._signoff = signoff

        self.create = to_streamed_response_wrapper(
            signoff.create,
        )


class AsyncSignoffResourceWithStreamingResponse:
    def __init__(self, signoff: AsyncSignoffResource) -> None:
        self._signoff = signoff

        self.create = async_to_streamed_response_wrapper(
            signoff.create,
        )
