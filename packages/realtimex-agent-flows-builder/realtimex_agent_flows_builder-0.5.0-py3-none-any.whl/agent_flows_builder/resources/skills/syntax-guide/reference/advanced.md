# Advanced Interpolation

## JMESPath Queries

The `jmespath()` function enables complex data extraction:

| Pattern | Example | Description |
|---------|---------|-------------|
| Filter | `[?active]` | Items where active is true |
| Project | `[].name` | Extract all names |
| First | `[0]` | First item |
| Sort | `sort_by(@, &name)` | Sort by property |
| Length | `length(@)` | Count items |

**Usage**:
```
{{ jmespath($users, '[?role==`admin`].name') }}
```

## Function Composition

Functions can be nested:
```
{{ upper(jmespath($users, '[0].name')) }}
{{ len(jmespath($data, '[?active]')) }}
{{ toJson(jmespath($items, '[?price > `100`]')) }}
```

## Type Preservation

| Context | Method | Behavior |
|---------|--------|----------|
| String field | `interpolate` | Objects → JSON strings |
| Object field | `interpolate_object` | Types preserved |

**Object preservation**: When a field value is a single expression like `"{{ $user }}"`, the object is preserved. When mixed with text, it becomes a string.
