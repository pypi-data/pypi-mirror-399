# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tekimax import TekimaxLlc, AsyncTekimaxLlc
from tests.utils import assert_matches_type
from tekimax.types import ContestOutcomeCreateResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestContestOutcome:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_create(self, client: TekimaxLlc) -> None:
        contest_outcome = client.contest_outcome.create(
            contestation_reason="factual_error",
            correction_text="correction_text",
            interaction_id="interaction_id",
        )
        assert_matches_type(ContestOutcomeCreateResponse, contest_outcome, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_create(self, client: TekimaxLlc) -> None:
        response = client.contest_outcome.with_raw_response.create(
            contestation_reason="factual_error",
            correction_text="correction_text",
            interaction_id="interaction_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        contest_outcome = response.parse()
        assert_matches_type(ContestOutcomeCreateResponse, contest_outcome, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_create(self, client: TekimaxLlc) -> None:
        with client.contest_outcome.with_streaming_response.create(
            contestation_reason="factual_error",
            correction_text="correction_text",
            interaction_id="interaction_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            contest_outcome = response.parse()
            assert_matches_type(ContestOutcomeCreateResponse, contest_outcome, path=["response"])

        assert cast(Any, response.is_closed) is True


class TestAsyncContestOutcome:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_create(self, async_client: AsyncTekimaxLlc) -> None:
        contest_outcome = await async_client.contest_outcome.create(
            contestation_reason="factual_error",
            correction_text="correction_text",
            interaction_id="interaction_id",
        )
        assert_matches_type(ContestOutcomeCreateResponse, contest_outcome, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_create(self, async_client: AsyncTekimaxLlc) -> None:
        response = await async_client.contest_outcome.with_raw_response.create(
            contestation_reason="factual_error",
            correction_text="correction_text",
            interaction_id="interaction_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        contest_outcome = await response.parse()
        assert_matches_type(ContestOutcomeCreateResponse, contest_outcome, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_create(self, async_client: AsyncTekimaxLlc) -> None:
        async with async_client.contest_outcome.with_streaming_response.create(
            contestation_reason="factual_error",
            correction_text="correction_text",
            interaction_id="interaction_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            contest_outcome = await response.parse()
            assert_matches_type(ContestOutcomeCreateResponse, contest_outcome, path=["response"])

        assert cast(Any, response.is_closed) is True
