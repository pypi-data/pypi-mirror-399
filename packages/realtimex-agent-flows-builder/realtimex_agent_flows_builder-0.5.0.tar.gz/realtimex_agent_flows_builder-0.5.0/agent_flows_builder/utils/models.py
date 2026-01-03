"""Model initialization utilities for Agent Flows Builder."""

from typing import Any

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_openai import ChatOpenAI

from agent_flows_builder.config.settings import ModelProviderConfig


def create_chat_model(
    model: str,
    provider_config: ModelProviderConfig | None = None,
    *,
    parallel_tool_calls: bool | None = None,
    **kwargs: Any,
) -> BaseChatModel:
    """Create a configured chat model.

    This function initializes a chat model that can connect to any OpenAI-compatible API endpoint.
    It uses the ChatOpenAI client to send requests, allowing for consistent API interaction
    with custom or third-party LLM hosts.

    Args:
        model: The name of the model to use (e.g., "gpt-4-turbo", "custom-model-name").
        provider_config: Configuration for the model provider, including API key and base URL.
        **kwargs: Additional options to pass to the ChatOpenAI constructor, such as:
                  - temperature: Controls response randomness.
                  - max_tokens: Maximum tokens in the response.
                  - timeout: Request timeout in seconds.

    Returns:
        A configured BaseChatModel instance ready for use.

    Examples:
        from agent_flows_builder.config.settings import ModelProviderConfig

        # Configure for a custom LLM host
        custom_provider = ModelProviderConfig(
            api_key="your-secret-api-key",
            base_path="https://your-custom-llm-host.com/v1"
        )

        # Create a model instance
        chat_model = create_chat_model(
            model="your-custom-model",
            provider_config=custom_provider,
            temperature=0.7
        )
    """
    if parallel_tool_calls is not None:
        model_kwargs = kwargs.pop("model_kwargs", {})
        kwargs["model_kwargs"] = {
            **model_kwargs,
            "parallel_tool_calls": parallel_tool_calls,
        }

    return ChatOpenAI(
        model=model,
        openai_api_key=provider_config.api_key,
        openai_api_base=provider_config.base_path,
        **kwargs,
    )
