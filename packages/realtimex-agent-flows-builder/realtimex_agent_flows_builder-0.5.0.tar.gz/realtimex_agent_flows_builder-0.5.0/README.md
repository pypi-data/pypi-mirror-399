# Agent Flows Builder

> **AI Agent that builds workflow automations via natural language**

## Overview

AI Agent that constructs workflow automations through natural language descriptions, making complex workflow building accessible without JSON expertise. Transform plain English requirements into complete, executable workflow configurations.

## Features

- **Natural Language Interface**: Describe workflows in plain English
- **8 Executor Types**: API calls, LLM processing, web scraping, conditionals, loops, switches, and more
- **Smart Pattern Matching**: Finds and adapts existing workflow templates from documentation
- **Real Filesystem Tools**: Works with actual files and project documentation
- **Research Specialist**: Handles complex integration analysis when needed
- **State Management**: Persistent conversation state across workflow building sessions
- **Sub-agent Delegation**: Specialized agents for complex pattern analysis

## Versioning

The package follows semantic versioning with a single source of truth in `_version.py`:

```python
from agent_flows_builder._version import APP_VERSION

print(APP_VERSION)  # Static constant: 1.0.0
```

## Architecture

- **Master Agent**: Primary workflow builder handling most tasks directly
- **Research Specialist**: Analyzes complex multi-executor integration patterns
- **Built-in Tools**: File system access, pattern search, documentation analysis
- **Planning System**: Task breakdown and progress tracking

## Installation

### As a Package (Recommended for Integration)

```bash
# Install from Git repository
pip install git+https://rtgit.rta.vn/rtlab/rtwebteam/realtimex-agent-flows-builder.git

# Or with uv
uv add git+https://rtgit.rta.vn/rtlab/rtwebteam/realtimex-agent-flows-builder.git
```

### Environment Setup
```bash
# Create .env file in your project
REALTIMEX_AI_BASE_PATH=https://realtimexai-llm-provider.realtimex.ai
REALTIMEX_AI_API_KEY=your_realtimex_api_key_here
MCP_ACI_API_KEY=your_mcp_api_key_here
MCP_ACI_LINKED_ACCOUNT_OWNER_ID=your_mcp_account_owner_id

# Optional model configuration overrides
AGENT_MAIN_MODEL=gpt-4.1-mini
AGENT_MAIN_TEMPERATURE=0.1
AGENT_MAIN_MAX_TOKENS=8192
AGENT_RESEARCH_MODEL=gpt-4.1-mini
AGENT_RESEARCH_TEMPERATURE=0
AGENT_RESEARCH_MAX_TOKENS=8192
AGENT_FLOW_VALIDATOR_MODEL=gpt-4.1-mini
AGENT_FLOW_VALIDATOR_MAX_TOKENS=4096
AGENT_RECURSION_LIMIT=1000
```

### For Development

Prerequisites: Python 3.11+, uv package manager

```bash
# Clone and install
git clone <repository-url>
cd agent-flows-builder

# Install production dependencies
uv sync

# Install with development dependencies (required for langgraph dev)
uv sync --group dev

# Environment setup
cp .env.example .env
# Populate REALTIMEX_AI_* and MCP_ACI_* with your credentials

# Phoenix tracing (enabled by default via RealTimeX host & API key)
# export PHOENIX_API_KEY=override_key                  # optional: custom key
# export PHOENIX_PROJECT_NAME=my-project               # optional: custom project name
# export PHOENIX_COLLECTOR_ENDPOINT=https://custom/v1/traces
# export AGENT_FLOWS_ENABLE_PHOENIX_TRACING=false      # disable tracing entirely
```

## Usage

### Integration in Your Project

```python
from agent_flows_builder import create_flow_builder_agent

# Required API configuration
REALTIMEX_BASE_PATH = "https://your-api-endpoint.com/v1"
REALTIMEX_API_KEY = "your_secret_api_key"

# Create the agent
agent = create_flow_builder_agent(
    realtimex_ai_base_path=REALTIMEX_BASE_PATH,
    realtimex_ai_api_key=REALTIMEX_API_KEY,
)

# Build a workflow from natural language
result = agent.invoke({
    "messages": [{"role": "user", "content": "Create a workflow that gets news from an API, analyzes it with AI, and posts summaries to Slack"}]
})

# Access the generated workflow files
files = result.get("files", {})
if "flow.json" in files:
    flow_config = files["flow.json"]  # Your complete workflow configuration

# Stream responses for real-time feedback
for chunk in agent.stream({"messages": [{"role": "user", "content": "Build API workflow"}]}):
    if "messages" in chunk:
        print(chunk["messages"][-1].content)
```

### Interactive Development
```bash
# Start development server with graph visualization
langgraph dev
```

## Example Workflows

The agent can build workflows for:
- **API Integration**: Fetch data → Process → Deliver
- **Content Analysis**: Scrape → Analyze → Summarize → Distribute  
- **Data Processing**: Import → Transform → Validate → Export
- **Notification Systems**: Monitor → Evaluate → Alert → Log

## Development

### Environment Setup
```bash
# Install with development dependencies
uv sync --group dev

# Activate environment  
uv shell
```

### Development Server
```bash
# Start interactive development with graph visualization
langgraph dev

# This provides:
# - Interactive agent testing
# - Graph execution visualization  
# - State inspection
# - Real-time debugging
```

### Code Quality
```bash
# Format code
uv run ruff format .

# Check types
uv run mypy agent_flows_builder/

# Run linter
uv run ruff check .

# Run tests
uv run pytest
```

### Project Structure
```
agent_flows_builder/
├── agents/           # Master agent factory and specialist builders
├── checkpointers/    # Checkpointer implementations (e.g., SQLite)
├── config/           # Provider configuration models
├── prompts/          # Prompt templates for the master and specialists
├── resources/        # Bundled documentation and workspace helpers
├── tools/            # Filesystem, validation, and discovery tools
├── utils/            # Shared utilities (file ops, model helpers)
├── settings.py       # Typed runtime settings facade
```

### Adding Features

#### Custom Tools
```python
from langchain.tools import tool

@tool
def custom_workflow_tool(input: str) -> str:
    """Tool description for agent"""
    # Implementation
    return result
```

#### Agent Configuration
```python
from deepagents import create_deep_agent

agent = create_deep_agent(
    tools=[your_tools],
    instructions=your_prompt,
    subagents=[specialized_agents]  # Optional
)
```

### Testing
```bash
# Run all tests
uv run pytest

# Test specific workflow patterns
uv run pytest tests/test_workflow_patterns.py

# With coverage
uv run pytest --cov=agent_flows_builder
```

### Code Conventions
- **Type Hints**: Required for all functions
- **Docstrings**: Google-style for public APIs
- **Error Handling**: Explicit error types with context
- **Tool Naming**: Descriptive names for agent clarity

## Contributing

1. Follow existing patterns in codebase
2. Test with real workflow examples  
3. Ensure agent-readable documentation
4. Validate generated workflows work correctly
5. Use `langgraph dev` for interactive development

---

**Built with [Deep Agents](https://github.com/langchain-ai/deepagents)**
