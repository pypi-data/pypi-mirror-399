# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import httpx

from ..types import stream_learning_content_create_params
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
from ..types.stream_learning_content_create_response import StreamLearningContentCreateResponse

__all__ = ["StreamLearningContentResource", "AsyncStreamLearningContentResource"]


class StreamLearningContentResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> StreamLearningContentResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TEKIMAX/tekimax-python#accessing-raw-response-data-eg-headers
        """
        return StreamLearningContentResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> StreamLearningContentResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TEKIMAX/tekimax-python#with_streaming_response
        """
        return StreamLearningContentResourceWithStreamingResponse(self)

    def create(
        self,
        *,
        modality_context: stream_learning_content_create_params.ModalityContext,
        prompt: str,
        provenance_enabled: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> StreamLearningContentCreateResponse:
        """
        Generates modality-adaptive AI content with audit tagging and C2PA provenance.

        Args:
          prompt: The learning query or topic

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v1/stream-learning-content",
            body=maybe_transform(
                {
                    "modality_context": modality_context,
                    "prompt": prompt,
                    "provenance_enabled": provenance_enabled,
                },
                stream_learning_content_create_params.StreamLearningContentCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=StreamLearningContentCreateResponse,
        )


class AsyncStreamLearningContentResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncStreamLearningContentResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TEKIMAX/tekimax-python#accessing-raw-response-data-eg-headers
        """
        return AsyncStreamLearningContentResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncStreamLearningContentResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TEKIMAX/tekimax-python#with_streaming_response
        """
        return AsyncStreamLearningContentResourceWithStreamingResponse(self)

    async def create(
        self,
        *,
        modality_context: stream_learning_content_create_params.ModalityContext,
        prompt: str,
        provenance_enabled: bool | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> StreamLearningContentCreateResponse:
        """
        Generates modality-adaptive AI content with audit tagging and C2PA provenance.

        Args:
          prompt: The learning query or topic

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v1/stream-learning-content",
            body=await async_maybe_transform(
                {
                    "modality_context": modality_context,
                    "prompt": prompt,
                    "provenance_enabled": provenance_enabled,
                },
                stream_learning_content_create_params.StreamLearningContentCreateParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=StreamLearningContentCreateResponse,
        )


class StreamLearningContentResourceWithRawResponse:
    def __init__(self, stream_learning_content: StreamLearningContentResource) -> None:
        self._stream_learning_content = stream_learning_content

        self.create = to_raw_response_wrapper(
            stream_learning_content.create,
        )


class AsyncStreamLearningContentResourceWithRawResponse:
    def __init__(self, stream_learning_content: AsyncStreamLearningContentResource) -> None:
        self._stream_learning_content = stream_learning_content

        self.create = async_to_raw_response_wrapper(
            stream_learning_content.create,
        )


class StreamLearningContentResourceWithStreamingResponse:
    def __init__(self, stream_learning_content: StreamLearningContentResource) -> None:
        self._stream_learning_content = stream_learning_content

        self.create = to_streamed_response_wrapper(
            stream_learning_content.create,
        )


class AsyncStreamLearningContentResourceWithStreamingResponse:
    def __init__(self, stream_learning_content: AsyncStreamLearningContentResource) -> None:
        self._stream_learning_content = stream_learning_content

        self.create = async_to_streamed_response_wrapper(
            stream_learning_content.create,
        )
