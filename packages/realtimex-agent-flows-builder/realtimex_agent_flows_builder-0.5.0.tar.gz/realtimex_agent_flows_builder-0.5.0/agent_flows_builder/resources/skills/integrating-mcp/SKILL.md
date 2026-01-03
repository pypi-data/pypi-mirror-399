---
name: integrating-mcp
description: External service integration via MCP servers (Gmail, Hacker News, etc). Covers discovery workflow with list_mcp_servers and get_mcp_action_schema tools, plus mcpServerAction executor configuration. Essential when user requests third-party service integrations.
---

# MCP Integration Guide

## When to Use

User mentions external services: Gmail, Hacker News, GitHub, Notion, databases, etc.

## Integration Workflow

Copy this checklist and track progress:

```
MCP Integration Progress:
- [ ] Step 1: Discover available servers
- [ ] Step 2: Find target action in server's actions list
- [ ] Step 3: Get action schema for parameter details
- [ ] Step 4: Configure mcpServerAction executor
- [ ] Step 5: Register result variable in flow_variables
```

## Step 1: Discover Servers

Call `list_mcp_servers()` to get available servers and their actions.

## Step 2: Identify Target Action

Match user intent to an action in the `actions` array from discovery.

## Step 3: Get Action Schema

Call `get_mcp_action_schema(server_id="...", action_id="...")` to get required parameters.

## Step 4: Configure Executor

```json
{
  "type": "mcpServerAction",
  "id": "/* unique_snake_case_id */",
  "config": {
    "provider": "/* remote | local — from schema */",
    "serverId": "/* exact server_id from discovery */",
    "action": "/* exact action_id from actions list */",
    "params": {
      "/* param_name */": "{{ $flow_variable }}"
    }
  },
  "resultVariable": "/* variable to store response */"
}
```

## Step 5: Register Variable

Add result variable to `flow_variables`:
```json
{"name": "action_result", "type": "object", "source": "node_output"}
```

## Common Actions

| Service | Example Action |
|---------|---------------|
| Gmail | `GMAIL__SEND_EMAIL` |
| Hacker News | `HACKERNEWS__TOP_STORIES_GET`, `HACKERNEWS__ITEM_GET` |

**Note:** Available servers depend on user's MCP configuration. Always discover first.