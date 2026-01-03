# File generated from our OpenAPI spec by Stainless. See CONTRIBUTING.md for details.

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Any, Dict, Mapping, cast
from typing_extensions import Self, Literal, override

import httpx

from . import _exceptions
from ._qs import Querystring
from ._types import (
    Omit,
    Timeout,
    NotGiven,
    Transport,
    ProxiesTypes,
    RequestOptions,
    not_given,
)
from ._utils import is_given, get_async_library
from ._compat import cached_property
from ._version import __version__
from ._streaming import Stream as Stream, AsyncStream as AsyncStream
from ._exceptions import TekimaxError, APIStatusError
from ._base_client import (
    DEFAULT_MAX_RETRIES,
    SyncAPIClient,
    AsyncAPIClient,
)

if TYPE_CHECKING:
    from .resources import (
        user,
        agent,
        metrics,
        redress,
        signoff,
        provenance,
        activity_log,
        transparency,
        contest_outcome,
        attribution_report,
        stream_learning_content,
    )
    from .resources.user import UserResource, AsyncUserResource
    from .resources.agent import AgentResource, AsyncAgentResource
    from .resources.metrics import MetricsResource, AsyncMetricsResource
    from .resources.redress import RedressResource, AsyncRedressResource
    from .resources.signoff import SignoffResource, AsyncSignoffResource
    from .resources.provenance import ProvenanceResource, AsyncProvenanceResource
    from .resources.activity_log import ActivityLogResource, AsyncActivityLogResource
    from .resources.transparency import TransparencyResource, AsyncTransparencyResource
    from .resources.contest_outcome import ContestOutcomeResource, AsyncContestOutcomeResource
    from .resources.attribution_report import AttributionReportResource, AsyncAttributionReportResource
    from .resources.stream_learning_content import StreamLearningContentResource, AsyncStreamLearningContentResource

__all__ = [
    "ENVIRONMENTS",
    "Timeout",
    "Transport",
    "ProxiesTypes",
    "RequestOptions",
    "Tekimax",
    "AsyncTekimax",
    "Client",
    "AsyncClient",
]

ENVIRONMENTS: Dict[str, str] = {
    "production": "https://architecture-engine-api-922336218060.us-central1.run.app",
    "local": "http://localhost:8080",
}


