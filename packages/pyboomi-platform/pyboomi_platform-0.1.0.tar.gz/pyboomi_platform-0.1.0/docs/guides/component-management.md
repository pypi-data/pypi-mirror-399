# Component Management

This guide covers working with components, processes, and connections in Boomi using the PyBoomi Platform SDK.

## Overview

Components in Boomi include processes, connections, shapes, and other integration artifacts. The SDK provides methods to create, query, and manage these components.

## Querying Processes

### Query All Processes

```python
from pyboomi_platform import BoomiPlatformClient

client = BoomiPlatformClient(...)

# Query all processes
processes = client.query_process()
for process in processes.get("result", []):
    print(f"Process: {process.get('name')} (ID: {process.get('id')})")
```

### Query Processes by Name

```python
# Query processes by name
results = client.query_process({"name": "MyProcess"})
for process in results.get("result", []):
    print(f"Found: {process.get('name')}")
```

## Creating Components

Components are created using XML content that follows Boomi's component schema.

### Create a Process Component

```python
# Process XML (simplified example)
process_xml = """<?xml version="1.0" encoding="UTF-8"?>
<Process>
    <name>MyNewProcess</name>
    <type>process</type>
    <version>1.0.0</version>
</Process>"""

# Create in default location
component = client.create_component(process_xml)
print(f"Created component: {component}")

# Create in a specific folder
component = client.create_component(process_xml, folder_id="folder-id-123")
```

### Create a Connection Component

```python
# Connection XML (simplified example)
connection_xml = """<?xml version="1.0" encoding="UTF-8"?>
<Connection>
    <name>DatabaseConnection</name>
    <type>connection</type>
    <connectionType>database</connectionType>
</Connection>"""

connection = client.create_component(connection_xml, folder_id="connections-folder-id")
```

**Important**: The XML structure must match Boomi's component schema. For complete XML structures, refer to the [Boomi Platform API documentation](https://developer.boomi.com/docs/api/platformapi/).

## Retrieving Components

### Get Component by ID

```python
# Get component (returns XML)
component_id = "component-id-123"
component_xml = client.get_component(component_id)
print(component_xml)
```

**Note**: The `get_component()` method returns XML content, not JSON.

## Querying Component Metadata

Component metadata provides information about components without retrieving the full component XML.

### Query API Services (Webservice Components)

```python
# Query for webservice components (API Services)
api_services = client.query_component_metadata({
    "QueryFilter": {
        "expression": {
            "operator": "and",
            "nestedExpression": [
                {
                    "argument": ["webservice"],
                    "operator": "EQUALS",
                    "property": "type"
                },
                {
                    "argument": ["true"],
                    "operator": "EQUALS",
                    "property": "currentVersion"
                },
                {
                    "argument": ["false"],
                    "operator": "EQUALS",
                    "property": "deleted"
                }
            ]
        }
    }
})

for service in api_services.get("result", []):
    print(f"API Service: {service.get('name')} (ID: {service.get('id')})")
```

### Get Component Metadata

```python
# Get metadata for a specific component
component_id = "component-id-123"
metadata = client.get_component_metadata(component_id)
print(f"Component: {metadata.get('name')}")

# Get metadata from a specific branch
metadata = client.get_component_metadata(component_id, branch_id="branch-id-456")
```

### Pagination

```python
# Query with pagination
results = client.query_component_metadata({...})
components = results.get("result", [])

if "queryToken" in results:
    next_page = client.query_more_component_metadata(results["queryToken"])
    components.extend(next_page.get("result", []))
```

## Packaged Components

Packaged components are versioned snapshots of components.

### Create a Packaged Component

```python
# Package a component
component_id = "component-id-123"
package = client.create_packaged_component(
    component_id=component_id,
    package_version="1.0.0",
    notes="Initial release",
    branch_name="main"
)
print(f"Created package: {package['id']}")
```

### Get Packaged Component

