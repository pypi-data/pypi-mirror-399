# LLM Instruction Executor

**Type**: `llmInstruction`
**Purpose**: Execute AI-powered text processing and generation using Large Language Models.

---

## Configuration Schema

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `instruction` | `string` | **Yes** | | The primary prompt/instruction to send to the LLM. Supports interpolation. |
| `provider` | `string` | No | `realtimexai` | Name of the LiteLLM provider. Common values: `realtimexai`, `openai`, `anthropic`, `ollama`. |
| `model` | `string` | No | `gpt-4o-mini` | LLM model to use (e.g., `gpt-4o-mini`, `claude-3-sonnet`). |
| `temperature`| `float` | No | `0.7` | Controls randomness (0.0 - 2.0). Lower is more deterministic. |
| `maxTokens` | `integer` | No | `null` | Maximum response tokens to generate. |
| `systemPrompt` | `string` | No | `null` | Sets the persona or context for the LLM. Supports interpolation. |
| `responseFormat` | `string` | No | `text` | Expected response format. Valid: `text`, `json`. |
| `resultVariable` | `string` | No | `null` | Variable to store the LLM's response content. |
| `directOutput` | `boolean` | No | `false` | If `true`, returns response directly instead of storing in a variable. |
| `timeout` | `integer` | No | `60` | Request timeout in seconds (1-300). |
| `maxRetries` | `integer` | No | `2` | Maximum retry attempts for server/network errors (0-10). |

---

## Output Variable (`resultVariable`)

When `resultVariable` is set, it stores **only the content** of the LLM's response.

The data type of this variable depends on the `responseFormat` parameter:
- `responseFormat: "text"`: The output will be a `string`.
- `responseFormat: "json"`: The output will be an `object` or `array`.

---

## Canonical Examples

These examples serve as the primary structural blueprints for the agent.

### 1. Text Analysis (Default Format)

This demonstrates a standard text analysis task using a cloud provider.

```json
{
  "type": "llmInstruction",
  "config": {
    "provider": "realtimexai",
    "model": "gpt-4o-mini",
    "instruction": "Analyze the following customer feedback for key themes and overall sentiment: {{ $customer_feedback }}",
    "temperature": 0.2,
    "resultVariable": "feedback_analysis"
  }
}
```

### 2. Structured Data Extraction (JSON Format)

This demonstrates extracting structured data using a local provider (Ollama) and the `json` response format.

```json
{
  "type": "llmInstruction",
  "config": {
    "provider": "ollama",
    "model": "llama3:8b",
    "systemPrompt": "You are a data extraction expert. Only return valid JSON.",
    "instruction": "From this text, extract the user's name, email, and order number. Text: '{{ $support_ticket_text }}'",
    "responseFormat": "json",
    "resultVariable": "extracted_user_data"
  }
}
```