class Tekimax(SyncAPIClient):
    # client options
    api_key: str

    _environment: Literal["production", "local"] | NotGiven

    def __init__(
        self,
        *,
        api_key: str | None = None,
        environment: Literal["production", "local"] | NotGiven = not_given,
        base_url: str | httpx.URL | None | NotGiven = not_given,
        timeout: float | Timeout | None | NotGiven = not_given,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        # Configure a custom httpx client.
        # We provide a `DefaultHttpxClient` class that you can pass to retain the default values we use for `limits`, `timeout` & `follow_redirects`.
        # See the [httpx documentation](https://www.python-httpx.org/api/#client) for more details.
        http_client: httpx.Client | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
        _strict_response_validation: bool = False,
    ) -> None:
        """Construct a new synchronous Tekimax client instance.

        This automatically infers the `api_key` argument from the `TEKIMAX_API_KEY` environment variable if it is not provided.
        """
        if api_key is None:
            api_key = os.environ.get("TEKIMAX_API_KEY")
        if api_key is None:
            raise TekimaxError(
                "The api_key client option must be set either by passing api_key to the client or by setting the TEKIMAX_API_KEY environment variable"
            )
        self.api_key = api_key

        self._environment = environment

        base_url_env = os.environ.get("TEKIMAX_BASE_URL")
        if is_given(base_url) and base_url is not None:
            # cast required because mypy doesn't understand the type narrowing
            base_url = cast("str | httpx.URL", base_url)  # pyright: ignore[reportUnnecessaryCast]
        elif is_given(environment):
            if base_url_env and base_url is not None:
                raise ValueError(
                    "Ambiguous URL; The `TEKIMAX_BASE_URL` env var and the `environment` argument are given. If you want to use the environment, you must pass base_url=None",
                )

            try:
                base_url = ENVIRONMENTS[environment]
            except KeyError as exc:
                raise ValueError(f"Unknown environment: {environment}") from exc
        elif base_url_env is not None:
            base_url = base_url_env
        else:
            self._environment = environment = "production"

            try:
                base_url = ENVIRONMENTS[environment]
            except KeyError as exc:
                raise ValueError(f"Unknown environment: {environment}") from exc

        super().__init__(
            version=__version__,
            base_url=base_url,
            max_retries=max_retries,
            timeout=timeout,
            http_client=http_client,
            custom_headers=default_headers,
            custom_query=default_query,
            _strict_response_validation=_strict_response_validation,
        )

    @cached_property
    def stream_learning_content(self) -> StreamLearningContentResource:
        from .resources.stream_learning_content import StreamLearningContentResource

        return StreamLearningContentResource(self)

    @cached_property
    def user(self) -> UserResource:
        from .resources.user import UserResource

        return UserResource(self)

    @cached_property
    def contest_outcome(self) -> ContestOutcomeResource:
        from .resources.contest_outcome import ContestOutcomeResource

        return ContestOutcomeResource(self)

    @cached_property
    def redress(self) -> RedressResource:
        from .resources.redress import RedressResource

        return RedressResource(self)

    @cached_property
    def provenance(self) -> ProvenanceResource:
        from .resources.provenance import ProvenanceResource

        return ProvenanceResource(self)

    @cached_property
    def signoff(self) -> SignoffResource:
        from .resources.signoff import SignoffResource

        return SignoffResource(self)

    @cached_property
    def transparency(self) -> TransparencyResource:
        from .resources.transparency import TransparencyResource

        return TransparencyResource(self)

    @cached_property
    def metrics(self) -> MetricsResource:
        from .resources.metrics import MetricsResource

        return MetricsResource(self)

    @cached_property
    def attribution_report(self) -> AttributionReportResource:
        from .resources.attribution_report import AttributionReportResource

        return AttributionReportResource(self)

    @cached_property
    def activity_log(self) -> ActivityLogResource:
        from .resources.activity_log import ActivityLogResource

        return ActivityLogResource(self)

    @cached_property
    def agent(self) -> AgentResource:
        from .resources.agent import AgentResource

        return AgentResource(self)

    @cached_property
    def with_raw_response(self) -> TekimaxWithRawResponse:
        return TekimaxWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> TekimaxWithStreamedResponse:
        return TekimaxWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="comma")

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": "false",
            **self._custom_headers,
        }

    def copy(
        self,
        *,
        api_key: str | None = None,
        environment: Literal["production", "local"] | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = not_given,
        http_client: httpx.Client | None = None,
        max_retries: int | NotGiven = not_given,
        default_headers: Mapping[str, str] | None = None,
        set_default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        set_default_query: Mapping[str, object] | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
    ) -> Self:
        """
        Create a new client instance re-using the same options given to the current client with optional overriding.
        """
        if default_headers is not None and set_default_headers is not None:
            raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")

        if default_query is not None and set_default_query is not None:
            raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")

        headers = self._custom_headers
        if default_headers is not None:
            headers = {**headers, **default_headers}
        elif set_default_headers is not None:
            headers = set_default_headers

        params = self._custom_query
        if default_query is not None:
            params = {**params, **default_query}
        elif set_default_query is not None:
            params = set_default_query

        http_client = http_client or self._client
        return self.__class__(
            api_key=api_key or self.api_key,
            base_url=base_url or self.base_url,
            environment=environment or self._environment,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            **_extra_kwargs,
        )

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    @override
    def _make_status_error(
        self,
        err_msg: str,
        *,
        body: object,
        response: httpx.Response,
    ) -> APIStatusError:
        if response.status_code == 400:
            return _exceptions.BadRequestError(err_msg, response=response, body=body)

        if response.status_code == 401:
            return _exceptions.AuthenticationError(err_msg, response=response, body=body)

        if response.status_code == 403:
            return _exceptions.PermissionDeniedError(err_msg, response=response, body=body)

        if response.status_code == 404:
            return _exceptions.NotFoundError(err_msg, response=response, body=body)

        if response.status_code == 409:
            return _exceptions.ConflictError(err_msg, response=response, body=body)

        if response.status_code == 422:
            return _exceptions.UnprocessableEntityError(err_msg, response=response, body=body)

        if response.status_code == 429:
            return _exceptions.RateLimitError(err_msg, response=response, body=body)

        if response.status_code >= 500:
            return _exceptions.InternalServerError(err_msg, response=response, body=body)
        return APIStatusError(err_msg, response=response, body=body)


