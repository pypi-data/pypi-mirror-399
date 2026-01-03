"""Filesystem helpers for Agent Flows Builder."""

from deepagents.backends import CompositeBackend, FilesystemBackend, StateBackend

from agent_flows_builder.resources import ResourceInfo


def create_composite_backend(resources: ResourceInfo, runtime) -> CompositeBackend:
    """Create hybrid backend routing scratchpad to state and docs/skills to real filesystem."""
    routes: dict[str, FilesystemBackend] = {
        "/docs/": FilesystemBackend(
            root_dir=resources.docs_dir,
            virtual_mode=True,
        ),
    }
    if resources.skills_dir and resources.skills_dir.exists():
        routes["/skills/"] = FilesystemBackend(
            root_dir=resources.skills_dir,
            virtual_mode=True,
        )

    return CompositeBackend(
        default=StateBackend(runtime),
        routes=routes,
    )
