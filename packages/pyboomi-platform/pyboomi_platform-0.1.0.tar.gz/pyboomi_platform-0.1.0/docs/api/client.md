# BoomiPlatformClient API Reference

Complete API reference for the `BoomiPlatformClient` class.

## Class: BoomiPlatformClient

Main client class for interacting with the Boomi Platform API.

### Constructor

```python
BoomiPlatformClient(
    account_id: Optional[str] = None,
    username: Optional[str] = None,
    api_token: Optional[str] = None,
    base_url: Optional[str] = None,
    timeout: Optional[int] = None,
    max_retries: Optional[int] = None,
    backoff_factor: Optional[float] = None,
    config: Optional[Config] = None,
    config_path: Optional[str] = None
)
```

#### Parameters

- `account_id` (Optional[str]): Boomi account ID
- `username` (Optional[str]): Boomi username/email
- `api_token` (Optional[str]): Boomi Platform API token
- `base_url` (Optional[str]): Custom base URL (default: `https://api.boomi.com/api/rest/v1`)
- `timeout` (Optional[int]): Request timeout in seconds (default: 30)
- `max_retries` (Optional[int]): Maximum retry attempts (default: 3)
- `backoff_factor` (Optional[float]): Exponential backoff factor (default: 1.5)
- `config` (Optional[Config]): Pre-loaded configuration object
- `config_path` (Optional[str]): Path to configuration file

#### Example

```python
from pyboomi_platform import BoomiPlatformClient

client = BoomiPlatformClient(
    account_id="your-account-id",
    username="your-username@company.com",
    api_token="your-api-token"
)
```

### Class Constants

- `DEFAULT_BASE_URL`: `"https://api.boomi.com/api/rest/v1"`
- `DEFAULT_TIMEOUT`: `30`
- `DEFAULT_MAX_RETRIES`: `3`
- `DEFAULT_BACKOFF_FACTOR`: `1.5`
- `RETRYABLE_STATUS_CODES`: `[500, 502, 504]`
- `RATE_LIMIT_STATUS_CODES`: `[429, 503]`

---

## Account Management

### get_account

Retrieves account information.

```python
get_account(account_id: Optional[str] = None) -> Any
```

**Parameters:**
- `account_id` (Optional[str]): Account ID. If not provided, uses the account_id configured in the client.

**Returns:** JSON response containing account information.

**Example:**
```python
account = client.get_account()
print(f"Account: {account['name']}")
```

### get_account_bulk

Retrieves multiple accounts (max 100).

```python
get_account_bulk(account_ids: List[str]) -> Any
```

**Parameters:**
- `account_ids` (List[str]): List of account IDs to retrieve.

**Returns:** JSON response containing account information.

**Example:**
```python
accounts = client.get_account_bulk(["account-id-1", "account-id-2"])
```

### query_account

Queries for Account objects.

```python
query_account(filters: Optional[Dict[str, Any]] = None) -> Any
```

**Parameters:**
- `filters` (Optional[Dict[str, Any]]): Dictionary of query fields (e.g., `{"name": "MyAccount"}`).

**Returns:** JSON response containing matched Account objects.

**Example:**
```python
results = client.query_account({"name": "MyAccount"})
```

### query_more_accounts

Gets next page of Account results.

```python
query_more_accounts(token: str) -> Any
```

**Parameters:**
- `token` (str): Pagination token from previous query.

**Returns:** JSON response with next set of Account results.

---

## Account Group Management

### create_account_group

Creates an account group.

```python
create_account_group(
    name: str,
    account_id: Optional[str] = None,
    auto_subscribe_alert_level: Optional[str] = None,
    default_group: Optional[bool] = None,
    resources: Optional[List[Dict[str, Any]]] = None
) -> Any
```

**Parameters:**
- `name` (str): Group name
- `account_id` (Optional[str]): Account ID
- `auto_subscribe_alert_level` (Optional[str]): Alert level
- `default_group` (Optional[bool]): Whether this is the default group
- `resources` (Optional[List[Dict[str, Any]]]): Group resources

**Returns:** JSON response containing created account group.

### get_account_group

Retrieves an account group.

```python
get_account_group(account_group_id: str) -> Any
```

### modify_account_group

Modifies an account group.

```python
modify_account_group(
    account_group_id: str,
    name: Optional[str] = None,
    account_id: Optional[str] = None,
    auto_subscribe_alert_level: Optional[str] = None,
    default_group: Optional[bool] = None,
    resources: Optional[List[Dict[str, Any]]] = None
) -> Any
```

### query_account_group

Queries for AccountGroup objects.

```python
query_account_group(filters: Optional[Dict[str, Any]] = None) -> Any
```

---

## Folder Management

### create_folder

Creates a folder.

```python
create_folder(name: str, parent_id: Optional[str] = None) -> Any
```