class AsyncTekimax(AsyncAPIClient):
    # client options
    api_key: str

    _environment: Literal["production", "local"] | NotGiven

    def __init__(
        self,
        *,
        api_key: str | None = None,
        environment: Literal["production", "local"] | NotGiven = not_given,
        base_url: str | httpx.URL | None | NotGiven = not_given,
        timeout: float | Timeout | None | NotGiven = not_given,
        max_retries: int = DEFAULT_MAX_RETRIES,
        default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        # Configure a custom httpx client.
        # We provide a `DefaultAsyncHttpxClient` class that you can pass to retain the default values we use for `limits`, `timeout` & `follow_redirects`.
        # See the [httpx documentation](https://www.python-httpx.org/api/#asyncclient) for more details.
        http_client: httpx.AsyncClient | None = None,
        # Enable or disable schema validation for data returned by the API.
        # When enabled an error APIResponseValidationError is raised
        # if the API responds with invalid data for the expected schema.
        #
        # This parameter may be removed or changed in the future.
        # If you rely on this feature, please open a GitHub issue
        # outlining your use-case to help us decide if it should be
        # part of our public interface in the future.
        _strict_response_validation: bool = False,
    ) -> None:
        """Construct a new async AsyncTekimax client instance.

        This automatically infers the `api_key` argument from the `TEKIMAX_API_KEY` environment variable if it is not provided.
        """
        if api_key is None:
            api_key = os.environ.get("TEKIMAX_API_KEY")
        if api_key is None:
            raise TekimaxError(
                "The api_key client option must be set either by passing api_key to the client or by setting the TEKIMAX_API_KEY environment variable"
            )
        self.api_key = api_key

        self._environment = environment

        base_url_env = os.environ.get("TEKIMAX_BASE_URL")
        if is_given(base_url) and base_url is not None:
            # cast required because mypy doesn't understand the type narrowing
            base_url = cast("str | httpx.URL", base_url)  # pyright: ignore[reportUnnecessaryCast]
        elif is_given(environment):
            if base_url_env and base_url is not None:
                raise ValueError(
                    "Ambiguous URL; The `TEKIMAX_BASE_URL` env var and the `environment` argument are given. If you want to use the environment, you must pass base_url=None",
                )

            try:
                base_url = ENVIRONMENTS[environment]
            except KeyError as exc:
                raise ValueError(f"Unknown environment: {environment}") from exc
        elif base_url_env is not None:
            base_url = base_url_env
        else:
            self._environment = environment = "production"

            try:
                base_url = ENVIRONMENTS[environment]
            except KeyError as exc:
                raise ValueError(f"Unknown environment: {environment}") from exc

        super().__init__(
            version=__version__,
            base_url=base_url,
            max_retries=max_retries,
            timeout=timeout,
            http_client=http_client,
            custom_headers=default_headers,
            custom_query=default_query,
            _strict_response_validation=_strict_response_validation,
        )

    @cached_property
    def stream_learning_content(self) -> AsyncStreamLearningContentResource:
        from .resources.stream_learning_content import AsyncStreamLearningContentResource

        return AsyncStreamLearningContentResource(self)

    @cached_property
    def user(self) -> AsyncUserResource:
        from .resources.user import AsyncUserResource

        return AsyncUserResource(self)

    @cached_property
    def contest_outcome(self) -> AsyncContestOutcomeResource:
        from .resources.contest_outcome import AsyncContestOutcomeResource

        return AsyncContestOutcomeResource(self)

    @cached_property
    def redress(self) -> AsyncRedressResource:
        from .resources.redress import AsyncRedressResource

        return AsyncRedressResource(self)

    @cached_property
    def provenance(self) -> AsyncProvenanceResource:
        from .resources.provenance import AsyncProvenanceResource

        return AsyncProvenanceResource(self)

    @cached_property
    def signoff(self) -> AsyncSignoffResource:
        from .resources.signoff import AsyncSignoffResource

        return AsyncSignoffResource(self)

    @cached_property
    def transparency(self) -> AsyncTransparencyResource:
        from .resources.transparency import AsyncTransparencyResource

        return AsyncTransparencyResource(self)

    @cached_property
    def metrics(self) -> AsyncMetricsResource:
        from .resources.metrics import AsyncMetricsResource

        return AsyncMetricsResource(self)

    @cached_property
    def attribution_report(self) -> AsyncAttributionReportResource:
        from .resources.attribution_report import AsyncAttributionReportResource

        return AsyncAttributionReportResource(self)

    @cached_property
    def activity_log(self) -> AsyncActivityLogResource:
        from .resources.activity_log import AsyncActivityLogResource

        return AsyncActivityLogResource(self)

    @cached_property
    def agent(self) -> AsyncAgentResource:
        from .resources.agent import AsyncAgentResource

        return AsyncAgentResource(self)

    @cached_property
    def with_raw_response(self) -> AsyncTekimaxWithRawResponse:
        return AsyncTekimaxWithRawResponse(self)

    @cached_property
    def with_streaming_response(self) -> AsyncTekimaxWithStreamedResponse:
        return AsyncTekimaxWithStreamedResponse(self)

    @property
    @override
    def qs(self) -> Querystring:
        return Querystring(array_format="comma")

    @property
    @override
    def default_headers(self) -> dict[str, str | Omit]:
        return {
            **super().default_headers,
            "X-Stainless-Async": f"async:{get_async_library()}",
            **self._custom_headers,
        }

    def copy(
        self,
        *,
        api_key: str | None = None,
        environment: Literal["production", "local"] | None = None,
        base_url: str | httpx.URL | None = None,
        timeout: float | Timeout | None | NotGiven = not_given,
        http_client: httpx.AsyncClient | None = None,
        max_retries: int | NotGiven = not_given,
        default_headers: Mapping[str, str] | None = None,
        set_default_headers: Mapping[str, str] | None = None,
        default_query: Mapping[str, object] | None = None,
        set_default_query: Mapping[str, object] | None = None,
        _extra_kwargs: Mapping[str, Any] = {},
    ) -> Self:
        """
        Create a new client instance re-using the same options given to the current client with optional overriding.
        """
        if default_headers is not None and set_default_headers is not None:
            raise ValueError("The `default_headers` and `set_default_headers` arguments are mutually exclusive")

        if default_query is not None and set_default_query is not None:
            raise ValueError("The `default_query` and `set_default_query` arguments are mutually exclusive")

        headers = self._custom_headers
        if default_headers is not None:
            headers = {**headers, **default_headers}
        elif set_default_headers is not None:
            headers = set_default_headers

        params = self._custom_query
        if default_query is not None:
            params = {**params, **default_query}
        elif set_default_query is not None:
            params = set_default_query

        http_client = http_client or self._client
        return self.__class__(
            api_key=api_key or self.api_key,
            base_url=base_url or self.base_url,
            environment=environment or self._environment,
            timeout=self.timeout if isinstance(timeout, NotGiven) else timeout,
            http_client=http_client,
            max_retries=max_retries if is_given(max_retries) else self.max_retries,
            default_headers=headers,
            default_query=params,
            **_extra_kwargs,
        )

    # Alias for `copy` for nicer inline usage, e.g.
    # client.with_options(timeout=10).foo.create(...)
    with_options = copy

    @override
    def _make_status_error(
        self,
        err_msg: str,
        *,
        body: object,
        response: httpx.Response,
    ) -> APIStatusError:
        if response.status_code == 400:
            return _exceptions.BadRequestError(err_msg, response=response, body=body)

        if response.status_code == 401:
            return _exceptions.AuthenticationError(err_msg, response=response, body=body)

        if response.status_code == 403:
            return _exceptions.PermissionDeniedError(err_msg, response=response, body=body)

        if response.status_code == 404:
            return _exceptions.NotFoundError(err_msg, response=response, body=body)

        if response.status_code == 409:
            return _exceptions.ConflictError(err_msg, response=response, body=body)

        if response.status_code == 422:
            return _exceptions.UnprocessableEntityError(err_msg, response=response, body=body)

        if response.status_code == 429:
            return _exceptions.RateLimitError(err_msg, response=response, body=body)

        if response.status_code >= 500:
            return _exceptions.InternalServerError(err_msg, response=response, body=body)
        return APIStatusError(err_msg, response=response, body=body)


