---
name: designing-flows
description: Flow design patterns and first-principles guidance. Provides pattern recognition tables for common workflow structures (list processing, conditional routing, AI processing) and decomposition strategies for complex requests. Helps identify the right executors and control flow for user requirements.
---

# Flow Design Guide

## Pattern Recognition

| User Says | Pattern | Key Executors |
|-----------|---------|---------------|
| "for each", "process each", "iterate" | List Processing | apiCall → loop → (nested steps) → finish |
| "if...then", "when X do Y" | Conditional | conditional → (true/false branches) |
| "based on type", "route to", "depending on" | Switch/Router | switch → (multiple cases) |
| "summarize", "analyze", "generate", "extract" | AI Processing | llmInstruction |
| "fetch from", "call API", "get data" | Data Retrieval | apiCall |
| "send to Slack/Gmail", "notify", "email" | External Integration | mcpServerAction |
| "scrape", "extract from page" | Web Extraction | webScraping |

## First Principles Design

When no pattern matches, derive from fundamentals:

1. **Identify Inputs**: What data enters the flow?
2. **Identify Outputs**: What should the flow produce?
3. **Map Transformations**: What must happen between input and output?
4. **Add Control Flow**: Any iteration, branching, or routing needed?

## Composite Patterns

Complex requests combine patterns:

| User Request | Decomposition |
|--------------|---------------|
| "For each item, if it matches criteria, send an email" | List Processing + Conditional + MCP Integration |
| "Fetch data, route by type, process each differently" | Data Retrieval + Switch + Multiple processors |
| "Scrape articles, summarize each, save results" | Web Extraction + Loop + AI Processing |

Always decompose into sub-patterns and design each before implementation.

## Flow Structure Rules

1. **Start with `flow_variables`**: Every flow begins with variable definitions
2. **End with `finish`**: Every flow must have a terminal step
3. **One executor per purpose**: Don't combine unrelated logic in a single step
4. **Name variables clearly**: Use descriptive names like `api_response`, not `data1`
