"""Middleware to inject live flow state into prompts via placeholders."""

from collections.abc import Callable
from typing import Any

from langchain.agents.middleware.types import (
    AgentMiddleware,
    ModelRequest,
    ModelResponse,
)

from agent_flows_builder.utils.file_operations import load_flow_json
from agent_flows_builder.utils.flow_state import PLACEHOLDER_REGISTRY, FlowConfig


class ContextInjectionMiddleware(AgentMiddleware):
    """Replace flow state placeholders in system prompts with live values.

    Supported placeholders come from `utils.flow_state.PLACEHOLDER_REGISTRY`
    (e.g., {{FLOW_GRAPH}}, {{FLOW_STATE}}, {{FLOW_VARIABLES}}, {{FLOW_STEP_IDS}}).
    """

    def __init__(
        self,
        *,
        placeholder_registry: dict[str, Callable[[FlowConfig], str]] | None = None,
        target_placeholders: list[str] | None = None,
        flow_loader: Callable[[dict[str, Any]], dict[str, Any] | None] | None = None,
    ) -> None:
        super().__init__()
        self.placeholder_registry = placeholder_registry or PLACEHOLDER_REGISTRY
        self.target_placeholders = (
            set(target_placeholders) if target_placeholders else None
        )
        self.flow_loader = flow_loader or _default_flow_loader

    def wrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], ModelResponse],
    ) -> ModelResponse:
        prompt = self._inject_prompt(request)
        if prompt is not None:
            request = request.override(system_prompt=prompt)
        return handler(request)

    async def awrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], Any],
    ) -> ModelResponse:
        prompt = self._inject_prompt(request)
        if prompt is not None:
            request = request.override(system_prompt=prompt)
        return await handler(request)

    def _inject_prompt(self, request: ModelRequest) -> str | None:
        system_prompt = request.system_prompt or ""
        runtime = getattr(request, "runtime", None)
        if not system_prompt or runtime is None:
            return None

        # Debug: show runtime/state snapshot before attempting load
        runtime_state = (
            getattr(runtime, "state", {}) if hasattr(runtime, "state") else {}
        )
        request_state = (
            getattr(request, "state", {}) if hasattr(request, "state") else {}
        )
        # Prefer request.state (contains files) over runtime.state
        state = request_state if isinstance(request_state, dict) else runtime_state

        flow_dict = self.flow_loader(state)
        if not flow_dict:
            return None

        flow_cfg = FlowConfig.from_dict(flow_dict)
        updated = system_prompt
        replaced_any = False
        for placeholder, formatter in self.placeholder_registry.items():
            if self.target_placeholders and placeholder not in self.target_placeholders:
                continue
            if placeholder in updated:
                updated = updated.replace(placeholder, formatter(flow_cfg))
                replaced_any = True

        if replaced_any:
            return updated
        return None


def _default_flow_loader(state: dict[str, Any]) -> dict[str, Any] | None:
    """Load /flow.json from state using shared flow loader."""
    files = state.get("files", {}) if isinstance(state, dict) else {}
    raw = files.get("/flow.json")
    if raw is None:
        return None
    try:
        return load_flow_json(raw)
    except Exception:  # pragma: no cover
        return None