**Parameters:**
- `name` (str): Folder name
- `parent_id` (Optional[str]): Parent folder ID

**Returns:** JSON response containing created folder.

**Example:**
```python
folder = client.create_folder("MyFolder")
subfolder = client.create_folder("SubFolder", parent_id=folder["id"])
```

### get_folder

Retrieves a folder by ID.

```python
get_folder(folder_id: str) -> Any
```

**Parameters:**
- `folder_id` (str): Folder ID

**Returns:** JSON response containing folder.

### update_folder

Updates a folder.

```python
update_folder(
    folder_id: str,
    name: Optional[str] = None,
    parent_id: Optional[str] = None
) -> Any
```

**Parameters:**
- `folder_id` (str): Folder ID
- `name` (Optional[str]): New folder name
- `parent_id` (Optional[str]): New parent folder ID

**Returns:** JSON response containing updated folder.

### delete_folder

Deletes a folder.

```python
delete_folder(folder_id: str) -> Any
```

**Parameters:**
- `folder_id` (str): Folder ID

**Returns:** JSON response containing deleted folder.

### get_folder_bulk

Retrieves multiple folders (max 100).

```python
get_folder_bulk(folder_ids: List[str]) -> Any
```

### query_folder

Queries for Folder objects.

```python
query_folder(filters: Optional[Dict[str, Any]] = None) -> Any
```

**Example:**
```python
results = client.query_folder({"name": "MyFolder"})
```

### query_more_folders

Gets next page of folder results.

```python
query_more_folders(token: str) -> Any
```

---

## Process Management

### query_process

Queries for Process objects.

```python
query_process(filters: Optional[Dict[str, Any]] = None) -> Any
```

**Parameters:**
- `filters` (Optional[Dict[str, Any]]): Dictionary of query fields (e.g., `{"name": "MyProcess"}`).

**Returns:** JSON response containing matched Process objects.

**Example:**
```python
processes = client.query_process({"name": "MyProcess"})
```

---

## Component Management

### create_component

Creates a component from XML.

```python
create_component(
    component_xml: str,
    folder_id: Optional[str] = None
) -> Any
```

**Parameters:**
- `component_xml` (str): Component XML content
- `folder_id` (Optional[str]): Folder ID to place component in

**Returns:** XML response string containing created component.

**Example:**
```python
process_xml = """<?xml version="1.0" encoding="UTF-8"?>
<Process>
    <name>MyProcess</name>
</Process>"""
component = client.create_component(process_xml, folder_id="folder-id")
```

### get_component

Retrieves a component by ID (returns XML).

```python
get_component(component_id: str) -> Any
```

**Parameters:**
- `component_id` (str): Component ID

**Returns:** XML string containing component.

### query_component_metadata

Queries ComponentMetadata.

```python
query_component_metadata(filters: Optional[Dict[str, Any]] = None) -> Any
```

**Parameters:**
- `filters` (Optional[Dict[str, Any]]): Query filter structure

**Returns:** JSON response containing ComponentMetadata objects.

**Example:**
```python
metadata = client.query_component_metadata({
    "QueryFilter": {
        "expression": {
            "operator": "EQUALS",
            "property": "type",
            "argument": ["webservice"]
        }
    }
})
```

### get_component_metadata

Gets metadata for a specific component.

```python
get_component_metadata(
    component_id: str,
    branch_id: Optional[str] = None
) -> Any
```

**Parameters:**
- `component_id` (str): Component ID
- `branch_id` (Optional[str]): Branch ID

**Returns:** JSON response containing component metadata.

---

## Packaged Components

### create_packaged_component

Creates a packaged component.

```python
create_packaged_component(
    component_id: str,
    package_version: Optional[str] = None,
    notes: Optional[str] = None,
    branch_name: Optional[str] = None
) -> Any
```

**Parameters:**
- `component_id` (str): Component ID to package
- `package_version` (Optional[str]): Package version
- `notes` (Optional[str]): Package notes
- `branch_name` (Optional[str]): Branch name

**Returns:** JSON response containing packaged component.

### get_packaged_component

Retrieves a packaged component.

```python
get_packaged_component(packaged_component_id: str) -> Any
```

### query_packaged_components

Queries for packaged components.

```python
query_packaged_components(
    filters: Optional[Dict[str, Any]] = None
) -> Any
```

### get_packaged_component_manifest

Gets manifest for a packaged component.

```python
get_packaged_component_manifest(package_id: str) -> Any
```

### get_packaged_component_manifest_bulk

Gets manifests for multiple packaged components.

```python
get_packaged_component_manifest_bulk(package_ids: List[str]) -> Any
```

---

## Deployed Packages

### create_deployed_package

Creates a deployed package.

```python
create_deployed_package(
    package_id: str,
    environment_id: str
) -> Any
```

