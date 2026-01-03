"""SQLite checkpointer implementation for Agent Flows Builder.

Provides SQLite-based conversation history persistence for local workflows.
"""

from pathlib import Path

from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver


def create_sqlite_checkpointer(workspace: Path | str | None = None) -> AsyncSqliteSaver:
    """Create async SQLite checkpointer context manager.

    Args:
        workspace: Directory for storing the SQLite database file.
                  If None, uses current working directory.

    Returns:
        AsyncSqliteSaver context manager ready for use with LangGraph agents.

    Usage:
        ```python
        from agent_flows_builder import create_sqlite_checkpointer

        async with create_sqlite_checkpointer() as saver:
            graph = builder.compile(checkpointer=saver)
            # Use graph with checkpointer
        ```

    Note:
        Database file will be created at: workspace/chat_history.db
        Uses aiosqlite for async database operations compatible with FastAPI streaming.
    """
    if workspace is None:
        workspace = Path.cwd()
    elif isinstance(workspace, str):
        workspace = Path(workspace)

    # Ensure workspace directory exists
    workspace.mkdir(parents=True, exist_ok=True)

    # SQLite database file in workspace
    db_path = workspace / "chat_history.db"

    return AsyncSqliteSaver.from_conn_string(str(db_path))
