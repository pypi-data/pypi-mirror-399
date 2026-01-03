"""Configuration models for the Agent Flows Builder."""

from dataclasses import dataclass


@dataclass(frozen=True)
class ModelProviderConfig:
    """Configuration for the language model provider.

    Attributes:
        api_key: The API key for authentication.
        base_path: The base URL of the API endpoint.
    """

    api_key: str
    base_path: str