class TekimaxWithRawResponse:
    _client: Tekimax

    def __init__(self, client: Tekimax) -> None:
        self._client = client

    @cached_property
    def stream_learning_content(self) -> stream_learning_content.StreamLearningContentResourceWithRawResponse:
        from .resources.stream_learning_content import StreamLearningContentResourceWithRawResponse

        return StreamLearningContentResourceWithRawResponse(self._client.stream_learning_content)

    @cached_property
    def user(self) -> user.UserResourceWithRawResponse:
        from .resources.user import UserResourceWithRawResponse

        return UserResourceWithRawResponse(self._client.user)

    @cached_property
    def contest_outcome(self) -> contest_outcome.ContestOutcomeResourceWithRawResponse:
        from .resources.contest_outcome import ContestOutcomeResourceWithRawResponse

        return ContestOutcomeResourceWithRawResponse(self._client.contest_outcome)

    @cached_property
    def redress(self) -> redress.RedressResourceWithRawResponse:
        from .resources.redress import RedressResourceWithRawResponse

        return RedressResourceWithRawResponse(self._client.redress)

    @cached_property
    def provenance(self) -> provenance.ProvenanceResourceWithRawResponse:
        from .resources.provenance import ProvenanceResourceWithRawResponse

        return ProvenanceResourceWithRawResponse(self._client.provenance)

    @cached_property
    def signoff(self) -> signoff.SignoffResourceWithRawResponse:
        from .resources.signoff import SignoffResourceWithRawResponse

        return SignoffResourceWithRawResponse(self._client.signoff)

    @cached_property
    def transparency(self) -> transparency.TransparencyResourceWithRawResponse:
        from .resources.transparency import TransparencyResourceWithRawResponse

        return TransparencyResourceWithRawResponse(self._client.transparency)

    @cached_property
    def metrics(self) -> metrics.MetricsResourceWithRawResponse:
        from .resources.metrics import MetricsResourceWithRawResponse

        return MetricsResourceWithRawResponse(self._client.metrics)

    @cached_property
    def attribution_report(self) -> attribution_report.AttributionReportResourceWithRawResponse:
        from .resources.attribution_report import AttributionReportResourceWithRawResponse

        return AttributionReportResourceWithRawResponse(self._client.attribution_report)

    @cached_property
    def activity_log(self) -> activity_log.ActivityLogResourceWithRawResponse:
        from .resources.activity_log import ActivityLogResourceWithRawResponse

        return ActivityLogResourceWithRawResponse(self._client.activity_log)

    @cached_property
    def agent(self) -> agent.AgentResourceWithRawResponse:
        from .resources.agent import AgentResourceWithRawResponse

        return AgentResourceWithRawResponse(self._client.agent)


