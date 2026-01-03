# BoomiAuth API Reference

API reference for the `BoomiAuth` class used for authentication.

## Class: BoomiAuth

Handles API token-based authentication for the Boomi Platform API using Basic Auth.

### Constructor

```python
BoomiAuth(username: str, api_token: str)
```

**Parameters:**
- `username` (str): The Boomi username (e.g., user@company.com). The `BOOMI_TOKEN.` prefix is automatically added if not present.
- `api_token` (str): The Platform API token generated from the Boomi UI.

**Example:**
```python
from pyboomi_platform.auth import BoomiAuth

auth = BoomiAuth(
    username="user@company.com",
    api_token="your-api-token"
)
```

**Note:** This class is typically used internally by `BoomiPlatformClient`. You usually don't need to instantiate it directly.

### Method: get_auth_header

Returns the Authorization header for Basic Auth with the token.

```python
get_auth_header() -> Dict[str, str]
```

**Returns:** Dictionary containing the Authorization header with key `"Authorization"`.

**Header Format:**
```
Authorization: Basic {base64_encoded_credentials}
```

Where `base64_encoded_credentials` is the base64 encoding of `{username}:{api_token}`.

**Example:**
```python
from pyboomi_platform.auth import BoomiAuth

auth = BoomiAuth("user@company.com", "api-token-123")
headers = auth.get_auth_header()

# headers = {"Authorization": "Basic dXNlckBjb21wYW55LmNvbTphcGktdG9rZW4tMTIz"}
```

### Username Format

The `BoomiAuth` class automatically handles username formatting:

- If username starts with `BOOMI_TOKEN.`, it's used as-is
- Otherwise, `BOOMI_TOKEN.` prefix is automatically added

**Examples:**
```python
# These are equivalent:
auth1 = BoomiAuth("user@company.com", "token")
auth2 = BoomiAuth("BOOMI_TOKEN.user@company.com", "token")

# Both produce: "BOOMI_TOKEN.user@company.com"
```

### Authentication Mechanism

The Boomi Platform API uses **Basic Authentication**:

1. Username and API token are combined: `{username}:{api_token}`
2. The combination is base64-encoded
3. The Authorization header is set to: `Basic {encoded_credentials}`

**Example Flow:**
```
Input:
  username: "user@company.com"
  api_token: "token123"

Step 1: Add prefix (if needed)
  username: "BOOMI_TOKEN.user@company.com"

Step 2: Combine
  credentials: "BOOMI_TOKEN.user@company.com:token123"

Step 3: Base64 encode
  encoded: "Qk9PTUlfVE9LRU4udXNlckBjb21wYW55LmNvbTp0b2tlbjEyMw=="

Step 4: Create header
  Authorization: "Basic Qk9PTUlfVE9LRU4udXNlckBjb21wYW55LmNvbTp0b2tlbjEyMw=="
```

---

## Usage

### Direct Usage (Advanced)

While typically used internally, you can use `BoomiAuth` directly:

```python
from pyboomi_platform.auth import BoomiAuth
import requests

# Create auth instance
auth = BoomiAuth("user@company.com", "api-token")

# Get headers
headers = auth.get_auth_header()

# Use with requests
response = requests.get(
    "https://api.boomi.com/api/rest/v1/account-id/Account/account-id",
    headers=headers
)
```

### Typical Usage (via BoomiPlatformClient)

In most cases, you'll use authentication through `BoomiPlatformClient`:

```python
from pyboomi_platform import BoomiPlatformClient

# Authentication is handled automatically
client = BoomiPlatformClient(
    account_id="account-id",
    username="user@company.com",
    api_token="api-token"
)

# All requests are automatically authenticated
folders = client.query_folder()
```

---

## Security Considerations

1. **Never commit tokens to version control**
   - Store tokens in environment variables or secure config files
   - Use `.gitignore` to exclude config files

2. **Token rotation**
   - Rotate API tokens regularly
   - Revoke old tokens when creating new ones

3. **Token storage**
   - Use secure secret management systems in production
   - Avoid hardcoding tokens in source code

4. **Token scope**
   - Create tokens with minimal required permissions
   - Use different tokens for different environments

---

## Error Handling

The `BoomiAuth` class itself doesn't raise exceptions. Authentication errors occur when making API requests:

```python
from pyboomi_platform import BoomiPlatformClient, BoomiAPIError

try:
    client = BoomiPlatformClient(
        account_id="account-id",
        username="wrong-user",
        api_token="wrong-token"
    )
    client.query_folder()  # This will raise BoomiAPIError with 401
except BoomiAPIError as e:
    if e.status_code == 401:
        print("Authentication failed - check credentials")
```

---

## See Also

- [Authentication Guide](../guides/authentication.md) - Authentication setup
- [BoomiPlatformClient API](client.md) - Client that uses BoomiAuth
- [Error Handling Guide](../guides/error-handling.md) - Handling auth errors
