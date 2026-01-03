"""Prompt accessors for Agent Flows Builder."""

from .config_expert import CONFIGURATION_EXPERT_PROMPT
from .config_reference import CONFIGURATION_REFERENCE_SPECIALIST_PROMPT
from .flow_architect import FLOW_ARCHITECT_PROMPT
from .flow_validator import FLOW_VALIDATOR_PROMPT
from .master import FLOW_BUILDER_MASTER_PROMPT

__all__ = [
    "CONFIGURATION_REFERENCE_SPECIALIST_PROMPT",
    "CONFIGURATION_EXPERT_PROMPT",
    "FLOW_ARCHITECT_PROMPT",
    "FLOW_BUILDER_MASTER_PROMPT",
    "FLOW_VALIDATOR_PROMPT",
]
