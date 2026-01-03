# Authentication

PyBoomi Platform SDK supports multiple methods for providing authentication credentials.

## Authentication Methods

The SDK supports three methods for providing credentials, in order of priority:

1. **Direct Parameters** (highest priority)
2. **Environment Variables**
3. **Configuration File** (lowest priority)

## Method 1: Direct Parameters

Pass credentials directly when creating the client:

```python
from pyboomi_platform import BoomiPlatformClient

client = BoomiPlatformClient(
    account_id="your-account-id",
    username="your-username@company.com",
    api_token="your-api-token",
    timeout=30,
    max_retries=3,
    backoff_factor=1.5
)
```

### Parameters

- `account_id` (required): Your Boomi account ID
- `username` (required): Your Boomi username/email
- `api_token` (required): Your Boomi Platform API token
- `base_url` (optional): Custom API base URL (defaults to `https://api.boomi.com/api/rest/v1`)
- `timeout` (optional): Request timeout in seconds (default: 30)
- `max_retries` (optional): Maximum retry attempts (default: 3)
- `backoff_factor` (optional): Exponential backoff factor (default: 1.5)

## Method 2: Environment Variables

Set environment variables before running your script:

```bash
export BOOMI_ACCOUNT_ID="your-account-id"
export BOOMI_USERNAME="your-username@company.com"
export BOOMI_API_TOKEN="your-api-token"
export BOOMI_TIMEOUT="30"
export BOOMI_MAX_RETRIES="3"
export BOOMI_BACKOFF_FACTOR="1.5"
```

Then initialize without parameters:

```python
from pyboomi_platform import BoomiPlatformClient

client = BoomiPlatformClient()
```

### Supported Environment Variables

- `BOOMI_ACCOUNT_ID` or `BOOMIACCT` - Account ID
- `BOOMI_USERNAME` or `BOOMI_CLIENT_ID` - Username
- `BOOMI_API_TOKEN` or `BOOMI_CLIENT_SECRET` - API token
- `BOOMI_API_BASE_URL` - Custom base URL
- `BOOMI_TIMEOUT` - Request timeout
- `BOOMI_MAX_RETRIES` - Maximum retries
- `BOOMI_BACKOFF_FACTOR` - Backoff factor

## Method 3: Configuration File

Create a YAML configuration file (default: `config.yaml`):

```yaml
boomi:
  username: "your-username@company.com"
  api_token: "your-api-token"
  account_id: "your-account-id"
  base_url: "https://api.boomi.com/api/rest/v1"
  timeout: 30
  max_retries: 3
  backoff_factor: 1.5
```

### Configuration File Locations

The SDK looks for configuration files in this order:

1. Path specified in `config_path` parameter
2. `config.yaml` in current directory
3. `pyboomi_config.yaml` in current directory
4. `~/.pyboomi/config.yaml` in user home directory

### Using Configuration File

```python
from pyboomi_platform import BoomiPlatformClient

# Use default config.yaml
client = BoomiPlatformClient()

# Or specify custom path
client = BoomiPlatformClient(config_path="/path/to/config.yaml")
```

## Authentication Mechanism

The SDK uses **Basic Authentication** with your username and API token:

- Username is prefixed with `BOOMI_TOKEN.` if not already present
- Credentials are base64-encoded
- Authorization header: `Basic {base64(username:token)}`

## Getting Your Credentials

### Account ID

Your Account ID can be found:
- In the Boomi Platform URL: `https://platform.boomi.com/BOOMI_TOKEN.{account-id}/...`
- In Account Settings → Account Information

### API Token

1. Log in to Boomi Platform
2. Navigate to **Account Settings** → **API Tokens**
3. Click **Create Token**
4. Copy the token immediately (it won't be shown again)
5. Store it securely

### Username

Use your Boomi login email address as the username.

## Security Best Practices

1. **Never commit credentials to version control**
   - Use environment variables or config files excluded from git
   - Add `config.yaml` to `.gitignore`

2. **Use environment variables in production**
   - Set via CI/CD pipeline secrets
   - Use secure secret management systems

3. **Rotate tokens regularly**
   - Create new tokens periodically
   - Revoke old tokens when no longer needed

4. **Use least privilege**
   - Create API tokens with only necessary permissions
   - Use separate tokens for different environments

5. **Monitor token usage**
   - Review audit logs regularly
   - Set up alerts for unusual activity

## Example: Secure Configuration

### Development (config.yaml - gitignored)

```yaml
# config.yaml (not in git)
boomi:
  username: "dev-user@company.com"
  api_token: "dev-token-123"
  account_id: "dev-account-id"
```

### Production (Environment Variables)

```bash
# Set in CI/CD or deployment system
export BOOMI_ACCOUNT_ID="prod-account-id"
export BOOMI_USERNAME="prod-user@company.com"
export BOOMI_API_TOKEN="prod-token-456"
```

```python
# Code works the same way
client = BoomiPlatformClient()
```

## Troubleshooting

### Authentication Errors

**401 Unauthorized**
- Verify username and token are correct
- Check that token hasn't expired
- Ensure username format is correct (email address)

**403 Forbidden**
- Check token permissions
- Verify account ID is correct
- Ensure account has API access enabled

**Missing Credentials Error**
- Ensure at least one authentication method provides all required values
- Check environment variable names are correct
- Verify config file format is valid YAML

### Configuration Loading Issues

**Config file not found**
- Check file path is correct
- Verify file exists in one of the default locations
- Ensure file has read permissions

**YAML parsing error**
- Validate YAML syntax
- Check for proper indentation
- Ensure all required fields are present

For more help, see [Error Handling](error-handling.md).
