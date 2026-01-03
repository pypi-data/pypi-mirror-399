# Retry Behavior

This guide explains the automatic retry behavior in the PyBoomi Platform SDK, including rate limiting, backoff strategies, and configuration options.

## Overview

The SDK includes robust retry logic that automatically handles:
- **Rate limiting** (429, 503) with Retry-After header support
- **Server errors** (500, 502, 504) with automatic retries
- **Connection errors** with exponential backoff
- **Timeout handling** with configurable retry attempts

## Automatic Retry Logic

### Rate Limiting (429, 503)

When the API returns a rate limit error, the SDK:

1. Checks for `Retry-After` header in the response
2. Waits for the specified duration if present
3. Falls back to exponential backoff if header is missing
4. Retries the request up to `max_retries` times

```python
from pyboomi_platform import BoomiPlatformClient

client = BoomiPlatformClient(
    account_id="your-account-id",
    username="your-username@company.com",
    api_token="your-api-token",
    max_retries=3,  # Maximum retry attempts
    backoff_factor=1.5  # Exponential backoff multiplier
)

# Rate limiting is handled automatically
folders = client.query_folder()  # Will retry if rate limited
```

### Server Errors (500, 502, 504)

Server errors are automatically retried using urllib3's retry mechanism:

```python
# These errors are automatically retried
# - 500 Internal Server Error
# - 502 Bad Gateway
# - 504 Gateway Timeout

# No special handling needed
result = client.query_process()  # Automatically retries on server errors
```

### Connection Errors

Network connection errors are retried with exponential backoff:

```python
# Connection errors are automatically retried
try:
    result = client.query_folder()
except Exception as e:
    # Only raised after all retries are exhausted
    print(f"Request failed after retries: {e}")
```

## Configuration

### Retry Parameters

Configure retry behavior when creating the client:

```python
client = BoomiPlatformClient(
    account_id="your-account-id",
    username="your-username@company.com",
    api_token="your-api-token",
    max_retries=5,  # Increase retry attempts
    backoff_factor=2.0,  # Increase backoff delay
    timeout=60  # Increase timeout
)
```

### Default Values

- `max_retries`: 3
- `backoff_factor`: 1.5
- `timeout`: 30 seconds

### Configuration File

Set retry parameters in `config.yaml`:

```yaml
boomi:
  username: "your-username@company.com"
  api_token: "your-api-token"
  account_id: "your-account-id"
  max_retries: 5
  backoff_factor: 2.0
  timeout: 60
```

### Environment Variables

Set via environment variables:

```bash
export BOOMI_MAX_RETRIES=5
export BOOMI_BACKOFF_FACTOR=2.0
export BOOMI_TIMEOUT=60
```

## Retry-After Header Support

The SDK respects the `Retry-After` header when present:

```python
# If API returns Retry-After: 10
# SDK waits 10 seconds before retrying

# If Retry-After header is missing
# SDK uses exponential backoff: 1.5s, 3s, 6s, etc.
```

### Exponential Backoff Calculation

When `Retry-After` is not present, backoff is calculated as:

```
delay = backoff_factor * (2 ^ attempt_number)
```

Example with `backoff_factor=1.5`:
- Attempt 1: 1.5 seconds
- Attempt 2: 3.0 seconds
- Attempt 3: 6.0 seconds

## Retry Status Codes

### Automatically Retried

These status codes trigger automatic retries:

- **429** (Too Many Requests) - Handled manually with Retry-After support
- **500** (Internal Server Error) - Automatic retry via urllib3
- **502** (Bad Gateway) - Automatic retry via urllib3
- **503** (Service Unavailable) - Handled manually with Retry-After support
- **504** (Gateway Timeout) - Automatic retry via urllib3

### Not Retried

These status codes are not retried (immediate failure):

- **400** (Bad Request) - Invalid request, retry won't help
- **401** (Unauthorized) - Authentication error, retry won't help
- **403** (Forbidden) - Permission error, retry won't help
- **404** (Not Found) - Resource doesn't exist, retry won't help
- **409** (Conflict) - Resource conflict, retry won't help

## Logging Retry Attempts

Enable logging to see retry attempts:

```python
import logging

# Enable debug logging
logging.basicConfig(level=logging.DEBUG)

client = BoomiPlatformClient(...)

# You'll see retry attempts in logs:
# WARNING: Rate limited (429), retrying in 10 seconds...
# WARNING: Server error (500), retrying...
```

## Best Practices

### 1. Configure Appropriate Retries

```python
# For production with high load
client = BoomiPlatformClient(
    ...,
    max_retries=5,  # More retries for reliability
    backoff_factor=2.0  # Longer delays
)

# For development/testing
client = BoomiPlatformClient(
    ...,
    max_retries=2,  # Fewer retries for faster feedback
    backoff_factor=1.0  # Shorter delays
)
```

### 2. Handle Retry Exhaustion

```python
from pyboomi_platform import BoomiPlatformClient, BoomiAPIError

client = BoomiPlatformClient(..., max_retries=3)

try:
    result = client.query_folder()
except BoomiAPIError as e:
    if e.status_code == 429:
        print("Rate limited - all retries exhausted")
        print("Consider implementing exponential backoff at application level")
    else:
        print(f"Request failed: {e}")
```

### 3. Monitor Rate Limits

```python
import logging

logger = logging.getLogger(__name__)

# The SDK logs retry attempts automatically
# Monitor logs for rate limit patterns
client = BoomiPlatformClient(...)
```

### 4. Adjust Timeout for Large Operations

```python
# For operations that may take longer
client = BoomiPlatformClient(
    ...,
    timeout=120  # 2 minutes for large queries
)
```

## Custom Retry Logic

If you need custom retry logic, you can implement it at the application level:

```python
import time
from pyboomi_platform import BoomiPlatformClient, BoomiAPIError

client = BoomiPlatformClient(...)

def query_with_custom_retry(client, max_attempts=5):
    """Custom retry with exponential backoff."""
    for attempt in range(max_attempts):
        try:
            return client.query_folder()
        except BoomiAPIError as e:
            if e.status_code == 429 and attempt < max_attempts - 1:
                wait_time = (2 ** attempt) * 5  # 5s, 10s, 20s, 40s
                print(f"Rate limited, waiting {wait_time} seconds...")
                time.sleep(wait_time)
                continue
            raise
    return None
```

## Understanding Retry Behavior

### Request Flow

1. **Initial Request** - SDK makes API request
2. **Check Response** - If error, check status code
3. **Retry Decision** - Determine if error is retryable
4. **Wait Period** - Calculate wait time (Retry-After or exponential backoff)
5. **Retry Request** - Make retry attempt
6. **Repeat** - Continue until success or max retries reached

### Retry-After Header Example

```python
# API Response:
# HTTP/1.1 429 Too Many Requests
# Retry-After: 15

# SDK Behavior:
# 1. Detects 429 status
# 2. Reads Retry-After: 15
# 3. Waits 15 seconds
# 4. Retries request
```

### Exponential Backoff Example

```python
# API Response:
# HTTP/1.1 429 Too Many Requests
# (No Retry-After header)

# SDK Behavior (backoff_factor=1.5):
# Attempt 1: Wait 1.5 seconds, retry
# Attempt 2: Wait 3.0 seconds, retry
# Attempt 3: Wait 6.0 seconds, retry
# If all fail: Raise BoomiAPIError
```

## Related Topics

- [Error Handling](error-handling.md) - Understanding exceptions
- [Authentication](authentication.md) - Configuration options
