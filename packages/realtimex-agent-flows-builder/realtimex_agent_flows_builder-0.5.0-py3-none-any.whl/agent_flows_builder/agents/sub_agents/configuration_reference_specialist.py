"""DEPRECATED: Configuration Reference Specialist Agent for comprehensive parameter documentation.

This module contains the configuration reference specialist that provides exhaustive
parameter documentation for workflow executors without making configuration recommendations.

This module is deprecated and will be removed in a future release.
"""

from collections.abc import Callable

from deepagents.middleware.filesystem import FilesystemMiddleware
from deepagents.middleware.patch_tool_calls import PatchToolCallsMiddleware
from deepagents.middleware.subagents import CompiledSubAgent
from langchain.agents import create_agent

from agent_flows_builder.config.settings import ModelProviderConfig
from agent_flows_builder.middleware import ToolAllowlistMiddleware
from agent_flows_builder.prompts import CONFIGURATION_REFERENCE_SPECIALIST_PROMPT
from agent_flows_builder.settings import AgentSettings
from agent_flows_builder.utils.models import create_chat_model


def create_configuration_reference_specialist(
    provider_config: ModelProviderConfig,
    settings: AgentSettings | None = None,
    backend_factory: Callable | None = None,
) -> CompiledSubAgent:
    """Create configuration reference specialist sub-agent configuration.

    DEPRECATED: This function is deprecated and will be removed in a future release.

    The configuration reference specialist handles:
    - Comprehensive parameter documentation for all executor types
    - Machine-readable configuration references with complete coverage
    - Zero-opinion technical documentation for informed decision making

    Args:
        provider_config: Model provider configuration shared with the master agent.
        settings: Optional runtime settings override used to configure the specialist.
        backend_factory: Backend factory to share the same filesystem routing as the master agent.

    Returns:
        CompiledSubAgent specification for configuration reference specialist
    """
    agent_settings = settings or AgentSettings.from_env()

    # Create configured chat model
    chat_model = create_chat_model(
        model=agent_settings.research.model,
        provider_config=provider_config,
        temperature=agent_settings.research.temperature,
        max_tokens=agent_settings.research.max_tokens,
        parallel_tool_calls=False,
    )

    # Build minimal compiled subagent with only read_file exposed
    specialist_graph = create_agent(
        model=chat_model,
        tools=[],  # FilesystemMiddleware injects filesystem tools
        system_prompt=CONFIGURATION_REFERENCE_SPECIALIST_PROMPT,
        middleware=[
            FilesystemMiddleware(
                backend=backend_factory,
                system_prompt="",
            ),
            ToolAllowlistMiddleware(["read_file"]),
            PatchToolCallsMiddleware(),
        ],
    )

    return {
        "name": "configuration-reference-specialist",
        "description": "Comprehensive parameter documentation specialist providing exhaustive configuration references for workflow executors. Documents every parameter, constraint, and option without making configuration recommendations.",
        "runnable": specialist_graph,
    }