class AsyncTekimaxWithRawResponse:
    _client: AsyncTekimax

    def __init__(self, client: AsyncTekimax) -> None:
        self._client = client

    @cached_property
    def stream_learning_content(self) -> stream_learning_content.AsyncStreamLearningContentResourceWithRawResponse:
        from .resources.stream_learning_content import AsyncStreamLearningContentResourceWithRawResponse

        return AsyncStreamLearningContentResourceWithRawResponse(self._client.stream_learning_content)

    @cached_property
    def user(self) -> user.AsyncUserResourceWithRawResponse:
        from .resources.user import AsyncUserResourceWithRawResponse

        return AsyncUserResourceWithRawResponse(self._client.user)

    @cached_property
    def contest_outcome(self) -> contest_outcome.AsyncContestOutcomeResourceWithRawResponse:
        from .resources.contest_outcome import AsyncContestOutcomeResourceWithRawResponse

        return AsyncContestOutcomeResourceWithRawResponse(self._client.contest_outcome)

    @cached_property
    def redress(self) -> redress.AsyncRedressResourceWithRawResponse:
        from .resources.redress import AsyncRedressResourceWithRawResponse

        return AsyncRedressResourceWithRawResponse(self._client.redress)

    @cached_property
    def provenance(self) -> provenance.AsyncProvenanceResourceWithRawResponse:
        from .resources.provenance import AsyncProvenanceResourceWithRawResponse

        return AsyncProvenanceResourceWithRawResponse(self._client.provenance)

    @cached_property
    def signoff(self) -> signoff.AsyncSignoffResourceWithRawResponse:
        from .resources.signoff import AsyncSignoffResourceWithRawResponse

        return AsyncSignoffResourceWithRawResponse(self._client.signoff)

    @cached_property
    def transparency(self) -> transparency.AsyncTransparencyResourceWithRawResponse:
        from .resources.transparency import AsyncTransparencyResourceWithRawResponse

        return AsyncTransparencyResourceWithRawResponse(self._client.transparency)

    @cached_property
    def metrics(self) -> metrics.AsyncMetricsResourceWithRawResponse:
        from .resources.metrics import AsyncMetricsResourceWithRawResponse

        return AsyncMetricsResourceWithRawResponse(self._client.metrics)

    @cached_property
    def attribution_report(self) -> attribution_report.AsyncAttributionReportResourceWithRawResponse:
        from .resources.attribution_report import AsyncAttributionReportResourceWithRawResponse

        return AsyncAttributionReportResourceWithRawResponse(self._client.attribution_report)

    @cached_property
    def activity_log(self) -> activity_log.AsyncActivityLogResourceWithRawResponse:
        from .resources.activity_log import AsyncActivityLogResourceWithRawResponse

        return AsyncActivityLogResourceWithRawResponse(self._client.activity_log)

    @cached_property
    def agent(self) -> agent.AsyncAgentResourceWithRawResponse:
        from .resources.agent import AsyncAgentResourceWithRawResponse

        return AsyncAgentResourceWithRawResponse(self._client.agent)


