# Getting Started

This guide will help you get started with PyBoomi Platform SDK.

## Installation

Install the package using pip:

```bash
pip install pyboomi-platform
```

### Development Installation

For development, clone the repository and install in editable mode:

```bash
git clone https://github.com/iesoftwaredeveloper/pyboomi-platform.git
cd pyboomi-platform
pip install -e .
```

## Requirements

- Python 3.8 or higher
- `requests` library (automatically installed)
- `PyYAML` library (optional, for config file support)

## Quick Start

### 1. Import the Client

```python
from pyboomi_platform import BoomiPlatformClient
```

### 2. Initialize the Client

You can initialize the client in three ways:

#### Method 1: Direct Parameters

```python
client = BoomiPlatformClient(
    account_id="your-account-id",
    username="your-username@company.com",
    api_token="your-api-token"
)
```

#### Method 2: Configuration File

Create a `config.yaml` file:

```yaml
boomi:
  username: "your-username@company.com"
  api_token: "your-api-token"
  account_id: "your-account-id"
  timeout: 30
  max_retries: 3
  backoff_factor: 1.5
```

Then initialize:

```python
client = BoomiPlatformClient()
# Or specify a custom path:
client = BoomiPlatformClient(config_path="/path/to/config.yaml")
```

#### Method 3: Environment Variables

Set environment variables:

```bash
export BOOMI_ACCOUNT_ID="your-account-id"
export BOOMI_USERNAME="your-username@company.com"
export BOOMI_API_TOKEN="your-api-token"
```

Then initialize:

```python
client = BoomiPlatformClient()
```

### 3. Make Your First API Call

```python
# Query all folders
folders = client.query_folder()
print(f"Found {len(folders.get('result', []))} folders")

# Query processes
processes = client.query_process()
print(f"Found {len(processes.get('result', []))} processes")
```

## Configuration Priority

Configuration values are resolved in this order (highest to lowest priority):

1. **Direct parameters** passed to constructor
2. **Environment variables**
3. **Configuration file** values
4. **Default values**

## Next Steps

- Learn about [Authentication](authentication.md) options
- Explore [Folder Management](folder-management.md)
- Discover [Component Management](component-management.md)
- Understand [Error Handling](error-handling.md)

## Getting Your API Token

To use the Boomi Platform API, you need to generate an API token:

1. Log in to your Boomi account
2. Navigate to **Account Settings** → **API Tokens**
3. Click **Create Token**
4. Copy the token (you won't be able to see it again)
5. Use your Boomi username/email and the token for authentication

## Account ID

Your Boomi Account ID can be found in:
- The URL when logged into Boomi: `https://platform.boomi.com/BOOMI_TOKEN.{account-id}/...`
- Account Settings in the Boomi UI

## Example: Complete Workflow

```python
from pyboomi_platform import BoomiPlatformClient

# Initialize client
client = BoomiPlatformClient(
    account_id="your-account-id",
    username="your-username@company.com",
    api_token="your-api-token"
)

# Create a folder
folder = client.create_folder("MyNewFolder")
print(f"Created folder: {folder['id']}")

# Query processes
processes = client.query_process({"name": "MyProcess"})
for process in processes.get("result", []):
    print(f"Found process: {process['name']}")

# Query execution records
execution_id = "execution-12345"
records = client.query_execution_record(execution_id)
print(f"Found {len(records.get('result', []))} execution records")
```

## Troubleshooting

### Common Issues

**Import Error**: Make sure the package is installed:
```bash
pip install pyboomi-platform
```

**Authentication Error**: Verify your credentials:
- Check that your username and API token are correct
- Ensure your API token hasn't expired
- Verify your account ID is correct

**Connection Error**: Check your network connection and firewall settings.

**Timeout Error**: Increase the timeout value:
```python
client = BoomiPlatformClient(
    account_id="your-account-id",
    username="your-username@company.com",
    api_token="your-api-token",
    timeout=60  # Increase timeout to 60 seconds
)
```

For more help, see the [Error Handling](error-handling.md) guide.
