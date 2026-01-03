"""Resource package exposing packaged documentation helpers."""

from .loaders import (
    DOCS_RESOURCE_PACKAGE,
    ResourceInfo,
    ensure_resources_available,
    get_agent_workspace,
    get_package_docs_path,
)

__all__ = [
    "DOCS_RESOURCE_PACKAGE",
    "ResourceInfo",
    "ensure_resources_available",
    "get_agent_workspace",
    "get_package_docs_path",
]