class TekimaxWithStreamedResponse:
    _client: Tekimax

    def __init__(self, client: Tekimax) -> None:
        self._client = client

    @cached_property
    def stream_learning_content(self) -> stream_learning_content.StreamLearningContentResourceWithStreamingResponse:
        from .resources.stream_learning_content import StreamLearningContentResourceWithStreamingResponse

        return StreamLearningContentResourceWithStreamingResponse(self._client.stream_learning_content)

    @cached_property
    def user(self) -> user.UserResourceWithStreamingResponse:
        from .resources.user import UserResourceWithStreamingResponse

        return UserResourceWithStreamingResponse(self._client.user)

    @cached_property
    def contest_outcome(self) -> contest_outcome.ContestOutcomeResourceWithStreamingResponse:
        from .resources.contest_outcome import ContestOutcomeResourceWithStreamingResponse

        return ContestOutcomeResourceWithStreamingResponse(self._client.contest_outcome)

    @cached_property
    def redress(self) -> redress.RedressResourceWithStreamingResponse:
        from .resources.redress import RedressResourceWithStreamingResponse

        return RedressResourceWithStreamingResponse(self._client.redress)

    @cached_property
    def provenance(self) -> provenance.ProvenanceResourceWithStreamingResponse:
        from .resources.provenance import ProvenanceResourceWithStreamingResponse

        return ProvenanceResourceWithStreamingResponse(self._client.provenance)

    @cached_property
    def signoff(self) -> signoff.SignoffResourceWithStreamingResponse:
        from .resources.signoff import SignoffResourceWithStreamingResponse

        return SignoffResourceWithStreamingResponse(self._client.signoff)

    @cached_property
    def transparency(self) -> transparency.TransparencyResourceWithStreamingResponse:
        from .resources.transparency import TransparencyResourceWithStreamingResponse

        return TransparencyResourceWithStreamingResponse(self._client.transparency)

    @cached_property
    def metrics(self) -> metrics.MetricsResourceWithStreamingResponse:
        from .resources.metrics import MetricsResourceWithStreamingResponse

        return MetricsResourceWithStreamingResponse(self._client.metrics)

    @cached_property
    def attribution_report(self) -> attribution_report.AttributionReportResourceWithStreamingResponse:
        from .resources.attribution_report import AttributionReportResourceWithStreamingResponse

        return AttributionReportResourceWithStreamingResponse(self._client.attribution_report)

    @cached_property
    def activity_log(self) -> activity_log.ActivityLogResourceWithStreamingResponse:
        from .resources.activity_log import ActivityLogResourceWithStreamingResponse

        return ActivityLogResourceWithStreamingResponse(self._client.activity_log)

    @cached_property
    def agent(self) -> agent.AgentResourceWithStreamingResponse:
        from .resources.agent import AgentResourceWithStreamingResponse

        return AgentResourceWithStreamingResponse(self._client.agent)


