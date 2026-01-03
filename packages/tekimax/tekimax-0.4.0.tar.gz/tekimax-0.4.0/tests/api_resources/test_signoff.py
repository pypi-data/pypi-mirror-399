# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tekimax import TekimaxLlc, AsyncTekimaxLlc
from tests.utils import assert_matches_type
from tekimax.types import SignoffCreateResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestSignoff:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: TekimaxLlc) -> None:
        signoff = client.signoff.create(
            action="verify_and_accept",
            interaction_id="interaction_id",
        )
        assert_matches_type(SignoffCreateResponse, signoff, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create_with_all_params(self, client: TekimaxLlc) -> None:
        signoff = client.signoff.create(
            action="verify_and_accept",
            interaction_id="interaction_id",
            attestation_comment="attestation_comment",
        )
        assert_matches_type(SignoffCreateResponse, signoff, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: TekimaxLlc) -> None:
        response = client.signoff.with_raw_response.create(
            action="verify_and_accept",
            interaction_id="interaction_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        signoff = response.parse()
        assert_matches_type(SignoffCreateResponse, signoff, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: TekimaxLlc) -> None:
        with client.signoff.with_streaming_response.create(
            action="verify_and_accept",
            interaction_id="interaction_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            signoff = response.parse()
            assert_matches_type(SignoffCreateResponse, signoff, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncSignoff:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncTekimaxLlc) -> None:
        signoff = await async_client.signoff.create(
            action="verify_and_accept",
            interaction_id="interaction_id",
        )
        assert_matches_type(SignoffCreateResponse, signoff, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create_with_all_params(self, async_client: AsyncTekimaxLlc) -> None:
        signoff = await async_client.signoff.create(
            action="verify_and_accept",
            interaction_id="interaction_id",
            attestation_comment="attestation_comment",
        )
        assert_matches_type(SignoffCreateResponse, signoff, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncTekimaxLlc) -> None:
        response = await async_client.signoff.with_raw_response.create(
            action="verify_and_accept",
            interaction_id="interaction_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        signoff = await response.parse()
        assert_matches_type(SignoffCreateResponse, signoff, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncTekimaxLlc) -> None:
        async with async_client.signoff.with_streaming_response.create(
            action="verify_and_accept",
            interaction_id="interaction_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            signoff = await response.parse()
            assert_matches_type(SignoffCreateResponse, signoff, path=["response"])

        assert cast(Any, response.is_closed) is True
