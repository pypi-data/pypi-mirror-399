"""Flow Architect Sub-Agent for high-level workflow design.

This module contains the Flow Architect sub-agent that produces high-level
design documents specifying WHAT to build (executor sequence, data flow,
control structures) without configuring HOW.
"""

from collections.abc import Callable

from deepagents.middleware.filesystem import FilesystemMiddleware
from deepagents.middleware.patch_tool_calls import PatchToolCallsMiddleware
from deepagents.middleware.subagents import CompiledSubAgent
from langchain.agents import create_agent

from agent_flows_builder.config.settings import ModelProviderConfig
from agent_flows_builder.middleware import (
    ContextInjectionMiddleware,
    ToolAllowlistMiddleware,
)
from agent_flows_builder.prompts.flow_architect import FLOW_ARCHITECT_PROMPT
from agent_flows_builder.settings import AgentSettings
from agent_flows_builder.utils.models import create_chat_model


def create_flow_architect(
    provider_config: ModelProviderConfig,
    settings: AgentSettings | None = None,
    backend_factory: Callable | None = None,  # noqa: ARG001 - kept for interface consistency
) -> CompiledSubAgent:
    """Create flow architect sub-agent for high-level flow design.

    The flow architect handles:
    - Analyzing user requirements and decomposing into flow structures
    - Pattern recognition (list processing, conditionals, etc.)
    - Producing design documents for the Master Agent to implement

    Args:
        provider_config: Model provider configuration shared with the master agent.
        settings: Optional runtime settings override.
        backend_factory: Unused, kept for interface consistency with other sub-agents.

    Returns:
        CompiledSubAgent specification for flow architect
    """
    agent_settings = settings or AgentSettings.from_env()

    # Create configured chat model
    # Use research model settings — architect needs reasoning capability
    # Temperature slightly higher for creative design work
    chat_model = create_chat_model(
        model=agent_settings.research.model,
        provider_config=provider_config,
        temperature=0.3,  # Slightly creative for design decisions
        max_tokens=agent_settings.research.max_tokens,
        parallel_tool_calls=False,
    )

    # Build pure reasoning subagent — no tools needed
    architect_graph = create_agent(
        model=chat_model,
        tools=[],  # FilesystemMiddleware injects filesystem tools
        system_prompt=FLOW_ARCHITECT_PROMPT,
        middleware=[
            FilesystemMiddleware(
                backend=backend_factory,
                system_prompt="",
            ),
            ContextInjectionMiddleware(
                target_placeholders=["{{FLOW_GRAPH}}", "{{FLOW_VARIABLES}}"]
            ),
            ToolAllowlistMiddleware(["read_file"]),
            PatchToolCallsMiddleware(),
        ],
    )

    return {
        "name": "flow-architect",
        "description": (
            "Strategic flow designer. Analyzes requirements and produces high-level "
            "design documents specifying WHAT to build (executor sequence, data flow, "
            "control structures) without configuring HOW. Delegate before building any steps."
        ),
        "runnable": architect_graph,
    }
