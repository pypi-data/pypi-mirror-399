#!/usr/bin/env python3
#
# PyBoomi Platform - Example 03: Execution Monitoring and Artifacts
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
Example 03: Execution Monitoring and Artifacts

This example demonstrates:
- Querying execution records
- Requesting execution artifacts
- Requesting process logs
- Querying execution connectors
- Downloading connector documents
"""

import os

from pyboomi_platform import BoomiPlatformClient

# Initialize the client
# Note: Replace with your actual credentials or use config file/env vars
client = BoomiPlatformClient(
    account_id="your-account-id",
    username="your-username@company.com",
    api_token="your-api-token",
)

# Replace with an actual execution ID from your Boomi account
EXECUTION_ID = "your-execution-id-12345"

# ============================================================================
# Query Execution Records
# ============================================================================

print("=" * 70)
print("Querying Execution Records")
print("=" * 70)

print(f"\n1. Querying execution records for execution: {EXECUTION_ID}")
try:
    records = client.query_execution_record(EXECUTION_ID)
    execution_records = records.get("result", [])
    print(f"   ✓ Found {len(execution_records)} execution record(s)")

    for record in execution_records[:5]:  # Show first 5
        record_id = record.get("id")
        status = record.get("status", "Unknown")
        print(f"     - Record ID: {record_id}, Status: {status}")

    # Handle pagination if needed
    if "queryToken" in records:
        print(
            "\n   Note: More records available. Use query_more_execution_record() to fetch them."
        )
        # next_page = client.query_more_execution_record(records["queryToken"])

except Exception as e:
    print(f"   ✗ Error querying execution records: {e}")

# ============================================================================
# Request Execution Artifacts
# ============================================================================

print("\n" + "=" * 70)
print("Requesting Execution Artifacts")
print("=" * 70)

print(f"\n2. Requesting execution artifacts for execution: {EXECUTION_ID}")
try:
    artifacts_response = client.create_execution_artifacts_request(EXECUTION_ID)
    download_url = artifacts_response.get("url")
    print("   ✓ Artifacts request created")
    print(f"   ✓ Download URL: {download_url}")

    # Download the artifacts
    output_dir = "/tmp/boomi-artifacts"
    os.makedirs(output_dir, exist_ok=True)
    artifacts_path = os.path.join(output_dir, "execution-artifacts.zip")

    print(f"\n3. Downloading artifacts to: {artifacts_path}")
    downloaded_path = client.download_to_path(download_url, artifacts_path)
    print(f"   ✓ Artifacts downloaded to: {downloaded_path}")

except Exception as e:
    print(f"   ✗ Error requesting/downloading artifacts: {e}")

# ============================================================================
# Request Process Logs
# ============================================================================

print("\n" + "=" * 70)
print("Requesting Process Logs")
print("=" * 70)

print(
    f"\n4. Requesting process log (default level: INFO) for execution: {EXECUTION_ID}"
)
try:
    # Request log with default log level (INFO)
    log_response = client.create_process_log_request(EXECUTION_ID)
    log_url = log_response.get("url")
    print("   ✓ Process log request created")
    print(f"   ✓ Download URL: {log_url}")

    # Download the log
    log_path = os.path.join(output_dir, "process-log-info.zip")
    downloaded_log = client.download_to_path(log_url, log_path)
    print(f"   ✓ Process log downloaded to: {downloaded_log}")

    # Request log with ALL log level
    print(f"\n5. Requesting process log (ALL levels) for execution: {EXECUTION_ID}")
    log_response_all = client.create_process_log_request(EXECUTION_ID, log_level="ALL")
    log_url_all = log_response_all.get("url")
    log_path_all = os.path.join(output_dir, "process-log-all.zip")
    downloaded_log_all = client.download_to_path(log_url_all, log_path_all)
    print(f"   ✓ Process log (ALL levels) downloaded to: {downloaded_log_all}")

except Exception as e:
    print(f"   ✗ Error requesting/downloading process logs: {e}")

# ============================================================================
# Query Execution Connectors
# ============================================================================

print("\n" + "=" * 70)
print("Querying Execution Connectors")
print("=" * 70)

print(f"\n6. Querying connectors for execution: {EXECUTION_ID}")
try:
    connectors = client.query_execution_connector(EXECUTION_ID)
    connector_results = connectors.get("result", [])
    print(f"   ✓ Found {len(connector_results)} connector(s)")

    for connector in connector_results[:5]:  # Show first 5
        connector_id = connector.get("id")
        connector_name = connector.get("name", "Unknown")
        print(f"     - {connector_name} (ID: {connector_id})")

    # Query generic connector records for each connector
    if connector_results:
        connector_id = connector_results[0].get("id")
        print(f"\n7. Querying generic connector records for connector: {connector_id}")
        records = client.query_generic_connector_record(EXECUTION_ID, connector_id)
        record_results = records.get("result", [])
        print(f"   ✓ Found {len(record_results)} connector record(s)")

        # Get connector document URL for each record
        for record in record_results[:3]:  # Show first 3
            record_id = record.get("id")
            print(f"\n8. Getting connector document URL for record: {record_id}")
            try:
                doc_response = client.get_connector_document_url(record_id)
                doc_url = doc_response.get("url")
                print(f"   ✓ Document URL: {doc_url}")

                # Download the connector document
                doc_path = os.path.join(output_dir, f"connector-doc-{record_id}.zip")
                downloaded_doc = client.download_to_path(doc_url, doc_path)
                print(f"   ✓ Connector document downloaded to: {downloaded_doc}")

            except Exception as e:
                print(f"   ✗ Error getting/downloading connector document: {e}")

except Exception as e:
    print(f"   ✗ Error querying connectors: {e}")

# ============================================================================
# Complete Example: Gather All Artifacts
# ============================================================================

print("\n" + "=" * 70)
print("Complete Example: Gathering All Execution Artifacts")
print("=" * 70)

print(f"\n9. Gathering all artifacts for execution: {EXECUTION_ID}")
try:
    output_directory = "/tmp/execution-artifacts-complete"
    os.makedirs(output_directory, exist_ok=True)

    # 1. Query execution records
    records = client.query_execution_record(EXECUTION_ID)
    print(f"   ✓ Found {len(records.get('result', []))} execution record(s)")

    # 2. Download execution artifacts
    artifacts_response = client.create_execution_artifacts_request(EXECUTION_ID)
    artifacts_path = client.download_to_path(
        artifacts_response["url"], os.path.join(output_directory, "artifacts.zip")
    )
    print("   ✓ Downloaded execution artifacts")

    # 3. Download process log
    log_response = client.create_process_log_request(EXECUTION_ID, log_level="ALL")
    log_path = client.download_to_path(
        log_response["url"], os.path.join(output_directory, "process-log.zip")
    )
    print("   ✓ Downloaded process log")

    # 4. Download connector documents
    connectors = client.query_execution_connector(EXECUTION_ID)
    connector_count = 0
    for connector in connectors.get("result", []):
        connector_id = connector["id"]
        records = client.query_generic_connector_record(EXECUTION_ID, connector_id)
        for record in records.get("result", []):
            record_id = record["id"]
            doc_response = client.get_connector_document_url(record_id)
            doc_path = client.download_to_path(
                doc_response["url"],
                os.path.join(output_directory, f"connector-{record_id}.zip"),
            )
            connector_count += 1
    print(f"   ✓ Downloaded {connector_count} connector document(s)")

    print(f"\n   ✓ All artifacts saved to: {output_directory}")

except Exception as e:
    print(f"   ✗ Error gathering artifacts: {e}")

print("\n" + "=" * 70)
print("Example completed!")
print("=" * 70)
