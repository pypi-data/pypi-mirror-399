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
from ..types.provenance_retrieve_response import ProvenanceRetrieveResponse

__all__ = ["ProvenanceResource", "AsyncProvenanceResource"]


class ProvenanceResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> ProvenanceResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TEKIMAX/tekimax-python#accessing-raw-response-data-eg-headers
        """
        return ProvenanceResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> ProvenanceResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TEKIMAX/tekimax-python#with_streaming_response
        """
        return ProvenanceResourceWithStreamingResponse(self)

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
    ) -> ProvenanceRetrieveResponse:
        """
        Returns C2PA provenance metadata and Human Agency Score for an interaction.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not interaction_id:
            raise ValueError(f"Expected a non-empty value for `interaction_id` but received {interaction_id!r}")
        return self._get(
            f"/v1/provenance/{interaction_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ProvenanceRetrieveResponse,
        )


class AsyncProvenanceResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncProvenanceResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TEKIMAX/tekimax-python#accessing-raw-response-data-eg-headers
        """
        return AsyncProvenanceResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncProvenanceResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TEKIMAX/tekimax-python#with_streaming_response
        """
        return AsyncProvenanceResourceWithStreamingResponse(self)

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
    ) -> ProvenanceRetrieveResponse:
        """
        Returns C2PA provenance metadata and Human Agency Score for an interaction.

        Args:
          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        if not interaction_id:
            raise ValueError(f"Expected a non-empty value for `interaction_id` but received {interaction_id!r}")
        return await self._get(
            f"/v1/provenance/{interaction_id}",
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=ProvenanceRetrieveResponse,
        )


class ProvenanceResourceWithRawResponse:
    def __init__(self, provenance: ProvenanceResource) -> None:
        self._provenance = provenance

        self.retrieve = to_raw_response_wrapper(
            provenance.retrieve,
        )


class AsyncProvenanceResourceWithRawResponse:
    def __init__(self, provenance: AsyncProvenanceResource) -> None:
        self._provenance = provenance

        self.retrieve = async_to_raw_response_wrapper(
            provenance.retrieve,
        )


class ProvenanceResourceWithStreamingResponse:
    def __init__(self, provenance: ProvenanceResource) -> None:
        self._provenance = provenance

        self.retrieve = to_streamed_response_wrapper(
            provenance.retrieve,
        )


class AsyncProvenanceResourceWithStreamingResponse:
    def __init__(self, provenance: AsyncProvenanceResource) -> None:
        self._provenance = provenance

        self.retrieve = async_to_streamed_response_wrapper(
            provenance.retrieve,
        )
