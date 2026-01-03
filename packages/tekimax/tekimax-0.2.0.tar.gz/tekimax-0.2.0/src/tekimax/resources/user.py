# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

from typing import Iterable
from typing_extensions import Literal

import httpx

from ..types import user_auto_detect_modality_profile_params
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
from ..types.user_auto_detect_modality_profile_response import UserAutoDetectModalityProfileResponse

__all__ = ["UserResource", "AsyncUserResource"]


class UserResource(SyncAPIResource):
    @cached_property
    def with_raw_response(self) -> UserResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TEKIMAX/tekimax-python#accessing-raw-response-data-eg-headers
        """
        return UserResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> UserResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TEKIMAX/tekimax-python#with_streaming_response
        """
        return UserResourceWithStreamingResponse(self)

    def auto_detect_modality_profile(
        self,
        *,
        interaction_history: Iterable[user_auto_detect_modality_profile_params.InteractionHistory],
        user_id: str,
        preferred_modality_override: Literal["visual", "auditory", "textual"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> UserAutoDetectModalityProfileResponse:
        """
        Analyzes a user's interaction history to recommend the optimal learning modality
        (Visual, Auditory, Textual) and support level. Used for self-adaptive interface
        scaling.

        Args:
          preferred_modality_override: Optional manual override by the user

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return self._post(
            "/v1/user/modality-profile",
            body=maybe_transform(
                {
                    "interaction_history": interaction_history,
                    "user_id": user_id,
                    "preferred_modality_override": preferred_modality_override,
                },
                user_auto_detect_modality_profile_params.UserAutoDetectModalityProfileParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UserAutoDetectModalityProfileResponse,
        )


class AsyncUserResource(AsyncAPIResource):
    @cached_property
    def with_raw_response(self) -> AsyncUserResourceWithRawResponse:
        """
        This property can be used as a prefix for any HTTP method call to return
        the raw response object instead of the parsed content.

        For more information, see https://www.github.com/TEKIMAX/tekimax-python#accessing-raw-response-data-eg-headers
        """
        return AsyncUserResourceWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncUserResourceWithStreamingResponse:
        """
        An alternative to `.with_raw_response` that doesn't eagerly read the response body.

        For more information, see https://www.github.com/TEKIMAX/tekimax-python#with_streaming_response
        """
        return AsyncUserResourceWithStreamingResponse(self)

    async def auto_detect_modality_profile(
        self,
        *,
        interaction_history: Iterable[user_auto_detect_modality_profile_params.InteractionHistory],
        user_id: str,
        preferred_modality_override: Literal["visual", "auditory", "textual"] | Omit = omit,
        # Use the following arguments if you need to pass additional parameters to the API that aren't available via kwargs.
        # The extra values given here take precedence over values defined on the client or passed to this method.
        extra_headers: Headers | None = None,
        extra_query: Query | None = None,
        extra_body: Body | None = None,
        timeout: float | httpx.Timeout | None | NotGiven = not_given,
    ) -> UserAutoDetectModalityProfileResponse:
        """
        Analyzes a user's interaction history to recommend the optimal learning modality
        (Visual, Auditory, Textual) and support level. Used for self-adaptive interface
        scaling.

        Args:
          preferred_modality_override: Optional manual override by the user

          extra_headers: Send extra headers

          extra_query: Add additional query parameters to the request

          extra_body: Add additional JSON properties to the request

          timeout: Override the client-level default timeout for this request, in seconds
        """
        return await self._post(
            "/v1/user/modality-profile",
            body=await async_maybe_transform(
                {
                    "interaction_history": interaction_history,
                    "user_id": user_id,
                    "preferred_modality_override": preferred_modality_override,
                },
                user_auto_detect_modality_profile_params.UserAutoDetectModalityProfileParams,
            ),
            options=make_request_options(
                extra_headers=extra_headers, extra_query=extra_query, extra_body=extra_body, timeout=timeout
            ),
            cast_to=UserAutoDetectModalityProfileResponse,
        )


class UserResourceWithRawResponse:
    def __init__(self, user: UserResource) -> None:
        self._user = user

        self.auto_detect_modality_profile = to_raw_response_wrapper(
            user.auto_detect_modality_profile,
        )


class AsyncUserResourceWithRawResponse:
    def __init__(self, user: AsyncUserResource) -> None:
        self._user = user

        self.auto_detect_modality_profile = async_to_raw_response_wrapper(
            user.auto_detect_modality_profile,
        )


class UserResourceWithStreamingResponse:
    def __init__(self, user: UserResource) -> None:
        self._user = user

        self.auto_detect_modality_profile = to_streamed_response_wrapper(
            user.auto_detect_modality_profile,
        )


class AsyncUserResourceWithStreamingResponse:
    def __init__(self, user: AsyncUserResource) -> None:
        self._user = user

        self.auto_detect_modality_profile = async_to_streamed_response_wrapper(
            user.auto_detect_modality_profile,
        )
