# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tekimax import TekimaxLlc, AsyncTekimaxLlc
from tests.utils import assert_matches_type
from tekimax.types import StreamLearningContentCreateResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestStreamLearningContent:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: TekimaxLlc) -> None:
        stream_learning_content = client.stream_learning_content.create(
            modality_context={},
            prompt="prompt",
        )
        assert_matches_type(StreamLearningContentCreateResponse, stream_learning_content, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: TekimaxLlc) -> None:
        stream_learning_content = client.stream_learning_content.create(
            modality_context={
                "support_level": "standard",
                "type": "visual",
            },
            prompt="prompt",
            provenance_enabled=True,
        )
        assert_matches_type(StreamLearningContentCreateResponse, stream_learning_content, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: TekimaxLlc) -> None:
        response = client.stream_learning_content.with_raw_response.create(
            modality_context={},
            prompt="prompt",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        stream_learning_content = response.parse()
        assert_matches_type(StreamLearningContentCreateResponse, stream_learning_content, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: TekimaxLlc) -> None:
        with client.stream_learning_content.with_streaming_response.create(
            modality_context={},
            prompt="prompt",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            stream_learning_content = response.parse()
            assert_matches_type(StreamLearningContentCreateResponse, stream_learning_content, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncStreamLearningContent:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncTekimaxLlc) -> None:
        stream_learning_content = await async_client.stream_learning_content.create(
            modality_context={},
            prompt="prompt",
        )
        assert_matches_type(StreamLearningContentCreateResponse, stream_learning_content, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncTekimaxLlc) -> None:
        stream_learning_content = await async_client.stream_learning_content.create(
            modality_context={
                "support_level": "standard",
                "type": "visual",
            },
            prompt="prompt",
            provenance_enabled=True,
        )
        assert_matches_type(StreamLearningContentCreateResponse, stream_learning_content, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncTekimaxLlc) -> None:
        response = await async_client.stream_learning_content.with_raw_response.create(
            modality_context={},
            prompt="prompt",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        stream_learning_content = await response.parse()
        assert_matches_type(StreamLearningContentCreateResponse, stream_learning_content, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncTekimaxLlc) -> None:
        async with async_client.stream_learning_content.with_streaming_response.create(
            modality_context={},
            prompt="prompt",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            stream_learning_content = await response.parse()
            assert_matches_type(StreamLearningContentCreateResponse, stream_learning_content, path=["response"])

        assert cast(Any, response.is_closed) is True
