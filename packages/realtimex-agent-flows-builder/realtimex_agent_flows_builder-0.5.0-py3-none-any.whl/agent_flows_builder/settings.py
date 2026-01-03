"""Runtime configuration objects for Agent Flows Builder."""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass


@dataclass(frozen=True)
class AgentModelConfig:
    """Model parameters used by a single agent instance."""

    model: str
    temperature: float
    max_tokens: int


@dataclass(frozen=True)
class AgentSettings:
    """Aggregated runtime settings for the master agent and specialists."""

    master: AgentModelConfig
    research: AgentModelConfig
    validator: AgentModelConfig
    recursion_limit: int

    @classmethod
    def from_env(cls, env: Mapping[str, str] | None = None) -> AgentSettings:
        """Build settings from environment variables or an explicit mapping."""
        source = os.environ if env is None else env

        master = _model_from_env(
            source,
            model_key="AGENT_MAIN_MODEL",
            temperature_key="AGENT_MAIN_TEMPERATURE",
            tokens_key="AGENT_MAIN_MAX_TOKENS",
            default_model=DEFAULT_MAIN_MODEL,
            default_temperature=DEFAULT_MAIN_TEMPERATURE,
            default_tokens=DEFAULT_MAIN_MAX_TOKENS,
        )
        research = _model_from_env(
            source,
            model_key="AGENT_RESEARCH_MODEL",
            temperature_key="AGENT_RESEARCH_TEMPERATURE",
            tokens_key="AGENT_RESEARCH_MAX_TOKENS",
            default_model=DEFAULT_RESEARCH_MODEL,
            default_temperature=DEFAULT_RESEARCH_TEMPERATURE,
            default_tokens=DEFAULT_RESEARCH_MAX_TOKENS,
        )
        validator = _model_from_env(
            source,
            model_key="AGENT_FLOW_VALIDATOR_MODEL",
            temperature_key="AGENT_FLOW_VALIDATOR_TEMPERATURE",
            tokens_key="AGENT_FLOW_VALIDATOR_MAX_TOKENS",
            default_model=DEFAULT_FLOW_VALIDATOR_MODEL,
            default_temperature=DEFAULT_FLOW_VALIDATOR_TEMPERATURE,
            default_tokens=DEFAULT_FLOW_VALIDATOR_MAX_TOKENS,
        )
        recursion_limit = _get_int(
            source,
            key="AGENT_RECURSION_LIMIT",
            default=DEFAULT_RECURSION_LIMIT,
        )

        return cls(
            master=master,
            research=research,
            validator=validator,
            recursion_limit=recursion_limit,
        )


def _model_from_env(
    env: Mapping[str, str],
    *,
    model_key: str,
    temperature_key: str,
    tokens_key: str,
    default_model: str,
    default_temperature: float,
    default_tokens: int,
) -> AgentModelConfig:
    return AgentModelConfig(
        model=_get_str(env, model_key, default_model),
        temperature=_get_float(env, temperature_key, default_temperature),
        max_tokens=_get_int(env, tokens_key, default_tokens),
    )


def _get_str(env: Mapping[str, str], key: str, default: str) -> str:
    raw = _get_raw(env, key)
    return raw if raw is not None else default


def _get_float(env: Mapping[str, str], key: str, default: float) -> float:
    raw = _get_raw(env, key)
    if raw is None:
        return default
    try:
        return float(raw)
    except ValueError as exc:  # pragma: no cover - defensive guard
        raise ValueError(
            f"Environment variable '{key}' must be a valid float."
        ) from exc


def _get_int(env: Mapping[str, str], key: str, default: int) -> int:
    raw = _get_raw(env, key)
    if raw is None:
        return default
    try:
        return int(raw)
    except ValueError as exc:  # pragma: no cover - defensive guard
        raise ValueError(
            f"Environment variable '{key}' must be a valid integer."
        ) from exc


def _get_raw(env: Mapping[str, str], key: str) -> str | None:
    value = env.get(key)
    if value is None:
        return None
    stripped = value.strip()
    return stripped if stripped else None


DEFAULT_MAIN_MODEL = "gpt-4.1-mini"
DEFAULT_MAIN_TEMPERATURE = 0.1
DEFAULT_MAIN_MAX_TOKENS = 8192

DEFAULT_RESEARCH_MODEL = "gpt-4.1-mini"
DEFAULT_RESEARCH_TEMPERATURE = 0.1
DEFAULT_RESEARCH_MAX_TOKENS = 8192

DEFAULT_FLOW_VALIDATOR_MODEL = "gpt-4.1-nano"
DEFAULT_FLOW_VALIDATOR_TEMPERATURE = 0.0
DEFAULT_FLOW_VALIDATOR_MAX_TOKENS = 4096

DEFAULT_RECURSION_LIMIT = 1000


__all__ = [
    "AgentModelConfig",
    "AgentSettings",
    "DEFAULT_FLOW_VALIDATOR_MAX_TOKENS",
    "DEFAULT_FLOW_VALIDATOR_MODEL",
    "DEFAULT_FLOW_VALIDATOR_TEMPERATURE",
    "DEFAULT_MAIN_MAX_TOKENS",
    "DEFAULT_MAIN_MODEL",
    "DEFAULT_MAIN_TEMPERATURE",
    "DEFAULT_RECURSION_LIMIT",
    "DEFAULT_RESEARCH_MAX_TOKENS",
    "DEFAULT_RESEARCH_MODEL",
    "DEFAULT_RESEARCH_TEMPERATURE",
]
