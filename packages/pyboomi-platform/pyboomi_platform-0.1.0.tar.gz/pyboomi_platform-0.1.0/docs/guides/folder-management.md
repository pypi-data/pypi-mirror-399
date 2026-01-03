# Folder Management

This guide covers managing folders in Boomi using the PyBoomi Platform SDK.

## Overview

Folders in Boomi provide organization for components, processes, and other resources. The SDK provides methods to create, query, update, and delete folders.

## Creating Folders

### Create a Folder in Root

```python
from pyboomi_platform import BoomiPlatformClient

client = BoomiPlatformClient(...)

# Create folder in root
folder = client.create_folder("MyNewFolder")
print(f"Created folder: {folder['id']}")
print(f"Folder name: {folder['name']}")
```

### Create a Subfolder

```python
# Create a subfolder under a parent folder
parent_id = "parent-folder-id-123"
subfolder = client.create_folder("MySubFolder", parent_id=parent_id)
print(f"Created subfolder: {subfolder['id']}")
```

## Retrieving Folders

### Get a Single Folder

```python
# Get folder by ID
folder_id = "folder-id-123"
folder = client.get_folder(folder_id)
print(f"Folder name: {folder['name']}")
print(f"Parent ID: {folder.get('parentId')}")
```

### Get Multiple Folders (Bulk)

```python
# Get multiple folders at once (max 100)
folder_ids = ["folder-id-1", "folder-id-2", "folder-id-3"]
folders = client.get_folder_bulk(folder_ids)

for folder in folders.get("result", []):
    print(f"Folder: {folder['name']} (ID: {folder['id']})")
```

## Querying Folders

### Query by Name

```python
# Query folders by name
results = client.query_folder({"name": "MyFolder"})
for folder in results.get("result", []):
    print(f"Found: {folder['name']} (ID: {folder['id']})")
```

### Query All Folders

```python
# Query all folders (no filter)
all_folders = client.query_folder()
print(f"Total folders: {len(all_folders.get('result', []))}")
```

### Pagination

```python
# Query with pagination
results = client.query_folder()
folders = results.get("result", [])

# Check if more results are available
if "queryToken" in results:
    # Get next page
    next_page = client.query_more_folders(results["queryToken"])
    more_folders = next_page.get("result", [])
    folders.extend(more_folders)
```

## Updating Folders

### Update Folder Name

```python
folder_id = "folder-id-123"
updated = client.update_folder(folder_id, name="RenamedFolder")
print(f"Updated folder name to: {updated['name']}")
```

### Move Folder to Different Parent

```python
# Move folder to a different parent
folder_id = "folder-id-123"
new_parent_id = "new-parent-id-456"
moved = client.update_folder(folder_id, parent_id=new_parent_id)
print(f"Moved folder to: {moved.get('parentId')}")
```

### Update Both Name and Parent

```python
# Update both name and parent
updated = client.update_folder(
    folder_id,
    name="NewName",
    parent_id="new-parent-id"
)
```

## Deleting Folders

```python
# Delete a folder
folder_id = "folder-id-123"
deleted = client.delete_folder(folder_id)
print(f"Deleted folder: {deleted['id']}")
```

**Note**: Ensure the folder is empty before deleting, or handle errors appropriately.

## Complete Example

```python
from pyboomi_platform import BoomiPlatformClient

client = BoomiPlatformClient(...)

# 1. Create a folder structure
root_folder = client.create_folder("Projects")
projects_id = root_folder["id"]

dev_folder = client.create_folder("Development", parent_id=projects_id)
prod_folder = client.create_folder("Production", parent_id=projects_id)

# 2. Query folders
all_folders = client.query_folder()
print(f"Total folders: {len(all_folders.get('result', []))}")

# 3. Get folder details
folder_info = client.get_folder(dev_folder["id"])
print(f"Development folder: {folder_info['name']}")

# 4. Update folder
updated = client.update_folder(
    dev_folder["id"],
    name="Dev Environment"
)

# 5. Cleanup (if needed)
# client.delete_folder(dev_folder["id"])
# client.delete_folder(prod_folder["id"])
# client.delete_folder(projects_id)
```

## Error Handling

```python
from pyboomi_platform import BoomiPlatformClient, BoomiAPIError

client = BoomiPlatformClient(...)

try:
    folder = client.create_folder("MyFolder")
except BoomiAPIError as e:
    if e.status_code == 409:
        print("Folder already exists")
    elif e.status_code == 404:
        print("Parent folder not found")
    else:
        print(f"Error: {e}")
```

## Best Practices

1. **Check for existing folders** before creating to avoid duplicates
2. **Use meaningful folder names** that reflect their purpose
3. **Organize hierarchically** using parent folders for better structure
4. **Handle pagination** when querying large numbers of folders
5. **Clean up test folders** after development/testing

## Related API Methods

- `create_folder()` - Create a new folder
- `get_folder()` - Get folder by ID
- `get_folder_bulk()` - Get multiple folders
- `query_folder()` - Query folders with filters
- `query_more_folders()` - Get next page of results
- `update_folder()` - Update folder name or parent
- `delete_folder()` - Delete a folder

For complete API reference, see [BoomiPlatformClient API](../api/client.md#folder-management).
