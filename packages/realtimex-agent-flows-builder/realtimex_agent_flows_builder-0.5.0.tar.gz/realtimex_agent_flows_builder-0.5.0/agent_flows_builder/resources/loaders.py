"""Helpers for accessing bundled documentation and workspace resources."""

from __future__ import annotations

import importlib.resources
import os
import shutil
import tempfile
from dataclasses import dataclass
from pathlib import Path

DOCS_RESOURCE_PACKAGE = "agent_flows_builder.resources"


@dataclass
class ResourceInfo:
    """Structured resource info for workspace assets."""

    workspace: Path
    docs_dir: Path
    skills_dir: Path
    all_available: bool
    missing: list[str]


def get_agent_workspace() -> Path:
    """Resolve the directory used to stage agent assets during execution."""
    if workspace := os.getenv("AGENT_FLOWS_WORKSPACE"):
        workspace_path = Path(workspace).resolve()
        workspace_path.mkdir(parents=True, exist_ok=True)
        return workspace_path

    return Path(tempfile.mkdtemp(prefix="agent-flows-"))


def _get_package_docs_directory() -> Path | None:
    """Return the packaged documentation directory if available."""
    try:
        with importlib.resources.as_file(
            importlib.resources.files(DOCS_RESOURCE_PACKAGE) / "docs"
        ) as docs_path:
            return docs_path if docs_path.exists() else None
    except Exception:
        return None


def _get_package_skills_directory() -> Path | None:
    """Return the packaged skills directory if available."""
    try:
        with importlib.resources.as_file(
            importlib.resources.files(DOCS_RESOURCE_PACKAGE) / "skills"
        ) as skills_path:
            return skills_path if skills_path.exists() else None
    except Exception:
        return None


def _ensure_resource(
    package_path: Path | None, target: Path, *, force_update: bool
) -> bool:
    """Generic copy helper for packaged resources."""
    if not force_update and target.exists() and target.is_dir():
        return True
    if package_path is None:
        return False
    try:
        if target.exists():
            shutil.rmtree(target)
        shutil.copytree(package_path, target, dirs_exist_ok=True)
        return True
    except Exception as exc:  # pragma: no cover - defensive guard
        print(f"Warning: Could not extract resources to {target}: {exc}")
        return False


def ensure_resources_available(
    workspace: Path | str | None = None,
    *,
    force_update: bool = True,
) -> ResourceInfo:
    """Ensure packaged docs and skills exist within the target workspace.

    Returns:
        (all_available, workspace_path, missing_resources)
    """
    workspace_path = Path(workspace).resolve() if workspace else Path.cwd()

    docs_ok = _ensure_resource(
        _get_package_docs_directory(),
        workspace_path / "docs",
        force_update=force_update,
    )
    skills_ok = _ensure_resource(
        _get_package_skills_directory(),
        workspace_path / "skills",
        force_update=force_update,
    )

    missing: list[str] = []
    if not docs_ok:
        missing.append("docs")
    if not skills_ok:
        missing.append("skills")

    return ResourceInfo(
        workspace=workspace_path,
        docs_dir=workspace_path / "docs",
        skills_dir=workspace_path / "skills",
        all_available=not missing,
        missing=missing,
    )


def get_package_docs_path() -> Path | None:
    """Expose the path to bundled documentation for development workflows."""
    return _get_package_docs_directory()


__all__ = [
    "DOCS_RESOURCE_PACKAGE",
    "ensure_resources_available",
    "get_agent_workspace",
    "get_package_docs_path",
]
