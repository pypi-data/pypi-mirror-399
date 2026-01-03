# Utils API Reference

API reference for utility functions in PyBoomi Platform SDK.

## Function: build_query_filter

Builds a Boomi API-compliant QueryFilter structure from a simple key-value dictionary.

### Signature

```python
build_query_filter(filters: Dict[str, Any]) -> Dict[str, Any]
```

### Parameters

- `filters` (Dict[str, Any]): Dictionary of filters like `{"name": "Shared", "type": "folder"}`.

### Returns

Dictionary structured for Boomi API QueryFilter format.

### Description

Converts a simple key-value filter dictionary into the complex nested structure required by the Boomi Platform API QueryFilter format.

**Input Format:**
```python
{"name": "MyFolder", "type": "folder"}
```

**Output Format:**
```python
{
    "QueryFilter": {
        "expression": {
            "operator": "and",
            "nestedExpression": [
                {
                    "property": "name",
                    "operator": "EQUALS",
                    "argument": ["MyFolder"]
                },
                {
                    "property": "type",
                    "operator": "EQUALS",
                    "argument": ["folder"]
                }
            ]
        }
    }
}
```

### Examples

#### Single Filter

```python
from pyboomi_platform.utils import build_query_filter

# Single filter
filters = {"name": "MyFolder"}
query_filter = build_query_filter(filters)

# Result:
# {
#     "QueryFilter": {
#         "expression": {
#             "property": "name",
#             "operator": "EQUALS",
#             "argument": ["MyFolder"]
#         }
#     }
# }
```

#### Multiple Filters (AND)

```python
# Multiple filters (combined with AND)
filters = {
    "name": "MyFolder",
    "type": "folder"
}
query_filter = build_query_filter(filters)

# Result:
# {
#     "QueryFilter": {
#         "expression": {
#             "operator": "and",
#             "nestedExpression": [
#                 {"property": "name", "operator": "EQUALS", "argument": ["MyFolder"]},
#                 {"property": "type", "operator": "EQUALS", "argument": ["folder"]}
#             ]
#         }
#     }
# }
```

#### List Values

```python
# List values are preserved
filters = {"type": ["folder", "process"]}
query_filter = build_query_filter(filters)

# Result:
# {
#     "QueryFilter": {
#         "expression": {
#             "property": "type",
#             "operator": "EQUALS",
#             "argument": ["folder", "process"]
#         }
#     }
# }
```

#### Empty Dictionary

```python
# Empty dictionary returns empty dict
filters = {}
query_filter = build_query_filter(filters)

# Result: {}
```

### Usage with BoomiPlatformClient

```python
from pyboomi_platform import BoomiPlatformClient
from pyboomi_platform.utils import build_query_filter

client = BoomiPlatformClient(...)

# Build query filter
filters = {"name": "MyFolder", "type": "folder"}
query_filter = build_query_filter(filters)

# Use with query methods
results = client.query_component_metadata(query_filter)
```

### Direct Usage vs. Utility Function

#### Without Utility (Manual)

```python
# Manual QueryFilter construction
query_filter = {
    "QueryFilter": {
        "expression": {
            "operator": "and",
            "nestedExpression": [
                {
                    "property": "name",
                    "operator": "EQUALS",
                    "argument": ["MyFolder"]
                },
                {
                    "property": "type",
                    "operator": "EQUALS",
                    "argument": ["folder"]
                }
            ]
        }
    }
}

results = client.query_component_metadata(query_filter)
```

#### With Utility (Simplified)

```python
# Using utility function
from pyboomi_platform.utils import build_query_filter

filters = {"name": "MyFolder", "type": "folder"}
query_filter = build_query_filter(filters)
results = client.query_component_metadata(query_filter)
```

### Limitations

The `build_query_filter` function:

- **Only supports EQUALS operator** - All filters use `"operator": "EQUALS"`
- **Only supports AND logic** - Multiple filters are combined with AND
- **Does not support complex expressions** - For complex queries, construct QueryFilter manually

### Advanced Usage

For complex queries with multiple operators (NOT, OR, etc.) or nested expressions, construct the QueryFilter manually:

```python
# Complex query (manual construction)
complex_filter = {
    "QueryFilter": {
        "expression": {
            "operator": "or",
            "nestedExpression": [
                {
                    "property": "name",
                    "operator": "EQUALS",
                    "argument": ["Folder1"]
                },
                {
                    "property": "name",
                    "operator": "EQUALS",
                    "argument": ["Folder2"]
                }
            ]
        }
    }
}

results = client.query_component_metadata(complex_filter)
```

### See Also

- [Boomi Platform API Documentation](https://developer.boomi.com/docs/api/platformapi/) - QueryFilter format
- [Component Management Guide](../guides/component-management.md) - Using filters with queries
