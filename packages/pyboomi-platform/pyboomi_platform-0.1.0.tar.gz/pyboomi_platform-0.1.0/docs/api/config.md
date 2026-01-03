# Config API Reference

API reference for the `Config` class and configuration utilities.

## Class: Config

Configuration manager for PyBoomi Platform SDK. Handles loading configuration from YAML files and environment variables.

### Constructor

```python
Config(config_path: Optional[str] = None)
```

**Parameters:**
- `config_path` (Optional[str]): Path to config.yaml file. If not provided, will look for config.yaml in current directory.

**Example:**
```python
from pyboomi_platform import Config

# Use default config.yaml
config = Config()

# Or specify custom path
config = Config(config_path="/path/to/config.yaml")
```

### Method: get_boomi_config

Gets Boomi configuration with environment variable overrides.

```python
get_boomi_config() -> Dict[str, Any]
```

**Returns:** Dictionary containing Boomi configuration values with environment variable overrides applied.

**Configuration Priority:**
1. Environment variables (highest)
2. Configuration file values (lowest)

**Returns Dictionary Keys:**
- `username` (str): Boomi username/email
- `api_token` (str): Boomi Platform API token
- `account_id` (str): Boomi account ID
- `base_url` (str): API base URL
- `timeout` (int): Request timeout in seconds
- `max_retries` (int): Maximum retry attempts
- `backoff_factor` (float): Exponential backoff factor

**Example:**
```python
from pyboomi_platform import Config

config = Config()
boomi_config = config.get_boomi_config()

print(f"Account ID: {boomi_config['account_id']}")
print(f"Username: {boomi_config['username']}")
```

### Configuration File Format

The configuration file should be in YAML format:

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

The SDK searches for configuration files in this order:

1. Path specified in `config_path` parameter
2. `config.yaml` in current directory
3. `pyboomi_config.yaml` in current directory
4. `~/.pyboomi/config.yaml` in user home directory

### Environment Variable Support

The following environment variables are supported:

- `BOOMI_USERNAME` or `BOOMI_CLIENT_ID` - Username
- `BOOMI_API_TOKEN` or `BOOMI_CLIENT_SECRET` - API token
- `BOOMI_ACCOUNT_ID` or `BOOMIACCT` - Account ID
- `BOOMI_API_BASE_URL` - Base URL
- `BOOMI_TIMEOUT` - Timeout
- `BOOMI_MAX_RETRIES` - Max retries
- `BOOMI_BACKOFF_FACTOR` - Backoff factor

Environment variables take precedence over configuration file values.

### PyYAML Dependency

The `Config` class requires `PyYAML` for YAML file support. If `PyYAML` is not available:

- Configuration file loading is skipped
- Only environment variables are used
- A warning message is printed

Install PyYAML:

```bash
pip install PyYAML
```

---

## Function: get_config

Convenience function to get a configuration instance.

```python
get_config(config_path: Optional[str] = None) -> Config
```

**Parameters:**
- `config_path` (Optional[str]): Optional path to config file.

**Returns:** `Config` instance.

**Example:**
```python
from pyboomi_platform import get_config

config = get_config()
boomi_config = config.get_boomi_config()
```

This is equivalent to:

```python
from pyboomi_platform import Config

config = Config()
boomi_config = config.get_boomi_config()
```

---

## Usage Examples

### Using Config with BoomiPlatformClient

```python
from pyboomi_platform import BoomiPlatformClient, Config

# Load configuration
config = Config()
boomi_config = config.get_boomi_config()

# Use with client
client = BoomiPlatformClient(
    account_id=boomi_config["account_id"],
    username=boomi_config["username"],
    api_token=boomi_config["api_token"]
)
```

### Direct Configuration Access

```python
from pyboomi_platform import Config

config = Config()
boomi_config = config.get_boomi_config()

# Access individual values
account_id = boomi_config["account_id"]
username = boomi_config["username"]
api_token = boomi_config["api_token"]
timeout = boomi_config["timeout"]
```

### Custom Configuration Path

```python
from pyboomi_platform import Config

# Use custom config file
config = Config(config_path="/etc/boomi/config.yaml")
boomi_config = config.get_boomi_config()
```

---

## Error Handling

The `Config` class handles errors gracefully:

- **Missing config file**: Falls back to environment variables only
- **Invalid YAML**: Prints warning and uses environment variables
- **Missing PyYAML**: Prints warning and uses environment variables only

No exceptions are raised for configuration loading issues.

---

## See Also

- [Authentication Guide](../guides/authentication.md) - Configuration methods
- [Getting Started Guide](../guides/getting-started.md) - Initial setup
