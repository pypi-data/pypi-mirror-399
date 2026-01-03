# Flow Pattern: ETL Pipeline

**Use Case**: Extract, Transform, Load. Standard data processing workflows.
**Examples**:
- "Scrape a website, summarize it, and email the result."
- "Fetch API data, filter it with Python, and save to a file."

## Architectural Blueprint

1.  **Extract (Source)**: Fetch raw data.
    - *Executors*: `apiCall`, `webScraping`, `mcpServerAction` (Read).
2.  **Transform (Process)**: Modify or analyze the data.
    - *Executors*: `llmInstruction`, `codeExecution` (if available), `loop` (for batch processing).
3.  **Load (Sink)**: Send the result to a destination.
    - *Executors*: `apiCall` (POST), `mcpServerAction` (Write/Send), `fileSave`.

## Configuration Rules

### 1. Separation of Concerns
- Do NOT try to fetch and process in the same step.
- **Step 1**: Get Data -> Output to `{{ $raw_data }}`.
- **Step 2**: Process `{{ $raw_data }}` -> Output to `{{ $clean_data }}`.

### 2. Data Flow
- Ensure the output of the Extract phase is compatible with the input of the Transform phase.
- Use `flow_variables` to define the intermediate data structures.

## Example Structure

```json
[
  {
    "id": "extract_data",
    "type": "apiCall",
    "config": {
      "url": "https://api.source.com/data",
      "resultVariable": "raw_data"
    }
  },
  {
    "id": "transform_data",
    "type": "llmInstruction",
    "config": {
      "instruction": "Summarize this: {{ $raw_data }}",
      "resultVariable": "summary"
    }
  },
  {
    "id": "load_data",
    "type": "mcpServerAction",
    "config": {
      "serverId": "GMAIL",
      "action": "SEND_EMAIL",
      "params": {
        "body": "{{ $summary }}"
      }
    }
  }
]
```
