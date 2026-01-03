"""
Agent Flows Builder

A Deep Agents-based system for building Agent Flows via natural language.
Translates user requirements into structured JSON workflow configurations.

Usage:
    from agent_flows_builder import create_flow_builder_agent

    # Create agent instance
    agent = create_flow_builder_agent()

    # Build workflow from natural language
    result = agent.invoke({
        "messages": [{"role": "user", "content": "Create a workflow that processes API data with AI"}]
    })

    # Stream responses
    for chunk in agent.stream({"messages": [{"role": "user", "content": "Build API workflow"}]}):
        print(chunk)
"""

from .agents.flow_builder_master import create_flow_builder_agent
from .checkpointers import create_sqlite_checkpointer

__all__ = ["create_flow_builder_agent", "create_sqlite_checkpointer"]
