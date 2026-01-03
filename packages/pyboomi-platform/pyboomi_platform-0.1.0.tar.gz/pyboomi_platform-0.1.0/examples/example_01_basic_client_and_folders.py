#!/usr/bin/env python3
#
# PyBoomi Platform - Example 01: Basic Client Initialization and Folder Management
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
Example 01: Basic Client Initialization and Folder Management

This example demonstrates:
- Different ways to initialize the BoomiPlatformClient
- Creating folders
- Querying folders
- Updating folders
- Deleting folders
"""

from pyboomi_platform import BoomiPlatformClient

# ============================================================================
# Method 1: Initialize with Direct Parameters
# ============================================================================

print("=" * 70)
print("Method 1: Direct Parameter Initialization")
print("=" * 70)

client = BoomiPlatformClient(
    account_id="your-account-id",
    username="your-username@company.com",
    api_token="your-api-token",
    timeout=30,
    max_retries=3,
)

# ============================================================================
# Method 2: Initialize using Configuration File
# ============================================================================

print("\n" + "=" * 70)
print("Method 2: Configuration File Initialization")
print("=" * 70)

# The client will automatically look for config.yaml in the current directory
# Or you can specify a custom path:
# client = BoomiPlatformClient(config_path="/path/to/your/config.yaml")
client = BoomiPlatformClient()

# ============================================================================
# Method 3: Initialize using Environment Variables
# ============================================================================

print("\n" + "=" * 70)
print("Method 3: Environment Variable Initialization")
print("=" * 70)

# Set these environment variables before running:
# export BOOMI_ACCOUNT_ID="your-account-id"
# export BOOMI_USERNAME="your-username@company.com"
# export BOOMI_API_TOKEN="your-api-token"

# Then initialize without parameters:
# client = BoomiPlatformClient()

# ============================================================================
# Folder Management Examples
# ============================================================================

print("\n" + "=" * 70)
print("Folder Management Operations")
print("=" * 70)

# Create a folder in the root
print("\n1. Creating a folder in the root...")
try:
    folder = client.create_folder("MyExampleFolder")
    folder_id = folder["id"]
    print(f"   ✓ Created folder: {folder['name']} (ID: {folder_id})")
except Exception as e:
    print(f"   ✗ Error creating folder: {e}")
    folder_id = None

# Create a subfolder
if folder_id:
    print("\n2. Creating a subfolder...")
    try:
        subfolder = client.create_folder("MySubFolder", parent_id=folder_id)
        subfolder_id = subfolder["id"]
        print(f"   ✓ Created subfolder: {subfolder['name']} (ID: {subfolder_id})")
    except Exception as e:
        print(f"   ✗ Error creating subfolder: {e}")
        subfolder_id = None

# Get folder information
if folder_id:
    print("\n3. Retrieving folder information...")
    try:
        folder_info = client.get_folder(folder_id)
        print(f"   ✓ Folder Name: {folder_info['name']}")
        print(f"   ✓ Folder ID: {folder_info['id']}")
        if "parentId" in folder_info:
            print(f"   ✓ Parent ID: {folder_info['parentId']}")
    except Exception as e:
        print(f"   ✗ Error retrieving folder: {e}")

# Query folders
print("\n4. Querying folders...")
try:
    # Query by name
    results = client.query_folder({"name": "MyExampleFolder"})
    folders = results.get("result", [])
    print(f"   ✓ Found {len(folders)} folder(s) matching 'MyExampleFolder'")
    for folder in folders:
        print(f"     - {folder['name']} (ID: {folder['id']})")

    # Query all folders (no filter)
    all_results = client.query_folder()
    all_folders = all_results.get("result", [])
    print(f"\n   ✓ Total folders found: {len(all_folders)}")
except Exception as e:
    print(f"   ✗ Error querying folders: {e}")

# Update folder
if folder_id:
    print("\n5. Updating folder name...")
    try:
        updated = client.update_folder(folder_id, name="MyRenamedFolder")
        print(f"   ✓ Updated folder name to: {updated['name']}")
    except Exception as e:
        print(f"   ✗ Error updating folder: {e}")

# Delete folder (cleanup)
if folder_id:
    print("\n6. Cleaning up - deleting folder...")
    try:
        deleted = client.delete_folder(folder_id)
        print(f"   ✓ Deleted folder: {deleted['id']}")
    except Exception as e:
        print(f"   ✗ Error deleting folder: {e}")

print("\n" + "=" * 70)
print("Example completed!")
print("=" * 70)