```python
package_id = "package-id-123"
package = client.get_packaged_component(package_id)
print(f"Package: {package.get('name')}")
```

### Query Packaged Components

```python
# Query all packaged components
packages = client.query_packaged_components()
for package in packages.get("result", []):
    print(f"Package: {package.get('name')}")

# Query with filters
packages = client.query_packaged_components({"componentId": "component-id-123"})
```

## Deployed Packages

Deployed packages are packages that have been deployed to environments.

### Create a Deployed Package

```python
# Deploy a package
package_id = "package-id-123"
environment_id = "environment-id-456"
deployment = client.create_deployed_package(
    package_id=package_id,
    environment_id=environment_id
)
print(f"Deployed package: {deployment['id']}")
```

### Query Deployed Packages

```python
# Query deployed packages
deployments = client.query_deployed_packages()
for deployment in deployments.get("result", []):
    print(f"Deployment: {deployment.get('id')}")

# Query with filters
deployments = client.query_deployed_packages({
    "environmentId": "environment-id-456"
})
```

### Get Package Manifest

```python
# Get manifest for a packaged component
package_id = "package-id-123"
manifest = client.get_packaged_component_manifest(package_id)
print(f"Manifest: {manifest}")

# Get multiple manifests
package_ids = ["package-id-1", "package-id-2"]
manifests = client.get_packaged_component_manifest_bulk(package_ids)
```

## Complete Example

```python
from pyboomi_platform import BoomiPlatformClient

client = BoomiPlatformClient(...)

# 1. Query existing processes
processes = client.query_process()
print(f"Found {len(processes.get('result', []))} processes")

# 2. Create a new process component
process_xml = """<?xml version="1.0" encoding="UTF-8"?>
<Process>
    <name>ExampleProcess</name>
    <type>process</type>
</Process>"""

component = client.create_component(process_xml, folder_id="my-folder-id")
component_id = component  # Component ID is in the response

# 3. Query component metadata
metadata = client.get_component_metadata(component_id)
print(f"Component metadata: {metadata.get('name')}")

# 4. Package the component
package = client.create_packaged_component(
    component_id=component_id,
    package_version="1.0.0",
    notes="First version"
)
print(f"Created package: {package['id']}")

# 5. Query API services
api_services = client.query_component_metadata({
    "QueryFilter": {
        "expression": {
            "operator": "and",
            "nestedExpression": [
                {"argument": ["webservice"], "operator": "EQUALS", "property": "type"},
                {"argument": ["true"], "operator": "EQUALS", "property": "currentVersion"}
            ]
        }
    }
})
print(f"Found {len(api_services.get('result', []))} API services")
```

## Error Handling

```python
from pyboomi_platform import BoomiPlatformClient, BoomiAPIError

client = BoomiPlatformClient(...)

try:
    component = client.create_component(process_xml)
except BoomiAPIError as e:
    if e.status_code == 400:
        print("Invalid XML structure")
    elif e.status_code == 404:
        print("Folder not found")
    else:
        print(f"Error: {e}")
```

## Best Practices

1. **Validate XML** before creating components
2. **Use folders** to organize components logically
3. **Version packages** using semantic versioning
4. **Query metadata** instead of full components when possible (faster)
5. **Handle pagination** for large result sets
6. **Use meaningful names** for components and packages

## Related API Methods

- `query_process()` - Query processes
- `create_component()` - Create a component from XML
- `get_component()` - Get component XML by ID
- `query_component_metadata()` - Query component metadata
- `get_component_metadata()` - Get metadata for a component
- `create_packaged_component()` - Package a component
- `get_packaged_component()` - Get packaged component
- `query_packaged_components()` - Query packaged components
- `create_deployed_package()` - Deploy a package
- `query_deployed_packages()` - Query deployments
- `get_packaged_component_manifest()` - Get package manifest

For complete API reference, see [BoomiPlatformClient API](../api/client.md#component-management).
