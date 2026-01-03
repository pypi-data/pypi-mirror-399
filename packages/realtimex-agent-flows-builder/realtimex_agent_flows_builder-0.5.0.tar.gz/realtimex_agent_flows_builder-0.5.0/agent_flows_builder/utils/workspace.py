# ruff: noqa: PLW0603
"""Global workspace management for Agent Flows Builder.

Provides a centralized mechanism to set and access the workspace directory
across all file tools and operations.
"""

from pathlib import Path

# Global workspace variable
_workspace: Path | None = None


def set_workspace(workspace: Path | str | None = None) -> Path:
    """Set the global workspace directory.

    Args:
        workspace: Directory path to use as workspace. If None, uses current working directory.

    Returns:
        The resolved workspace Path object.
    """
    global _workspace

    if workspace is None:
        _workspace = Path.cwd()
    elif isinstance(workspace, str):
        _workspace = Path(workspace)
    else:
        _workspace = workspace

    # Resolve to absolute path
    _workspace = _workspace.resolve()
    return _workspace


def get_workspace() -> Path:
    """Get the current global workspace directory.

    Returns:
        The current workspace Path object. Defaults to current working directory if not set.
    """
    global _workspace

    if _workspace is None:
        _workspace = Path.cwd().resolve()

    return _workspace


def clear_workspace() -> None:
    """Clear the global workspace setting.

    After calling this, get_workspace() will return the current working directory.
    """
    global _workspace
    _workspace = None
