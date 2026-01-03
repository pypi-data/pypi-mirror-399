# Loop Executor

**Type**: `loop`
**Purpose**: Execute a block of steps iteratively. Supports `forEach`, `for`, and `while` loop types.

---

## Configuration Schema

| Field | Type | Required | Default | Description |
|---|---|---|---|---|
| `loopType` | `string` | **Yes** | | The type of loop. Valid: `forEach`, `for`, `while`. |
| `loopBlocks` | `array` | **Yes** | `[]` | An array of steps to execute in each iteration. |
| `maxIterations`| `integer` | No | `100` | Safety limit for the maximum number of iterations. |
| `resultVariable`| `string` | No | `null` | Variable to store an array of the results from each iteration. |
| `directOutput` | `boolean` | No | `false` | If `true`, returns results directly instead of storing in a variable. |

---

## Loop Type: `forEach`

Iterates over an array or collection. This is the most common loop type.

| Field | Type | Required | Description |
|---|---|---|---|
| `iterableVariable` | `string` | **Yes** | The array to iterate over, using `{{ $variable }}` syntax. |
| `itemVariable` | `string` | **Yes** | The name of the variable to hold the current item in each iteration. |
| `indexVariable` | `string` | No | The name of the variable to hold the current index (0-based). |

---

## Loop Type: `for`

Executes for a specific number of times using a counter.

| Field | Type | Required | Description |
|---|---|---|---|
| `startValue` | `integer` | **Yes** | The starting value of the counter. |
| `endValue` | `integer` | **Yes** | The value at which the loop stops (inclusive). |
| `counterVariable` | `string` | **Yes** | The name of the variable to hold the current counter value. |
| `stepValue` | `integer` | No | The value to increment the counter by in each iteration (default: 1). |

---

## Loop Type: `while`

Executes as long as a condition remains true. Uses the same condition object as the `conditional` executor.

| Field | Type | Required | Description |
|---|---|---|---|
| `condition` | `object` | **Yes** | The condition object to evaluate before each iteration. |

---

## Output Variable (`resultVariable`)

When `resultVariable` is set, it stores an `array` where each element is an `object` containing the `resultVariable` values from the steps inside that iteration.

**Example Output Structure:**
```json
[
  { "user_analysis": "...", "api_status": "success" }, // Iteration 1 results
  { "user_analysis": "...", "api_status": "success" }, // Iteration 2 results
  ...
]
```

---

## Canonical Examples

### 1. `forEach` Loop (Processing a List)

This demonstrates iterating over a list of users from a previous API call to process each one.

```json
{
  "type": "loop",
  "config": {
    "loopType": "forEach",
    "iterableVariable": "{{ $user_list }}",
    "itemVariable": "current_user",
    "loopBlocks": [
      {
        "id": "analyze_user_data",
        "type": "llmInstruction",
        "config": {
          "instruction": "Analyze the profile for user: {{ $current_user.name }}",
          "resultVariable": "user_analysis"
        }
      }
    ],
    "resultVariable": "all_user_analyses"
  }
}
```

### 2. `for` Loop (Fixed Number of Iterations)

This demonstrates performing a task a fixed number of times.

```json
{
  "type": "loop",
  "config": {
    "loopType": "for",
    "startValue": 1,
    "endValue": 5,
    "counterVariable": "page_number",
    "loopBlocks": [
      {
        "id": "fetch_page_data",
        "type": "apiCall",
        "config": {
          "url": "https://api.example.com/data?page={{ $page_number }}",
          "responseVariable": "page_data"
        }
      }
    ]
  }
}
```