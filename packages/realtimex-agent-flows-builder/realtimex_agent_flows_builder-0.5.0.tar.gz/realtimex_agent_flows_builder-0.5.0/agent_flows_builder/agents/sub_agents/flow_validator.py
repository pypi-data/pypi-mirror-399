"""Flow Validator Agent for comprehensive flow configuration validation.

This module contains the flow validator specialist that performs structural correctness
and variable consistency validation without making configuration recommendations.
"""

from collections.abc import Callable

from deepagents.middleware.filesystem import FilesystemMiddleware
from deepagents.middleware.patch_tool_calls import PatchToolCallsMiddleware
from deepagents.middleware.subagents import CompiledSubAgent
from langchain.agents import create_agent

from agent_flows_builder.config.settings import ModelProviderConfig
from agent_flows_builder.middleware import ToolAllowlistMiddleware
from agent_flows_builder.prompts import FLOW_VALIDATOR_PROMPT
from agent_flows_builder.settings import AgentSettings
from agent_flows_builder.tools.flow_validation import validate_flow_configuration
from agent_flows_builder.utils.models import create_chat_model


def create_flow_validator(
    provider_config: ModelProviderConfig,
    settings: AgentSettings | None = None,
    backend_factory: Callable | None = None,
) -> CompiledSubAgent:
    """Create flow validator specialist as custom sub-agent.

    The flow validator specialist handles:
    - Comprehensive validation of /flow.json structural correctness
    - Variable reference consistency checking across workflow steps
    - Schema compliance validation using Agent Flows Python package
    - Machine-readable validation reports with specific issue locations

    Args:
        provider_config: Model provider configuration shared with the master agent.
        settings: Optional runtime settings override used to configure the specialist.
        backend_factory: Optional backend factory to share routing with master agent.

    Returns:
        CompiledSubAgent specification for flow validator specialist
    """
    agent_settings = settings or AgentSettings.from_env()

    # Create configured chat model
    chat_model = create_chat_model(
        model=agent_settings.validator.model,
        provider_config=provider_config,
        temperature=agent_settings.validator.temperature,
        max_tokens=agent_settings.validator.max_tokens,
        parallel_tool_calls=False,
    )

    validator_graph = create_agent(
        model=chat_model,
        tools=[validate_flow_configuration],
        system_prompt=FLOW_VALIDATOR_PROMPT,
        middleware=[
            FilesystemMiddleware(backend=backend_factory, system_prompt=""),
            ToolAllowlistMiddleware(["validate_flow_configuration"]),
            PatchToolCallsMiddleware(),
        ],
    )

    return {
        "name": "flow-validator",
        "description": "Flow configuration validation specialist that validates /flow.json structural correctness and variable consistency. Reports validation issues without making configuration recommendations.",
        "runnable": validator_graph,
    }
