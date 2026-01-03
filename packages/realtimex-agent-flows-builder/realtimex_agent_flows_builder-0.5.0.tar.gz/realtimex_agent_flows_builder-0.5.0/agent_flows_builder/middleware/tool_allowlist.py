"""Middleware to restrict the exposed tool surface to an allowlist."""

from collections.abc import Callable, Iterable

from langchain.agents.middleware.types import (
    AgentMiddleware,
    ModelRequest,
    ModelResponse,
)


class ToolAllowlistMiddleware(AgentMiddleware):
    """Filter tools passed to the model to an explicit allowlist."""

    def __init__(self, allowed_tools: Iterable[str]) -> None:
        super().__init__()
        self.allowed = set(allowed_tools)

    def _filter_request(self, request: ModelRequest) -> ModelRequest:
        filtered_tools = []
        for tool in request.tools:
            name = getattr(tool, "name", None)
            if name is None and isinstance(tool, dict):
                name = tool.get("name")
            if name in self.allowed:
                filtered_tools.append(tool)
        return request.override(tools=filtered_tools)

    def wrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], ModelResponse],
    ) -> ModelResponse:
        return handler(self._filter_request(request))

    async def awrap_model_call(
        self,
        request: ModelRequest,
        handler: Callable[[ModelRequest], ModelResponse],
    ) -> ModelResponse:
        return await handler(self._filter_request(request))
