# Execution Monitoring

This guide covers monitoring process executions, querying execution records, and downloading execution artifacts using the PyBoomi Platform SDK.

## Overview

The execution monitoring APIs allow you to:
- Query execution records for process runs
- Download execution artifacts (logs, data, etc.)
- Query execution connectors
- Download connector documents

## Querying Execution Records

### Query Records for an Execution

```python
from pyboomi_platform import BoomiPlatformClient

client = BoomiPlatformClient(...)

# Query execution records
execution_id = "execution-12345"
records = client.query_execution_record(execution_id)

for record in records.get("result", []):
    print(f"Record ID: {record.get('id')}")
    print(f"Status: {record.get('status')}")
    print(f"Start Time: {record.get('startTime')}")
```

### Pagination

```python
# Handle pagination
records = client.query_execution_record(execution_id)
all_records = records.get("result", [])

# Get next page if available
if "queryToken" in records:
    next_page = client.query_more_execution_record(records["queryToken"])
    all_records.extend(next_page.get("result", []))
```

## Execution Artifacts

Execution artifacts contain logs, data, and other information from process executions.

### Request Execution Artifacts

```python
# Request artifacts for an execution
execution_id = "execution-12345"
artifacts_response = client.create_execution_artifacts_request(execution_id)

# Get download URL
download_url = artifacts_response.get("url")
print(f"Download URL: {download_url}")
```

### Download Artifacts

```python
import os

# Download artifacts to a file
output_path = "/tmp/execution-artifacts.zip"
downloaded_path = client.download_to_path(download_url, output_path)
print(f"Artifacts saved to: {downloaded_path}")
```

## Process Logs

Process logs contain detailed execution logs for debugging and monitoring.

### Request Process Log (Default Level)

```python
# Request log with default level (INFO)
execution_id = "execution-12345"
log_response = client.create_process_log_request(execution_id)
log_url = log_response.get("url")

# Download the log
log_path = client.download_to_path(log_url, "/tmp/process-log.zip")
```

### Request Process Log (All Levels)

```python
# Request log with ALL levels
log_response = client.create_process_log_request(execution_id, log_level="ALL")
log_url = log_response.get("url")
log_path = client.download_to_path(log_url, "/tmp/process-log-all.zip")
```

**Available Log Levels:**
- `INFO` (default) - Information level logs
- `ALL` - All log levels including DEBUG and TRACE

## Execution Connectors

Connectors represent external systems that the process interacts with during execution.

### Query Execution Connectors

```python
# Query connectors for an execution
execution_id = "execution-12345"
connectors = client.query_execution_connector(execution_id)

for connector in connectors.get("result", []):
    print(f"Connector: {connector.get('name')} (ID: {connector.get('id')})")
```

### Pagination

```python
connectors = client.query_execution_connector(execution_id)
all_connectors = connectors.get("result", [])

if "queryToken" in connectors:
    next_page = client.query_more_execution_connector(connectors["queryToken"])
    all_connectors.extend(next_page.get("result", []))
```

## Generic Connector Records

Generic connector records contain detailed information about connector operations.

### Query Generic Connector Records

```python
# Query records for a specific connector
execution_id = "execution-12345"
connector_id = "connector-id-123"
records = client.query_generic_connector_record(execution_id, connector_id)

for record in records.get("result", []):
    print(f"Record ID: {record.get('id')}")
    print(f"Status: {record.get('status')}")
```

### Get Connector Document URL

```python
# Get document URL for a connector record
record_id = "generic-connector-record-123"
doc_response = client.get_connector_document_url(record_id)
doc_url = doc_response.get("url")

# Download the document
doc_path = client.download_to_path(doc_url, "/tmp/connector-doc.zip")
```

## Complete Example: Gathering All Artifacts

```python
import os
from pyboomi_platform import BoomiPlatformClient

client = BoomiPlatformClient(...)

execution_id = "execution-12345"
output_dir = "/tmp/execution-artifacts"
os.makedirs(output_dir, exist_ok=True)

# 1. Query execution records
records = client.query_execution_record(execution_id)
print(f"Found {len(records.get('result', []))} execution records")

# 2. Download execution artifacts
artifacts_response = client.create_execution_artifacts_request(execution_id)
artifacts_path = client.download_to_path(
    artifacts_response["url"],
    os.path.join(output_dir, "artifacts.zip")
)
print(f"Downloaded artifacts to: {artifacts_path}")

# 3. Download process log
log_response = client.create_process_log_request(execution_id, log_level="ALL")
log_path = client.download_to_path(
    log_response["url"],
    os.path.join(output_dir, "process-log.zip")
)
print(f"Downloaded process log to: {log_path}")

# 4. Download connector documents
connectors = client.query_execution_connector(execution_id)
connector_count = 0

for connector in connectors.get("result", []):
    connector_id = connector["id"]

    # Query generic connector records
    records = client.query_generic_connector_record(execution_id, connector_id)

    for record in records.get("result", []):
        record_id = record["id"]

        # Get and download connector document
        doc_response = client.get_connector_document_url(record_id)
        doc_path = client.download_to_path(
            doc_response["url"],
            os.path.join(output_dir, f"connector-{record_id}.zip")
        )
        connector_count += 1
        print(f"Downloaded connector document: {doc_path}")

print(f"Downloaded {connector_count} connector document(s)")
print(f"All artifacts saved to: {output_dir}")
```

## Error Handling

```python
from pyboomi_platform import BoomiPlatformClient, BoomiAPIError

client = BoomiPlatformClient(...)

try:
    records = client.query_execution_record(execution_id)
except BoomiAPIError as e:
    if e.status_code == 404:
        print("Execution not found")
    elif e.status_code == 429:
        print("Rate limited - retrying...")
    else:
        print(f"Error: {e}")
```

## Download Helper Features

The `download_to_path()` method includes:

- **Automatic retry logic** with Retry-After header support
- **Streaming downloads** for large files
- **Progress tracking** (via logging)
- **Error handling** for network issues

### Download with Custom Path

```python
# Download to a specific directory
output_dir = "/data/executions"
os.makedirs(output_dir, exist_ok=True)

download_path = client.download_to_path(
    download_url,
    os.path.join(output_dir, f"execution-{execution_id}-artifacts.zip")
)
```

## Best Practices

1. **Use appropriate log levels** - Use `INFO` for production monitoring, `ALL` for debugging
2. **Handle pagination** - Always check for `queryToken` when querying
3. **Organize downloads** - Use meaningful file names and directory structures
4. **Clean up old artifacts** - Remove downloaded files after processing
5. **Monitor execution status** - Check record status before downloading artifacts
6. **Handle rate limiting** - The SDK automatically handles retries, but be aware of API limits

## Related API Methods

- `query_execution_record()` - Query execution records
- `query_more_execution_record()` - Get next page of records
- `create_execution_artifacts_request()` - Request execution artifacts
- `create_process_log_request()` - Request process logs
- `query_execution_connector()` - Query execution connectors
- `query_more_execution_connector()` - Get next page of connectors
- `query_generic_connector_record()` - Query connector records
- `query_more_generic_connector_record()` - Get next page of connector records
- `get_connector_document_url()` - Get connector document download URL
- `download_to_path()` - Download file from URL to local path

For complete API reference, see [BoomiPlatformClient API](../api/client.md#execution-monitoring).
