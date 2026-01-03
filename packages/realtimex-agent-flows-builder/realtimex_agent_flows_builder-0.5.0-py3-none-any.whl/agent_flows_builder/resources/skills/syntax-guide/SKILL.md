---
name: syntax-guide
description: Reference for {{ $variable }} interpolation, condition operators, and built-in functions. Covers variable access patterns, loop iteration, conditional comparisons, and data transformation functions. Essential when configuring executor parameters.
---

# Syntax Guide

## Variable Interpolation

All expressions use `{{ $variable }}` syntax:

| Pattern | Example | Description |
|---------|---------|-------------|
| Direct | `{{ $user_id }}` | Top-level variable |
| Nested | `{{ $user.profile.name }}` | Dot notation for properties |
| Array | `{{ $items[0] }}` | Index access (0-based) |
| Deep | `{{ $data.users[0].email }}` | Combined patterns |

**In strings**: Multiple expressions concatenate:
```
"https://api.com/users/{{ $user_id }}/posts/{{ $post_id }}"
```

## Inside Loops

Loop executors define iteration variables:

| Field | Example | Description |
|-------|---------|-------------|
| `itemVariable` | `"current_item"` | Current element: `{{ $current_item }}` |
| `indexVariable` | `"idx"` | Current index: `{{ $idx }}` |
| `counterVariable` | `"page"` | For-loop counter: `{{ $page }}` |

## Condition Operators

Conditions are **JSON objects**, not inline expressions:

```json
{
  "variable": "{{ $user.age }}",
  "operator": "greater_than_or_equal",
  "value": 18,
  "type": "number"
}
```

| Operator | Types | Description |
|----------|-------|-------------|
| `equals` | All | Equality check |
| `not_equals` | All | Inequality check |
| `greater_than` | number, datetime, string | Greater than |
| `less_than` | number, datetime, string | Less than |
| `greater_than_or_equal` | number, datetime, string | >= |
| `less_than_or_equal` | number, datetime, string | <= |
| `contains` | string, array | Substring or element check |
| `not_contains` | string, array | Inverse of contains |
| `starts_with` | string | Prefix check |
| `ends_with` | string | Suffix check |
| `is_empty` | All | Null, empty string, or empty collection |
| `is_not_empty` | All | Has value |

**Type field**: Enforces strict type checking. Values: `auto`, `string`, `number`, `boolean`, `datetime`, `array`, `object`.

## Built-in Functions

Available within `{{ }}` expressions:

| Function | Example | Description |
|----------|---------|-------------|
| `len(x)` | `{{ len($items) }}` | Array/string length |
| `toJson(x)` | `{{ toJson($data) }}` | Convert to JSON string |
| `toString(x)` | `{{ toString($id) }}` | Convert to string |
| `upper(s)` | `{{ upper($name) }}` | Uppercase |
| `lower(s)` | `{{ lower($email) }}` | Lowercase |
| `strip(s)` | `{{ strip($input) }}` | Trim whitespace |
| `jmespath(obj, q)` | `{{ jmespath($users, '[?active]') }}` | Query objects |

**Advanced queries**: See [reference/advanced.md](reference/advanced.md) for JMESPath patterns.

## Common Mistakes

| Wrong    | Correct   | Issue |
|----------|-----------|-------|
| `$variable` | `{{ $variable }}` | Missing braces |
| `{{ variable }}` | `{{ $variable }}` | Missing `$` prefix |
| `operator: "greaterThan"` | `operator: "greater_than"` | Wrong case |

## Error Behavior

| Scenario | Result |
|----------|--------|
| Missing variable | Original expression preserved |
| Invalid syntax | Expression unchanged |
| Type mismatch (strict) | `ValueError` raised |