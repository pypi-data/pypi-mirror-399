"""Phoenix tracing helpers for LangChain-based workflows."""

from __future__ import annotations

import logging
import os
from collections.abc import Mapping
from contextlib import ExitStack, contextmanager
from typing import Any, Final

from openinference.instrumentation import dangerously_using_project, using_metadata
from openinference.instrumentation.langchain import LangChainInstrumentor
from opentelemetry import trace as trace_api
from opentelemetry.sdk.trace import TracerProvider
from phoenix.otel import register

_LOGGER = logging.getLogger(__name__)

_PHOENIX_ENABLE_ENV: Final = "AGENT_FLOWS_ENABLE_PHOENIX_TRACING"
_PHOENIX_PROJECT_ENV: Final = "PHOENIX_PROJECT_NAME"
_PHOENIX_API_KEY_ENV: Final = "PHOENIX_API_KEY"
_ALT_PHOENIX_API_KEY_ENV: Final = "AGENT_FLOWS_PHOENIX_API_KEY"
_PHOENIX_ENDPOINT_ENV: Final = "PHOENIX_COLLECTOR_ENDPOINT"

_DEFAULT_PROJECT_NAME: Final = "realtimex-agent-flows-builder"
_DEFAULT_COLLECTOR_ENDPOINT: Final = "https://llmtracing.realtimex.co/v1/traces"
_DEFAULT_API_KEY: Final = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJqdGkiOiJBcGlLZXk6OCJ9.XT43ShmBWN23Nkf9tG3np6f3SEMAYZvFCq2GPdm23e8"

_LANGCHAIN_INSTRUMENTED = False


def initialize_phoenix_tracing(
    *,
    project_name: str | None = None,
    collector_endpoint: str | None = None,
    api_key: str | None = None,
    auto_instrument: bool = False,
    skip_if_disabled: bool = True,
) -> TracerProvider | None:
    """Configure Phoenix tracing and instrument LangChain if enabled.

    Tracing is enabled by default. Set ``AGENT_FLOWS_ENABLE_PHOENIX_TRACING`` to a
    falsy value (``0``, ``false``, ``off``) to opt out while keeping the helper available.
    Defaults point at the shared RealTimeX Phoenix deployment. When another
    OpenTelemetry tracer provider is already configured globally, it is reused
    instead of creating a new one.

    Args:
        project_name: Optional Phoenix project override. Defaults to the
            RealTimeX project ``realtimex-agent-flows-builder`` unless
            ``PHOENIX_PROJECT_NAME`` is set.
        collector_endpoint: Optional Phoenix collector override. Defaults to
            ``https://llmtracing.realtimex.co/v1/traces`` unless
            ``PHOENIX_COLLECTOR_ENDPOINT`` is set.
        api_key: Optional Phoenix API key. Defaults to the shared RealTimeX key
            unless ``PHOENIX_API_KEY`` or ``AGENT_FLOWS_PHOENIX_API_KEY`` is set.
        auto_instrument: Whether Phoenix should auto-instrument additional supported
            frameworks. Defaults to ``False`` so instrumentation remains explicit.
        skip_if_disabled: When ``True`` (default), the helper returns ``None`` without
            configuring tracing if tracing was explicitly disabled via environment.

    Returns:
        The configured :class:`~opentelemetry.sdk.trace.TracerProvider` or ``None`` when
        tracing is disabled.
    """
    if skip_if_disabled and not _is_tracing_enabled():
        _LOGGER.debug("Phoenix tracing disabled via %s", _PHOENIX_ENABLE_ENV)
        return None

    resolved_endpoint = _resolve_endpoint(collector_endpoint)
    resolved_project = _resolve_project_name(project_name)
    resolved_api_key = _resolve_api_key(api_key)

    tracer_provider = _get_existing_tracer_provider()
    if tracer_provider is None:
        tracer_provider = register(
            endpoint=resolved_endpoint,
            project_name=resolved_project,
            api_key=resolved_api_key,
            auto_instrument=auto_instrument,
        )
        _LOGGER.info(
            "Phoenix tracing initialized for project '%s' targeting '%s'",
            resolved_project,
            resolved_endpoint,
        )
    else:
        _LOGGER.debug("Reusing existing OpenTelemetry tracer provider")

    _instrument_langchain(tracer_provider)

    return tracer_provider


def _instrument_langchain(tracer_provider: TracerProvider) -> None:
    """Instrument LangChain with the provided tracer provider once per process."""
    global _LANGCHAIN_INSTRUMENTED  # noqa: PLW0603

    if _LANGCHAIN_INSTRUMENTED:
        return

    LangChainInstrumentor().instrument(
        tracer_provider=tracer_provider,
        skip_dep_check=True,
    )
    _LANGCHAIN_INSTRUMENTED = True


def _resolve_project_name(explicit: str | None) -> str:
    """Resolve the Phoenix project name."""
    candidate = explicit or os.getenv(_PHOENIX_PROJECT_ENV)
    if candidate:
        return candidate.strip()
    return _DEFAULT_PROJECT_NAME


def _resolve_endpoint(explicit: str | None) -> str:
    """Resolve the Phoenix collector endpoint."""
    candidate = explicit or os.getenv(_PHOENIX_ENDPOINT_ENV)
    if candidate:
        return candidate.strip()
    return _DEFAULT_COLLECTOR_ENDPOINT


def _resolve_api_key(explicit: str | None) -> str:
    """Resolve the Phoenix API key."""
    candidate = (
        explicit
        or os.getenv(_PHOENIX_API_KEY_ENV)
        or os.getenv(_ALT_PHOENIX_API_KEY_ENV)
    )
    if candidate:
        return candidate.strip()
    return _DEFAULT_API_KEY


def _get_existing_tracer_provider() -> TracerProvider | None:
    """Return an existing SDK tracer provider if already configured."""
    provider = trace_api.get_tracer_provider()
    if isinstance(provider, TracerProvider):
        return provider
    return None


def _is_tracing_enabled() -> bool:
    """Determine whether Phoenix tracing should be configured."""
    explicit_flag = os.getenv(_PHOENIX_ENABLE_ENV)
    if explicit_flag is None:
        return True

    normalized = explicit_flag.strip().lower()
    if normalized in {"0", "false", "no", "off"}:
        return False
    if normalized in {"1", "true", "yes", "on"}:
        return True

    _LOGGER.warning(
        "Unrecognized value '%s' for %s. Defaulting to enabled.",
        explicit_flag,
        _PHOENIX_ENABLE_ENV,
    )
    return True


@contextmanager
def flow_builder_tracing_context(
    *,
    project_name: str | None = None,
    metadata: Mapping[str, Any] | None = None,
):
    """Context manager that applies Phoenix project and optional metadata.

    Ensures spans emitted within the block are associated with the correct
    Phoenix project and include any supplied metadata. Mirrors the behaviour
    used in the A2A agent service.
    """
    resolved_project = _resolve_project_name(project_name)

    with ExitStack() as stack:
        stack.enter_context(dangerously_using_project(project_name=resolved_project))
        if metadata:
            stack.enter_context(using_metadata(dict(metadata)))
        yield


__all__ = ["initialize_phoenix_tracing", "flow_builder_tracing_context"]