class AsyncTekimaxWithStreamedResponse:
    _client: AsyncTekimax

    def __init__(self, client: AsyncTekimax) -> None:
        self._client = client

    @cached_property
    def stream_learning_content(
        self,
    ) -> stream_learning_content.AsyncStreamLearningContentResourceWithStreamingResponse:
        from .resources.stream_learning_content import AsyncStreamLearningContentResourceWithStreamingResponse

        return AsyncStreamLearningContentResourceWithStreamingResponse(self._client.stream_learning_content)

    @cached_property
    def user(self) -> user.AsyncUserResourceWithStreamingResponse:
        from .resources.user import AsyncUserResourceWithStreamingResponse

        return AsyncUserResourceWithStreamingResponse(self._client.user)

    @cached_property
    def contest_outcome(self) -> contest_outcome.AsyncContestOutcomeResourceWithStreamingResponse:
        from .resources.contest_outcome import AsyncContestOutcomeResourceWithStreamingResponse

        return AsyncContestOutcomeResourceWithStreamingResponse(self._client.contest_outcome)

    @cached_property
    def redress(self) -> redress.AsyncRedressResourceWithStreamingResponse:
        from .resources.redress import AsyncRedressResourceWithStreamingResponse

        return AsyncRedressResourceWithStreamingResponse(self._client.redress)

    @cached_property
    def provenance(self) -> provenance.AsyncProvenanceResourceWithStreamingResponse:
        from .resources.provenance import AsyncProvenanceResourceWithStreamingResponse

        return AsyncProvenanceResourceWithStreamingResponse(self._client.provenance)

    @cached_property
    def signoff(self) -> signoff.AsyncSignoffResourceWithStreamingResponse:
        from .resources.signoff import AsyncSignoffResourceWithStreamingResponse

        return AsyncSignoffResourceWithStreamingResponse(self._client.signoff)

    @cached_property
    def transparency(self) -> transparency.AsyncTransparencyResourceWithStreamingResponse:
        from .resources.transparency import AsyncTransparencyResourceWithStreamingResponse

        return AsyncTransparencyResourceWithStreamingResponse(self._client.transparency)

    @cached_property
    def metrics(self) -> metrics.AsyncMetricsResourceWithStreamingResponse:
        from .resources.metrics import AsyncMetricsResourceWithStreamingResponse

        return AsyncMetricsResourceWithStreamingResponse(self._client.metrics)

    @cached_property
    def attribution_report(self) -> attribution_report.AsyncAttributionReportResourceWithStreamingResponse:
        from .resources.attribution_report import AsyncAttributionReportResourceWithStreamingResponse

        return AsyncAttributionReportResourceWithStreamingResponse(self._client.attribution_report)

    @cached_property
    def activity_log(self) -> activity_log.AsyncActivityLogResourceWithStreamingResponse:
        from .resources.activity_log import AsyncActivityLogResourceWithStreamingResponse

        return AsyncActivityLogResourceWithStreamingResponse(self._client.activity_log)

    @cached_property
    def agent(self) -> agent.AsyncAgentResourceWithStreamingResponse:
        from .resources.agent import AsyncAgentResourceWithStreamingResponse

        return AsyncAgentResourceWithStreamingResponse(self._client.agent)


Client = Tekimax

AsyncClient = AsyncTekimax
