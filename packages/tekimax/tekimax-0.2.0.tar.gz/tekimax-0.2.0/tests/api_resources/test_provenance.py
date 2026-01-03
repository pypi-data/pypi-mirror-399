# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import Any, cast

import pytest

from tekimax import Tekimax, AsyncTekimax
from tests.utils import assert_matches_type
from tekimax.types import ProvenanceRetrieveResponse

base_url = os.environ.get("TEST_API_BASE_URL", "http://127.0.0.1:4010")


class TestProvenance:
    parametrize = pytest.mark.parametrize("client", [False, True], indirect=True, ids=["loose", "strict"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_method_retrieve(self, client: Tekimax) -> None:
        provenance = client.provenance.retrieve(
            "interaction_id",
        )
        assert_matches_type(ProvenanceRetrieveResponse, provenance, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_raw_response_retrieve(self, client: Tekimax) -> None:
        response = client.provenance.with_raw_response.retrieve(
            "interaction_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        provenance = response.parse()
        assert_matches_type(ProvenanceRetrieveResponse, provenance, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_streaming_response_retrieve(self, client: Tekimax) -> None:
        with client.provenance.with_streaming_response.retrieve(
            "interaction_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            provenance = response.parse()
            assert_matches_type(ProvenanceRetrieveResponse, provenance, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    def test_path_params_retrieve(self, client: Tekimax) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `interaction_id` but received ''"):
            client.provenance.with_raw_response.retrieve(
                "",
            )


class TestAsyncProvenance:
    parametrize = pytest.mark.parametrize(
        "async_client", [False, True, {"http_client": "aiohttp"}], indirect=True, ids=["loose", "strict", "aiohttp"]
    )

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_method_retrieve(self, async_client: AsyncTekimax) -> None:
        provenance = await async_client.provenance.retrieve(
            "interaction_id",
        )
        assert_matches_type(ProvenanceRetrieveResponse, provenance, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_raw_response_retrieve(self, async_client: AsyncTekimax) -> None:
        response = await async_client.provenance.with_raw_response.retrieve(
            "interaction_id",
        )

        assert response.is_closed is True
        assert response.http_request.headers.get("X-Stainless-Lang") == "python"
        provenance = await response.parse()
        assert_matches_type(ProvenanceRetrieveResponse, provenance, path=["response"])

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_streaming_response_retrieve(self, async_client: AsyncTekimax) -> None:
        async with async_client.provenance.with_streaming_response.retrieve(
            "interaction_id",
        ) as response:
            assert not response.is_closed
            assert response.http_request.headers.get("X-Stainless-Lang") == "python"

            provenance = await response.parse()
            assert_matches_type(ProvenanceRetrieveResponse, provenance, path=["response"])

        assert cast(Any, response.is_closed) is True

    @pytest.mark.skip(reason="Prism tests are disabled")
    @parametrize
    async def test_path_params_retrieve(self, async_client: AsyncTekimax) -> None:
        with pytest.raises(ValueError, match=r"Expected a non-empty value for `interaction_id` but received ''"):
            await async_client.provenance.with_raw_response.retrieve(
                "",
            )
