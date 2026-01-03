"""Configuration Expert Sub-Agent for actionable executor templates.

This module contains the Configuration Expert sub-agent that transforms
executor documentation into ready-to-use JSON templates with context-aware
guidance. Supports both single and batch requests.
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
from agent_flows_builder.prompts.config_expert import CONFIGURATION_EXPERT_PROMPT
from agent_flows_builder.settings import AgentSettings
from agent_flows_builder.utils.models import create_chat_model


def create_configuration_expert(
    provider_config: ModelProviderConfig,
    settings: AgentSettings | None = None,
    backend_factory: Callable | None = None,
) -> CompiledSubAgent:
    """Create configuration expert sub-agent for actionable executor templates.

    The configuration expert handles:
    - Reading executor documentation
    - Building ready-to-use JSON templates
    - Providing context-aware interpolation hints
    - Processing batch requests for multiple executors

    Args:
        provider_config: Model provider configuration shared with the master agent.
        settings: Optional runtime settings override.
        backend_factory: Backend factory to share filesystem routing with master agent.

    Returns:
        CompiledSubAgent specification for configuration expert
    """
    agent_settings = settings or AgentSettings.from_env()

    chat_model = create_chat_model(
        model=agent_settings.research.model,
        provider_config=provider_config,
        temperature=0,  # Zero creativity — factual templates only
        max_tokens=agent_settings.research.max_tokens,
        parallel_tool_calls=False,
    )

    expert_graph = create_agent(
        model=chat_model,
        tools=[],  # FilesystemMiddleware injects filesystem tools
        system_prompt=CONFIGURATION_EXPERT_PROMPT,
        middleware=[
            FilesystemMiddleware(
                backend=backend_factory,
                system_prompt="",
            ),
            ContextInjectionMiddleware(target_placeholders=["{{FLOW_VARIABLES}}"]),
            ToolAllowlistMiddleware(["read_file"]),
            PatchToolCallsMiddleware(),
        ],
    )

    return {
        "name": "configuration-expert",
        "description": (
            "Executor template specialist. Provide: executor type and usage context. "
            "Returns ready-to-use JSON template with parameter guidance and interpolation hints. "
            "Supports batch requests for multiple executors."
        ),
        "runnable": expert_graph,
    }
