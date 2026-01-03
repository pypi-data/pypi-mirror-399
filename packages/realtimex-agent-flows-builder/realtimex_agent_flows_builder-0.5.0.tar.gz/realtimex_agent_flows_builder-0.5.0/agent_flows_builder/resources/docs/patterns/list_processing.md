# Flow Pattern: List Processing

**Intent**: Iterate over a list of items (usually from an API response) and process each item individually.

## When to Use
- User asks to "process each..." or "for every..."
- API returns an array of items that need individual handling (e.g., "get news and summarize each story")
- You need to aggregate results from multiple items

## Architectural Blueprint

1. **Fetch Data**: Use `apiCall` (or similar) to get the list.
2. **Loop Node**: Create a `loop` node (`loopType: "forEach"`) that iterates over the array from step 1.
3. **Process Item**: Inside the loop, use `{{ $itemVariable }}` to access the current item.
4. **Aggregate (Optional)**: Use a loop `resultVariable` if you need per-item results collected.

## Critical Configuration Rules

- **Loop Type**: Use `loopType: "forEach"` for array iteration.
- **Loop Source**: The `iterableVariable` must point to the array (e.g., `{{ $api_response.body.items }}`).
- **Loop Variable**: Define a clear `itemVariable` (e.g., `news_item`).
- **Inside the Loop**: All steps must reference the `itemVariable` (e.g., `{{ $news_item.title }}`), not the original list.

## Example Structure

```json
[
  {
    "id": "fetch_news",
    "type": "apiCall",
    "config": { "url": "...", "resultVariable": "news_list" }
  },
  {
    "id": "process_each_news",
    "type": "loop",
    "config": {
      "loopType": "forEach",
      "iterableVariable": "{{ $news_list }}",
      "itemVariable": "story",
      "loopBlocks": [
        {
          "id": "summarize_story",
          "type": "llmInstruction",
          "config": {
            "instruction": "Summarize this story: {{ $story.title }}"
          }
        }
      ],
      "resultVariable": "all_story_summaries"
    }
  }
]
```
