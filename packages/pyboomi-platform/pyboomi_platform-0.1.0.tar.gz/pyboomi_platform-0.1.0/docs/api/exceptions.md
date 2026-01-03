# Exceptions API Reference

API reference for exception classes in PyBoomi Platform SDK.

## Class: BoomiAPIError

Raised when a Boomi Platform API request returns an error response.

### Inheritance

```python
BoomiAPIError(Exception)
```

### Constructor

```python
BoomiAPIError(
    message: str,
    status_code: Optional[int] = None,
    response_body: Optional[str] = None
)
```

**Parameters:**
- `message` (str): Error message
- `status_code` (Optional[int]): HTTP status code from the API response
- `response_body` (Optional[str]): Response body from the API (if available)

**Example:**
```python
from pyboomi_platform import BoomiAPIError

# Typically raised by the SDK, not instantiated directly
try:
    client.get_folder("invalid-id")
except BoomiAPIError as e:
    print(f"Error: {e}")
    print(f"Status: {e.status_code}")
    print(f"Response: {e.response_body}")
```

### Attributes

#### status_code

HTTP status code from the API response.

**Type:** `Optional[int]`

**Example:**
```python
try:
    folder = client.get_folder("invalid-id")
except BoomiAPIError as e:
    if e.status_code == 404:
        print("Resource not found")
    elif e.status_code == 401:
        print("Authentication failed")
```

**Common Status Codes:**
- `400` - Bad Request
- `401` - Unauthorized
- `403` - Forbidden
- `404` - Not Found
- `409` - Conflict
- `429` - Too Many Requests (rate limited)
- `500` - Internal Server Error
- `502` - Bad Gateway
- `503` - Service Unavailable
- `504` - Gateway Timeout

#### response_body

Response body from the API (if available).

**Type:** `Optional[str]`

**Example:**
```python
try:
    result = client.query_process()
except BoomiAPIError as e:
    if e.response_body:
        print(f"API Response: {e.response_body}")
        # May contain additional error details
```

#### message

Error message (inherited from `Exception`).

**Type:** `str`

The message includes the status code: `"{message} (status: {status_code})"`

**Example:**
```python
try:
    folder = client.get_folder("invalid-id")
except BoomiAPIError as e:
    print(e.message)  # e.g., "Resource not found (status: 404)"
```

---

## Usage Examples

### Basic Error Handling

```python
from pyboomi_platform import BoomiPlatformClient, BoomiAPIError

client = BoomiPlatformClient(...)

try:
    folder = client.get_folder("folder-id")
except BoomiAPIError as e:
    print(f"API Error: {e}")
    print(f"Status Code: {e.status_code}")
```

### Handling Specific Status Codes

```python
try:
    folder = client.create_folder("MyFolder")
except BoomiAPIError as e:
    if e.status_code == 409:
        print("Folder already exists")
    elif e.status_code == 404:
        print("Parent folder not found")
    elif e.status_code == 401:
        print("Authentication failed")
    else:
        print(f"Unexpected error: {e}")
```

### Accessing Response Body

```python
try:
    component = client.create_component("invalid-xml")
except BoomiAPIError as e:
    print(f"Error: {e.status_code}")
    if e.response_body:
        # Response body may contain detailed error information
        print(f"Details: {e.response_body}")
```

### Error Logging

```python
import logging
from pyboomi_platform import BoomiPlatformClient, BoomiAPIError

logger = logging.getLogger(__name__)
client = BoomiPlatformClient(...)

try:
    result = client.query_process()
except BoomiAPIError as e:
    logger.error(
        f"API request failed: {e.status_code} - {e.message}",
        extra={
            "status_code": e.status_code,
            "response_body": e.response_body
        }
    )
```

### Custom Error Handling Function

```python
def handle_api_error(e: BoomiAPIError) -> str:
    """Convert API error to user-friendly message."""
    error_messages = {
        400: "Invalid request. Please check your input.",
        401: "Authentication failed. Please check your credentials.",
        403: "Access denied. Insufficient permissions.",
        404: "Resource not found.",
        409: "Resource conflict. The resource may already exist.",
        429: "Rate limited. Please try again later.",
        500: "Server error. Please try again later.",
        502: "Bad gateway. Please try again later.",
        503: "Service unavailable. Please try again later.",
        504: "Gateway timeout. Please try again later.",
    }

    return error_messages.get(
        e.status_code,
        f"An error occurred: {e.message}"
    )

try:
    folder = client.get_folder("invalid-id")
except BoomiAPIError as e:
    user_message = handle_api_error(e)
    print(user_message)
```

---

## When Exceptions Are Raised

`BoomiAPIError` is raised in the following scenarios:

1. **API returns error status code** (4xx, 5xx)
2. **Request timeout** (after all retries)
3. **Network errors** (after all retries)
4. **Invalid response format**

**Note:** The SDK automatically retries certain errors (429, 500, 502, 504). The exception is only raised after all retries are exhausted.

---

## Exception Hierarchy

```
Exception
└── BoomiAPIError
```

`BoomiAPIError` is a direct subclass of Python's built-in `Exception` class.

---

## Best Practices

1. **Always catch specific exceptions:**
   ```python
   try:
       result = client.query_process()
   except BoomiAPIError as e:
       # Handle API errors
   except Exception as e:
       # Handle other errors
   ```

2. **Check status codes for specific handling:**
   ```python
   if e.status_code == 404:
       # Handle not found
   elif e.status_code == 429:
       # Handle rate limiting
   ```

3. **Log errors with context:**
   ```python
   logger.error(f"API error: {e.status_code}", extra={
       "status_code": e.status_code,
       "response_body": e.response_body
   })
   ```

4. **Provide user-friendly messages:**
   ```python
   user_message = get_user_friendly_error(e)
   ```

---

## See Also

- [Error Handling Guide](../guides/error-handling.md) - Comprehensive error handling guide
- [Retry Behavior Guide](../guides/retry-behavior.md) - Understanding automatic retries
- [BoomiPlatformClient API](client.md) - Methods that may raise BoomiAPIError
