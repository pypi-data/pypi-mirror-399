# Error Handling

This guide covers error handling in the PyBoomi Platform SDK, including exception types and best practices.

## Exception Types

### BoomiAPIError

The main exception class for API-related errors:

```python
from pyboomi_platform import BoomiPlatformClient, BoomiAPIError

client = BoomiPlatformClient(...)

try:
    folder = client.get_folder("invalid-id")
except BoomiAPIError as e:
    print(f"Error: {e}")
    print(f"Status code: {e.status_code}")
    print(f"Response body: {e.response_body}")
```

### Exception Attributes

- `status_code` - HTTP status code (e.g., 404, 500)
- `response_body` - Response body from the API (if available)
- `message` - Error message with status code

## Common HTTP Status Codes

### 400 Bad Request

Invalid request parameters or malformed data:

```python
try:
    component = client.create_component("invalid-xml")
except BoomiAPIError as e:
    if e.status_code == 400:
        print("Invalid request - check your input data")
```

### 401 Unauthorized

Authentication failed:

```python
try:
    client = BoomiPlatformClient(
        account_id="wrong-id",
        username="wrong-user",
        api_token="wrong-token"
    )
    client.query_folder()
except BoomiAPIError as e:
    if e.status_code == 401:
        print("Authentication failed - check credentials")
```

### 403 Forbidden

Insufficient permissions:

```python
try:
    # Attempt operation without permission
    client.delete_folder("protected-folder-id")
except BoomiAPIError as e:
    if e.status_code == 403:
        print("Access denied - insufficient permissions")
```

### 404 Not Found

Resource not found:

```python
try:
    folder = client.get_folder("non-existent-id")
except BoomiAPIError as e:
    if e.status_code == 404:
        print("Resource not found")
```

### 409 Conflict

Resource conflict (e.g., duplicate name):

```python
try:
    folder = client.create_folder("ExistingFolder")
except BoomiAPIError as e:
    if e.status_code == 409:
        print("Resource already exists")
```

### 429 Too Many Requests

Rate limiting:

```python
try:
    # Make many requests quickly
    for i in range(100):
        client.query_folder()
except BoomiAPIError as e:
    if e.status_code == 429:
        print("Rate limited - the SDK will automatically retry")
```

**Note**: The SDK automatically handles 429 errors with retry logic.

### 500, 502, 504 Server Errors

Server-side errors:

```python
try:
    result = client.query_process()
except BoomiAPIError as e:
    if e.status_code in [500, 502, 504]:
        print("Server error - the SDK will automatically retry")
```

**Note**: The SDK automatically retries these errors.

## Error Handling Patterns

### Basic Error Handling

```python
from pyboomi_platform import BoomiPlatformClient, BoomiAPIError

client = BoomiPlatformClient(...)

try:
    folder = client.create_folder("MyFolder")
    print(f"Created folder: {folder['id']}")
except BoomiAPIError as e:
    print(f"API Error: {e}")
    if e.status_code == 409:
        print("Folder already exists")
except Exception as e:
    print(f"Unexpected error: {e}")
```

### Handling Multiple Operations

```python
def create_folder_safe(client, name):
    """Create folder with error handling."""
    try:
        return client.create_folder(name)
    except BoomiAPIError as e:
        if e.status_code == 409:
            # Folder exists, try to get it
            results = client.query_folder({"name": name})
            if results.get("result"):
                return results["result"][0]
        raise

# Use the safe function
try:
    folder = create_folder_safe(client, "MyFolder")
except BoomiAPIError as e:
    print(f"Failed to create folder: {e}")
```

### Retry Logic

The SDK includes automatic retry logic, but you can implement custom retries:

```python
import time
from pyboomi_platform import BoomiPlatformClient, BoomiAPIError

client = BoomiPlatformClient(...)

def query_with_retry(client, max_attempts=3):
    """Query with custom retry logic."""
    for attempt in range(max_attempts):
        try:
            return client.query_folder()
        except BoomiAPIError as e:
            if e.status_code == 429 and attempt < max_attempts - 1:
                wait_time = 2 ** attempt  # Exponential backoff
                print(f"Rate limited, waiting {wait_time} seconds...")
                time.sleep(wait_time)
                continue
            raise
    return None
```

### Validating Responses

```python
def get_folder_safe(client, folder_id):
    """Get folder with validation."""
    try:
        folder = client.get_folder(folder_id)

        # Validate response
        if not folder or "id" not in folder:
            raise ValueError("Invalid folder response")

        return folder
    except BoomiAPIError as e:
        if e.status_code == 404:
            return None  # Folder doesn't exist
        raise
```

## Best Practices

### 1. Always Use Try-Except

```python
# Good
try:
    result = client.query_process()
except BoomiAPIError as e:
    handle_error(e)

# Bad
result = client.query_process()  # May raise exception
```

### 2. Handle Specific Status Codes

```python
try:
    folder = client.get_folder(folder_id)
except BoomiAPIError as e:
    if e.status_code == 404:
        print("Folder not found")
    elif e.status_code == 403:
        print("Access denied")
    else:
        print(f"Unexpected error: {e}")
```

### 3. Log Errors Appropriately

```python
import logging

logger = logging.getLogger(__name__)

try:
    result = client.query_process()
except BoomiAPIError as e:
    logger.error(f"API error: {e.status_code} - {e}")
    logger.debug(f"Response body: {e.response_body}")
```

### 4. Provide User-Friendly Messages

```python
def get_user_friendly_error(e):
    """Convert API error to user-friendly message."""
    if e.status_code == 401:
        return "Authentication failed. Please check your credentials."
    elif e.status_code == 404:
        return "The requested resource was not found."
    elif e.status_code == 409:
        return "A resource with this name already exists."
    else:
        return f"An error occurred: {e}"

try:
    folder = client.create_folder("MyFolder")
except BoomiAPIError as e:
    print(get_user_friendly_error(e))
```

### 5. Handle Network Errors

```python
import requests
from pyboomi_platform import BoomiPlatformClient, BoomiAPIError

client = BoomiPlatformClient(...)

try:
    result = client.query_process()
except requests.exceptions.ConnectionError:
    print("Network connection error")
except requests.exceptions.Timeout:
    print("Request timeout")
except BoomiAPIError as e:
    print(f"API error: {e}")
```

## Debugging Tips

### Enable Logging

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

client = BoomiPlatformClient(...)
# Now you'll see detailed request/response logs
```

### Inspect Error Details

```python
try:
    result = client.query_process()
except BoomiAPIError as e:
    print(f"Status: {e.status_code}")
    print(f"Message: {e}")
    print(f"Response: {e.response_body}")

    # Log full details for debugging
    import json
    print(json.dumps({
        "status_code": e.status_code,
        "message": str(e),
        "response": e.response_body
    }, indent=2))
```

### Check Request Parameters

```python
# Before making request, validate inputs
folder_id = "folder-id-123"

if not folder_id:
    raise ValueError("folder_id is required")

if not isinstance(folder_id, str):
    raise TypeError("folder_id must be a string")

try:
    folder = client.get_folder(folder_id)
except BoomiAPIError as e:
    print(f"Failed to get folder {folder_id}: {e}")
```

## Related Topics

- [Retry Behavior](retry-behavior.md) - Understanding automatic retry logic
- [Authentication](authentication.md) - Troubleshooting authentication errors
