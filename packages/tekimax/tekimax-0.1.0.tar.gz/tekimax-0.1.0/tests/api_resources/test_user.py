# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tekimax import Tekimax, AsyncTekimax
from tests.utils import assert_matches_type
from tekimax.types import UserAutoDetectModalityProfileResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestUser:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_auto_detect_modality_profile(self, client: Tekimax) -> None:
        user = client.user.auto_detect_modality_profile(
            interaction_history=[{}],
            user_id="user-123",
        )
        assert_matches_type(UserAutoDetectModalityProfileResponse, user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_auto_detect_modality_profile_with_all_params(self, client: Tekimax) -> None:
        user = client.user.auto_detect_modality_profile(
            interaction_history=[
                {
                    "completion_status": "completion_status",
                    "content_type_offered": "content_type_offered",
                    "engagement_duration": 0,
                    "interaction_id": "interaction_id",
                    "user_feedback_rating": 0,
                }
            ],
            user_id="user-123",
            preferred_modality_override="visual",
        )
        assert_matches_type(UserAutoDetectModalityProfileResponse, user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_auto_detect_modality_profile(self, client: Tekimax) -> None:
        response = client.user.with_raw_response.auto_detect_modality_profile(
            interaction_history=[{}],
            user_id="user-123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = response.parse()
        assert_matches_type(UserAutoDetectModalityProfileResponse, user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_auto_detect_modality_profile(self, client: Tekimax) -> None:
        with client.user.with_streaming_response.auto_detect_modality_profile(
            interaction_history=[{}],
            user_id="user-123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = response.parse()
            assert_matches_type(UserAutoDetectModalityProfileResponse, user, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncUser:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_auto_detect_modality_profile(self, async_client: AsyncTekimax) -> None:
        user = await async_client.user.auto_detect_modality_profile(
            interaction_history=[{}],
            user_id="user-123",
        )
        assert_matches_type(UserAutoDetectModalityProfileResponse, user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_auto_detect_modality_profile_with_all_params(self, async_client: AsyncTekimax) -> None:
        user = await async_client.user.auto_detect_modality_profile(
            interaction_history=[
                {
                    "completion_status": "completion_status",
                    "content_type_offered": "content_type_offered",
                    "engagement_duration": 0,
                    "interaction_id": "interaction_id",
                    "user_feedback_rating": 0,
                }
            ],
            user_id="user-123",
            preferred_modality_override="visual",
        )
        assert_matches_type(UserAutoDetectModalityProfileResponse, user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_auto_detect_modality_profile(self, async_client: AsyncTekimax) -> None:
        response = await async_client.user.with_raw_response.auto_detect_modality_profile(
            interaction_history=[{}],
            user_id="user-123",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        user = await response.parse()
        assert_matches_type(UserAutoDetectModalityProfileResponse, user, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_auto_detect_modality_profile(self, async_client: AsyncTekimax) -> None:
        async with async_client.user.with_streaming_response.auto_detect_modality_profile(
            interaction_history=[{}],
            user_id="user-123",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            user = await response.parse()
            assert_matches_type(UserAutoDetectModalityProfileResponse, user, path=["response"])

        assert cast(Any, response.is_closed) is True