**Parameters:**
- `package_id` (str): Package ID
- `environment_id` (str): Environment ID

**Returns:** JSON response containing deployed package.

### get_deployed_package

Retrieves a deployed package.

```python
get_deployed_package(deployed_package_id: str) -> Any
```

### query_deployed_packages

Queries for deployed packages.

```python
query_deployed_packages(
    filters: Optional[Dict[str, Any]] = None
) -> Any
```

---

## Branch Management

### create_branch

Creates a branch.

```python
create_branch(
    parent_branch_id: str,
    branch_name: str,
    package_id: Optional[str] = None
) -> Any
```

**Parameters:**
- `parent_branch_id` (str): Parent branch ID
- `branch_name` (str): Branch name
- `package_id` (Optional[str]): Package ID (for creating from package)

**Returns:** JSON response containing created branch.

**Example:**
```python
# Create from parent branch
branch = client.create_branch("main-branch-id", "feature-branch")

# Create from package
branch = client.create_branch(
    "main-branch-id",
    "release-branch",
    package_id="package-id-123"
)
```

### get_branch

Retrieves a branch.

```python
get_branch(branch_id: str) -> Any
```

### update_branch

Updates a branch.

```python
update_branch(
    branch_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    ready: Optional[bool] = None
) -> Any
```

**Parameters:**
- `branch_id` (str): Branch ID
- `name` (Optional[str]): New branch name
- `description` (Optional[str]): Branch description
- `ready` (Optional[bool]): Ready flag

**Returns:** JSON response containing updated branch.

### delete_branch

Deletes a branch.

```python
delete_branch(branch_id: str) -> Any
```

### query_branches

Queries for branches.

```python
query_branches(filters: Optional[Dict[str, Any]] = None) -> Any
```

---

## Execution Monitoring

### query_execution_record

Queries execution records for an execution.

```python
query_execution_record(execution_id: str) -> Any
```

**Parameters:**
- `execution_id` (str): Execution ID

**Returns:** JSON response containing execution records.

**Example:**
```python
records = client.query_execution_record("execution-12345")
```

### query_more_execution_record

Gets next page of execution records.

```python
query_more_execution_record(query_token: str) -> Any
```

### create_execution_artifacts_request

Requests execution artifacts.

```python
create_execution_artifacts_request(execution_id: str) -> Any
```

**Returns:** JSON response with download URL.

**Example:**
```python
response = client.create_execution_artifacts_request("execution-12345")
download_url = response["url"]
```

### create_process_log_request

Requests process logs.

```python
create_process_log_request(
    execution_id: str,
    log_level: str = "INFO"
) -> Any
```

**Parameters:**
- `execution_id` (str): Execution ID
- `log_level` (str): Log level ("INFO" or "ALL")

**Returns:** JSON response with download URL.

### query_execution_connector

Queries execution connectors.

```python
query_execution_connector(execution_id: str) -> Any
```

### query_generic_connector_record

Queries generic connector records.

```python
query_generic_connector_record(
    execution_id: str,
    connector_id: str
) -> Any
```

### get_connector_document_url

Gets connector document download URL.

```python
get_connector_document_url(generic_connector_record_id: str) -> Any
```

**Returns:** JSON response with download URL.

### download_to_path

Downloads a file from URL to local path.

```python
download_to_path(url: str, file_path: str) -> str
```

**Parameters:**
- `url` (str): Download URL
- `file_path` (str): Local file path

**Returns:** Path to downloaded file.

**Example:**
```python
downloaded_path = client.download_to_path(
    download_url,
    "/tmp/artifacts.zip"
)
```

---

## Additional API Methods

The client also provides methods for:

- **Account SSO Configuration**: `get_account_sso_config()`, `modify_account_sso_config()`, etc.
- **User Federation**: `create_account_user_federation()`, `query_account_user_federation()`, etc.
- **User Roles**: `create_account_user_role()`, `query_account_user_role()`, etc.
- **API Usage**: `query_api_usage_count()`, etc.
- **Audit Logs**: `get_audit_log()`, `query_audit_log()`, etc.
- **Roles**: `create_role()`, `get_role()`, `modify_role()`, etc.
- **Environments**: `get_environment()`, `query_environments()`, etc.
- **Connection Licensing**: `create_connection_licensing_report()`, etc.
- **Custom Tracked Fields**: `query_custom_tracked_fields()`, etc.
- **Events**: `query_event()`, etc.

For complete method signatures, see the source code or use Python's `help()` function:

```python
help(client.create_folder)
```

---

## Error Handling

All methods may raise `BoomiAPIError` on API errors:

```python
from pyboomi_platform import BoomiAPIError

try:
    folder = client.get_folder("invalid-id")
except BoomiAPIError as e:
    print(f"Error: {e.status_code} - {e}")
```

See [Error Handling Guide](../guides/error-handling.md) for details.
