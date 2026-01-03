#!/usr/bin/env python3
#
# PyBoomi Platform - Example 02: Component Management
#
# Copyright 2025 Robert Little
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# Author: Robert Little
# Created: 2025-12-12

"""
Example 02: Component Management

This example demonstrates:
- Querying processes
- Creating components (Process, Connection)
- Querying component metadata
- Working with packaged components
"""

from pyboomi_platform import BoomiPlatformClient

# Initialize the client
# Note: Replace with your actual credentials or use config file/env vars
client = BoomiPlatformClient(
    account_id="your-account-id",
    username="your-username@company.com",
    api_token="your-api-token",
)

# ============================================================================
# Query Processes
# ============================================================================

print("=" * 70)
print("Querying Processes")
print("=" * 70)

try:
    # Query all processes
    print("\n1. Querying all processes...")
    all_processes = client.query_process()
    processes = all_processes.get("result", [])
    print(f"   ✓ Found {len(processes)} process(es)")

    # Query processes by name
    print("\n2. Querying processes by name...")
    filtered_processes = client.query_process({"name": "MyProcess"})
    matching = filtered_processes.get("result", [])
    print(f"   ✓ Found {len(matching)} process(es) matching 'MyProcess'")
    for process in matching[:5]:  # Show first 5
        print(f"     - {process.get('name')} (ID: {process.get('id')})")

except Exception as e:
    print(f"   ✗ Error querying processes: {e}")

# ============================================================================
# Create a Process Component
# ============================================================================

print("\n" + "=" * 70)
print("Creating Process Component")
print("=" * 70)

# Example Process XML (simplified - actual XML would be more complex)
process_xml = """<?xml version="1.0" encoding="UTF-8"?>
<Process>
    <name>ExampleProcess</name>
    <type>process</type>
    <version>1.0.0</version>
</Process>"""

print("\n3. Creating a process component...")
try:
    # Create component in default location
    component = client.create_component(process_xml)
    print("   ✓ Created process component")
    print(f"   Response: {component[:200]}...")  # Show first 200 chars

    # Create component in a specific folder (if you have a folder_id)
    # component = client.create_component(process_xml, folder_id="folder-id-123")
    # print(f"   ✓ Created process component in folder")

except Exception as e:
    print(f"   ✗ Error creating component: {e}")
    print("   Note: This may fail if the XML structure is incomplete")

# ============================================================================
# Create a Connection Component
# ============================================================================

print("\n" + "=" * 70)
print("Creating Connection Component")
print("=" * 70)

# Example Connection XML (simplified)
connection_xml = """<?xml version="1.0" encoding="UTF-8"?>
<Connection>
    <name>ExampleDatabaseConnection</name>
    <type>connection</type>
    <connectionType>database</connectionType>
</Connection>"""

print("\n4. Creating a connection component...")
try:
    connection = client.create_component(connection_xml)
    print("   ✓ Created connection component")
    print(f"   Response: {connection[:200]}...")  # Show first 200 chars
except Exception as e:
    print(f"   ✗ Error creating connection: {e}")
    print("   Note: This may fail if the XML structure is incomplete")

# ============================================================================
# Query Component Metadata
# ============================================================================

print("\n" + "=" * 70)
print("Querying Component Metadata")
print("=" * 70)

print("\n5. Querying API services (webservice components)...")
try:
    # Query for webservice components (API Services)
    api_services = client.query_component_metadata(
        {
            "QueryFilter": {
                "expression": {
                    "operator": "and",
                    "nestedExpression": [
                        {
                            "argument": ["webservice"],
                            "operator": "EQUALS",
                            "property": "type",
                        },
                        {
                            "argument": ["true"],
                            "operator": "EQUALS",
                            "property": "currentVersion",
                        },
                        {
                            "argument": ["false"],
                            "operator": "EQUALS",
                            "property": "deleted",
                        },
                    ],
                }
            }
        }
    )

    results = api_services.get("result", [])
    print(f"   ✓ Found {len(results)} API service(s)")
    for service in results[:5]:  # Show first 5
        print(f"     - {service.get('name', 'Unknown')} (ID: {service.get('id')})")

except Exception as e:
    print(f"   ✗ Error querying component metadata: {e}")

# ============================================================================
# Query Packaged Components
# ============================================================================

print("\n" + "=" * 70)
print("Querying Packaged Components")
print("=" * 70)

print("\n6. Querying packaged components...")
try:
    packages = client.query_packaged_components()
    package_results = packages.get("result", [])
    print(f"   ✓ Found {len(package_results)} packaged component(s)")
    for package in package_results[:5]:  # Show first 5
        print(f"     - {package.get('name', 'Unknown')} (ID: {package.get('id')})")

    # Get details of a specific packaged component
    if package_results:
        package_id = package_results[0].get("id")
        print(f"\n7. Getting details for package: {package_id}")
        package_details = client.get_packaged_component(package_id)
        print(f"   ✓ Package Name: {package_details.get('name')}")
        print(f"   ✓ Package ID: {package_details.get('id')}")

except Exception as e:
    print(f"   ✗ Error querying packaged components: {e}")

print("\n" + "=" * 70)
print("Example completed!")
print("=" * 70)
