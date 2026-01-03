#!/usr/bin/env python3
#
# PyBoomi Platform - Client Tests
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
# Development Notes:
#     Contents of this file were produced with the help of code generation tools
#     and subsequently reviewed and edited by the author. While some code was
#     created with AI assistance, manual adjustments have been made to ensure
#     correctness, readability, functionality, and compliance with coding
#     standards. Any future modifications should preserve these manual changes.
#
# Author: Robert Little
# Created: 2025-07-27

"""
Tests for the BoomiPlatformClient class.
"""

__author__ = "Robert Little"
__copyright__ = "Copyright 2025, Robert Little"
__license__ = "Apache 2.0"
__version__ = "0.1.0"

from unittest.mock import MagicMock, patch

import pytest
import requests

from pyboomi_platform.client import BoomiPlatformClient


@pytest.fixture
def boomi_client():
    return BoomiPlatformClient(
        account_id="account123",
        username="user@boomi.com",
        api_token="mocked-token-value",
    )


@patch("requests.Session.request")
def test_query_folders_returns_data(mock_request, boomi_client):
    # Mocked response payload
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {
        "result": [
            {"id": "folder1", "name": "Integration"},
            {"id": "folder2", "name": "Shared"},
        ]
    }
    mock_request.return_value = mock_response

    # Call method under test
    filters = {"name": "Integration"}
    result = boomi_client.query_folders(filters)

    # Assertions
    assert "result" in result
    assert isinstance(result["result"], list)
    assert result["result"][0]["name"] == "Integration"

    # Ensure the correct request was made
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "POST"
    assert "Folder/query" in kwargs["url"]
    assert kwargs["json"] == filters


@patch("requests.Session.request")
def test_query_more_folders_returns_next_page(mock_request, boomi_client):
    # Simulate paginated follow-up call
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {
        "result": [{"id": "folder3", "name": "NextPageFolder"}]
    }
    mock_request.return_value = mock_response

    # This assumes you have a method like query_more_folders(token)
    token = "some-pagination-token"
    result = boomi_client._request("POST", "Folder/queryMore", data=token)

    # Assertions
    assert "result" in result
    assert result["result"][0]["name"] == "NextPageFolder"
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "POST"
    assert "queryMore" in kwargs["url"]
    assert kwargs["data"] == token


@patch("pyboomi_platform.client.requests.request")
def test_query_folders_raises_on_error(mock_request, boomi_client):
    # Simulate error from API
    mock_response = MagicMock()
    mock_response.ok = False
    mock_response.status_code = 403
    mock_response.text = "Forbidden"
    mock_request.return_value = mock_response

    with pytest.raises(Exception) as exc_info:
        boomi_client.query_folders({"name": "Invalid"})

    assert "Boomi API error" in str(exc_info.value)
    assert "403" in str(exc_info.value)


@patch("requests.Session.request")
def test_get_component_returns_xml_data(mock_request, boomi_client):
    """Test that get_component returns XML content when endpoint returns XML."""
    component_id = "component-12345"
    xml_content = """<?xml version="1.0" encoding="UTF-8"?>
<Process>
    <id>component-12345</id>
    <name>Test Process</name>
    <type>process</type>
    <version>1.0.0</version>
</Process>"""

    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/xml"}
    mock_response.text = xml_content
    mock_request.return_value = mock_response

    # Call method under test
    result = boomi_client.get_component(component_id)

    # Verify XML content is returned as text
    assert isinstance(result, str)
    assert "<?xml" in result
    assert component_id in result
    assert "Test Process" in result

    # Verify the correct request was made with Accept: application/xml header
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "GET"
    assert f"Component/{component_id}" in kwargs["url"]
    assert "Accept" in kwargs["headers"]
    assert kwargs["headers"]["Accept"] == "application/xml"


@patch("requests.Session.request")
def test_get_component_sets_accept_xml_header(mock_request, boomi_client):
    """Test that get_component explicitly sets Accept: application/xml to avoid 406 errors."""
    component_id = "component-67890"
    xml_content = "<Process><id>component-67890</id></Process>"

    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/xml; charset=utf-8"}
    mock_response.text = xml_content
    mock_request.return_value = mock_response

    # Call method under test
    result = boomi_client.get_component(component_id)

    # Verify Accept header is set correctly (overrides default Accept: application/json)
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    request_headers = kwargs.get("headers", {})
    assert request_headers.get("Accept") == "application/xml"

    # Verify XML is returned as text
    assert isinstance(result, str)
    assert result == xml_content


@patch("requests.Session.request")
def test_get_component_handles_text_xml_content_type(mock_request, boomi_client):
    """Test that get_component handles text/xml content type correctly."""
    component_id = "component-11111"
    xml_content = "<Process><name>Test</name></Process>"

    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "text/xml"}
    mock_response.text = xml_content
    mock_request.return_value = mock_response

    # Call method under test
    result = boomi_client.get_component(component_id)

    # Verify XML content is returned as text
    assert isinstance(result, str)
    assert result == xml_content


@patch("requests.Session.request")
def test_get_component_prevents_406_error(mock_request, boomi_client):
    """Test that setting Accept: application/xml prevents 406 Not Acceptable errors."""
    component_id = "component-22222"
    xml_content = "<Process><id>component-22222</id></Process>"

    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.status_code = 200
    mock_response.headers = {"Content-Type": "application/xml"}
    mock_response.text = xml_content
    mock_request.return_value = mock_response

    # Call method under test - should succeed with proper Accept header
    result = boomi_client.get_component(component_id)

    # Verify request succeeded (not 406)
    assert mock_response.ok is True
    assert mock_response.status_code == 200

    # Verify Accept header was set to application/xml
    args, kwargs = mock_request.call_args
    assert kwargs["headers"]["Accept"] == "application/xml"

    # Verify XML content returned
    assert isinstance(result, str)
    assert "<Process>" in result


@patch("requests.Session.request")
def test_get_component_handles_404_error(mock_request, boomi_client):
    """Test that get_component properly handles 404 Not Found errors."""
    component_id = "nonexistent-component"

    mock_response = MagicMock()
    mock_response.ok = False
    mock_response.status_code = 404
    mock_response.text = "Component not found"
    mock_response.json.side_effect = ValueError("Not JSON")
    mock_request.return_value = mock_response

    # Call method under test - should raise BoomiAPIError
    with pytest.raises(Exception) as exc_info:
        boomi_client.get_component(component_id)

    assert "Boomi API error" in str(exc_info.value)
    assert "404" in str(exc_info.value)

    # Verify Accept header was still set correctly
    args, kwargs = mock_request.call_args
    assert kwargs["headers"]["Accept"] == "application/xml"


@patch("requests.Session.request")
def test_get_component_handles_500_error(mock_request, boomi_client):
    """Test that get_component properly handles server errors."""
    component_id = "component-error"

    mock_response = MagicMock()
    mock_response.ok = False
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"
    mock_response.json.side_effect = ValueError("Not JSON")
    mock_request.return_value = mock_response

    # Call method under test - should raise BoomiAPIError
    with pytest.raises(Exception) as exc_info:
        boomi_client.get_component(component_id)

    assert "Boomi API error" in str(exc_info.value)
    assert "500" in str(exc_info.value)


@patch("requests.Session.request")
def test_get_packaged_component_manifest_returns_manifest(mock_request, boomi_client):
    """Test that get_packaged_component_manifest returns manifest data."""
    package_id = "12d47c77-667a-47b2-8853-a7f501e05045"
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {
        "id": package_id,
        "components": [
            {"id": "comp1", "type": "process", "name": "Test Process"},
            {"id": "comp2", "type": "connection", "name": "Test Connection"},
        ],
    }
    mock_request.return_value = mock_response

    # Call method under test
    result = boomi_client.get_packaged_component_manifest(package_id)

    # Verify response structure
    assert isinstance(result, dict)
    assert "id" in result
    assert result["id"] == package_id
    assert "components" in result

    # Verify the correct request was made
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "GET"
    assert f"PackagedComponentManifest/{package_id}" in kwargs["url"]


@patch("requests.Session.request")
def test_get_packaged_component_manifest_bulk_returns_manifests(
    mock_request, boomi_client
):
    """Test that get_packaged_component_manifest_bulk returns multiple manifests."""
    package_ids = ["12d47c77-667a-47b2-8853-a7f501e05045", "another-package-id"]
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {
        "result": [
            {
                "id": package_ids[0],
                "components": [{"id": "comp1", "type": "process"}],
            },
            {
                "id": package_ids[1],
                "components": [{"id": "comp2", "type": "connection"}],
            },
        ]
    }
    mock_request.return_value = mock_response

    # Call method under test
    result = boomi_client.get_packaged_component_manifest_bulk(package_ids)

    # Verify response structure
    assert isinstance(result, dict)
    assert "result" in result
    assert len(result["result"]) == 2

    # Verify the correct request was made
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "POST"
    assert "PackagedComponentManifest/bulk" in kwargs["url"]
    assert "json" in kwargs
    assert kwargs["json"]["type"] == "GET"
    assert len(kwargs["json"]["request"]) == 2
    assert kwargs["json"]["request"][0]["id"] == package_ids[0]
    assert kwargs["json"]["request"][1]["id"] == package_ids[1]


@patch("requests.Session.request")
def test_get_packaged_component_manifest_handles_404_error(mock_request, boomi_client):
    """Test that get_packaged_component_manifest handles 404 errors."""
    package_id = "nonexistent-package-id"
    mock_response = MagicMock()
    mock_response.ok = False
    mock_response.status_code = 404
    mock_response.text = "Package not found"
    mock_response.json.side_effect = ValueError("Not JSON")
    mock_request.return_value = mock_response

    # Call method under test - should raise BoomiAPIError
    with pytest.raises(Exception) as exc_info:
        boomi_client.get_packaged_component_manifest(package_id)

    assert "Boomi API error" in str(exc_info.value)
    assert "404" in str(exc_info.value)


@patch("requests.Session.request")
def test_update_branch_sends_put_with_optional_fields(mock_request, boomi_client):
    """Ensure update_branch sends PUT with provided optional fields."""
    branch_id = "branch-123"
    payload_response = {
        "id": branch_id,
        "name": "Renamed",
        "description": "Updated description",
        "ready": True,
    }

    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = payload_response
    mock_request.return_value = mock_response

    result = boomi_client.update_branch(
        branch_id, name="Renamed", description="Updated description", ready=True
    )

    assert result["id"] == branch_id
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "PUT"
    assert f"Branch/{branch_id}" in kwargs["url"]
    assert kwargs["json"] == {
        "name": "Renamed",
        "description": "Updated description",
        "ready": True,
    }


@patch("requests.Session.request")
def test_delete_branch_calls_delete(mock_request, boomi_client):
    """Ensure delete_branch issues DELETE to Branch/{branch_id}."""
    branch_id = "branch-to-delete"
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"id": branch_id, "status": "deleted"}
    mock_request.return_value = mock_response

    result = boomi_client.delete_branch(branch_id)

    assert result["id"] == branch_id
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "DELETE"
    assert f"Branch/{branch_id}" in kwargs["url"]


@patch("requests.Session.request")
def test_get_branch_returns_branch_data(mock_request, boomi_client):
    """Test that get_branch retrieves a branch by ID."""
    branch_id = "branch-123"
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {
        "id": branch_id,
        "name": "TestBranch",
        "ready": True,
        "parentBranchId": "parent-123",
    }
    mock_request.return_value = mock_response

    result = boomi_client.get_branch(branch_id)

    assert result["id"] == branch_id
    assert result["name"] == "TestBranch"
    assert result["ready"] is True
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "GET"
    assert f"Branch/{branch_id}" in kwargs["url"]


@patch("requests.Session.request")
def test_get_branch_handles_404_error(mock_request, boomi_client):
    """Test that get_branch properly handles 404 Not Found errors."""
    branch_id = "nonexistent-branch"
    mock_response = MagicMock()
    mock_response.ok = False
    mock_response.status_code = 404
    mock_response.text = "Branch not found"
    mock_response.json.side_effect = ValueError("Not JSON")
    mock_request.return_value = mock_response

    with pytest.raises(Exception) as exc_info:
        boomi_client.get_branch(branch_id)

    assert "Boomi API error" in str(exc_info.value)
    assert "404" in str(exc_info.value)


@patch("requests.Session.request")
def test_get_branch_handles_500_error(mock_request, boomi_client):
    """Test that get_branch properly handles server errors."""
    branch_id = "branch-error"
    mock_response = MagicMock()
    mock_response.ok = False
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"
    mock_response.json.side_effect = ValueError("Not JSON")
    mock_request.return_value = mock_response

    with pytest.raises(Exception) as exc_info:
        boomi_client.get_branch(branch_id)

    assert "Boomi API error" in str(exc_info.value)
    assert "500" in str(exc_info.value)


@patch("requests.Session.request")
def test_get_branch_returns_branch_with_metadata(mock_request, boomi_client):
    """Test that get_branch returns branch with all metadata fields."""
    branch_id = "branch-456"
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {
        "id": branch_id,
        "name": "FeatureBranch",
        "description": "Branch for feature development",
        "ready": False,
        "parentBranchId": "main-branch",
        "createdDate": "2025-01-01T00:00:00Z",
    }
    mock_request.return_value = mock_response

    result = boomi_client.get_branch(branch_id)

    assert result["id"] == branch_id
    assert result["name"] == "FeatureBranch"
    assert result["description"] == "Branch for feature development"
    assert result["ready"] is False
    assert result["parentBranchId"] == "main-branch"
    mock_request.assert_called_once()


@patch("requests.Session.request")
def test_get_branch_bulk_returns_branches(mock_request, boomi_client):
    """Ensure get_branch_bulk posts bulk request with ids."""
    branch_ids = ["b1", "b2"]
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {
        "result": [{"id": "b1"}, {"id": "b2"}],
    }
    mock_request.return_value = mock_response

    result = boomi_client.get_branch_bulk(branch_ids)

    assert "result" in result
    assert len(result["result"]) == 2
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "POST"
    assert "Branch/bulk" in kwargs["url"]
    assert kwargs["json"]["type"] == "GET"
    assert kwargs["json"]["request"][0]["id"] == "b1"
    assert kwargs["json"]["request"][1]["id"] == "b2"


@patch("requests.Session.request")
def test_query_branches_returns_filtered_results(mock_request, boomi_client):
    """Ensure query_branches posts filter payload and returns results."""
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"result": [{"id": "b1", "name": "MyBranch"}]}
    mock_request.return_value = mock_response

    filters = {"name": "MyBranch"}
    result = boomi_client.query_branches(filters)

    assert "result" in result
    assert result["result"][0]["name"] == "MyBranch"
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "POST"
    assert "Branch/query" in kwargs["url"]
    assert kwargs["json"] == filters


@patch("requests.Session.request")
def test_query_more_branches_uses_query_more_endpoint(mock_request, boomi_client):
    """Ensure query_more_branches posts token with text/plain content type."""
    token = "next-token"
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"result": [{"id": "b3"}]}
    mock_request.return_value = mock_response

    result = boomi_client.query_more_branches(token)

    assert "result" in result
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "POST"
    assert "Branch/queryMore" in kwargs["url"]
    assert kwargs["data"] == token
    assert kwargs["headers"]["Content-Type"] == "text/plain"


@patch("requests.Session.request")
def test_create_and_delete_branch_sequence_non_destructive(mock_request, boomi_client):
    """
    Ensure branch creation uses a new branch name, verifies non-existence, and deletes only that branch.
    All calls are mocked to remain non-destructive.
    """
    parent_branch_id = "parent-branch-123"
    branch_name = "test-branch-unique"

    # Responses: query (no results), create (new branch), delete (success)
    query_response = MagicMock()
    query_response.ok = True
    query_response.headers = {"Content-Type": "application/json"}
    query_response.json.return_value = {"result": []}

    created_branch_id = "branch-created-123"
    create_response = MagicMock()
    create_response.ok = True
    create_response.headers = {"Content-Type": "application/json"}
    create_response.json.return_value = {
        "id": created_branch_id,
        "name": branch_name,
        "ready": False,
    }

    delete_response = MagicMock()
    delete_response.ok = True
    delete_response.headers = {"Content-Type": "application/json"}
    delete_response.json.return_value = {"id": created_branch_id, "status": "deleted"}

    mock_request.side_effect = [query_response, create_response, delete_response]

    # 1) Verify branch does not exist
    existing = boomi_client.query_branches({"name": branch_name})
    assert existing["result"] == []

    # 2) Create branch
    created = boomi_client.create_branch(parent_branch_id, branch_name)
    assert created["id"] == created_branch_id
    assert created["name"] == branch_name

    # 3) Delete the branch just created
    deleted = boomi_client.delete_branch(created_branch_id)
    assert deleted["id"] == created_branch_id
    assert deleted["status"] == "deleted"

    assert mock_request.call_count == 3
    # Validate each call
    query_call = mock_request.call_args_list[0][1]
    assert query_call["method"] == "POST"
    assert "Branch/query" in query_call["url"]
    assert query_call["json"] == {"name": branch_name}

    create_call = mock_request.call_args_list[1][1]
    assert create_call["method"] == "POST"
    assert "Branch" in create_call["url"]
    assert create_call["json"]["parentBranchId"] == parent_branch_id
    assert create_call["json"]["name"] == branch_name

    delete_call = mock_request.call_args_list[2][1]
    assert delete_call["method"] == "DELETE"
    assert f"Branch/{created_branch_id}" in delete_call["url"]


# Folder API Tests
@patch("requests.Session.request")
def test_create_folder_without_parent(mock_request, boomi_client):
    """Test that create_folder creates a folder without a parent."""
    folder_name = "NewFolder"
    created_folder_id = "folder-123"

    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {
        "id": created_folder_id,
        "name": folder_name,
        "parentId": None,
    }
    mock_request.return_value = mock_response

    result = boomi_client.create_folder(folder_name)

    assert result["id"] == created_folder_id
    assert result["name"] == folder_name
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "POST"
    assert "Folder" in kwargs["url"]
    assert kwargs["json"] == {"@type": "Folder", "name": folder_name, "parentId": None}


@patch("requests.Session.request")
def test_create_folder_with_parent(mock_request, boomi_client):
    """Test that create_folder creates a folder with a parent."""
    folder_name = "ChildFolder"
    parent_id = "parent-folder-123"
    created_folder_id = "folder-456"

    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {
        "id": created_folder_id,
        "name": folder_name,
        "parentId": parent_id,
    }
    mock_request.return_value = mock_response

    result = boomi_client.create_folder(folder_name, parent_id=parent_id)

    assert result["id"] == created_folder_id
    assert result["name"] == folder_name
    assert result["parentId"] == parent_id
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "POST"
    assert "Folder" in kwargs["url"]
    assert kwargs["json"] == {
        "@type": "Folder",
        "name": folder_name,
        "parentId": parent_id,
    }


@patch("requests.Session.request")
def test_get_folder_returns_folder_data(mock_request, boomi_client):
    """Test that get_folder retrieves a folder by ID."""
    folder_id = "folder-789"
    folder_name = "TestFolder"

    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {
        "id": folder_id,
        "name": folder_name,
        "parentId": "parent-123",
    }
    mock_request.return_value = mock_response

    result = boomi_client.get_folder(folder_id)

    assert result["id"] == folder_id
    assert result["name"] == folder_name
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "GET"
    assert f"Folder/{folder_id}" in kwargs["url"]


@patch("requests.Session.request")
def test_get_folder_handles_404_error(mock_request, boomi_client):
    """Test that get_folder properly handles 404 Not Found errors."""
    folder_id = "nonexistent-folder"

    mock_response = MagicMock()
    mock_response.ok = False
    mock_response.status_code = 404
    mock_response.text = "Folder not found"
    mock_response.json.side_effect = ValueError("Not JSON")
    mock_request.return_value = mock_response

    with pytest.raises(Exception) as exc_info:
        boomi_client.get_folder(folder_id)

    assert "Boomi API error" in str(exc_info.value)
    assert "404" in str(exc_info.value)


@patch("requests.Session.request")
def test_update_folder_with_name_and_parent(mock_request, boomi_client):
    """Test that update_folder updates a folder with name and parent."""
    folder_id = "folder-999"
    new_name = "UpdatedFolder"
    new_parent_id = "new-parent-123"

    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {
        "id": folder_id,
        "name": new_name,
        "parentId": new_parent_id,
    }
    mock_request.return_value = mock_response

    result = boomi_client.update_folder(
        folder_id, name=new_name, parent_id=new_parent_id
    )

    assert result["id"] == folder_id
    assert result["name"] == new_name
    assert result["parentId"] == new_parent_id
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "POST"
    assert f"Folder/{folder_id}" in kwargs["url"]
    assert kwargs["json"] == {"name": new_name, "parentId": new_parent_id}


@patch("requests.Session.request")
def test_update_folder_with_name_only(mock_request, boomi_client):
    """Test that update_folder updates only the name when parent_id is not provided."""
    folder_id = "folder-888"
    new_name = "RenamedFolder"

    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {
        "id": folder_id,
        "name": new_name,
        "parentId": None,
    }
    mock_request.return_value = mock_response

    result = boomi_client.update_folder(folder_id, name=new_name)

    assert result["id"] == folder_id
    assert result["name"] == new_name
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "POST"
    assert f"Folder/{folder_id}" in kwargs["url"]
    assert kwargs["json"] == {"name": new_name, "parentId": None}


@patch("requests.Session.request")
def test_update_folder_with_parent_only(mock_request, boomi_client):
    """Test that update_folder updates only the parent when name is not provided."""
    folder_id = "folder-777"
    new_parent_id = "new-parent-456"

    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {
        "id": folder_id,
        "name": "ExistingName",
        "parentId": new_parent_id,
    }
    mock_request.return_value = mock_response

    result = boomi_client.update_folder(folder_id, parent_id=new_parent_id)

    assert result["id"] == folder_id
    assert result["parentId"] == new_parent_id
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "POST"
    assert f"Folder/{folder_id}" in kwargs["url"]
    assert kwargs["json"] == {"name": None, "parentId": new_parent_id}


@patch("requests.Session.request")
def test_delete_folder_calls_delete(mock_request, boomi_client):
    """Test that delete_folder issues DELETE to Folder/{folder_id}."""
    folder_id = "folder-to-delete"

    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"id": folder_id, "status": "deleted"}
    mock_request.return_value = mock_response

    result = boomi_client.delete_folder(folder_id)

    assert result["id"] == folder_id
    assert result["status"] == "deleted"
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "DELETE"
    assert f"Folder/{folder_id}" in kwargs["url"]


@patch("requests.Session.request")
def test_delete_folder_handles_404_error(mock_request, boomi_client):
    """Test that delete_folder properly handles 404 Not Found errors."""
    folder_id = "nonexistent-folder"

    mock_response = MagicMock()
    mock_response.ok = False
    mock_response.status_code = 404
    mock_response.text = "Folder not found"
    mock_response.json.side_effect = ValueError("Not JSON")
    mock_request.return_value = mock_response

    with pytest.raises(Exception) as exc_info:
        boomi_client.delete_folder(folder_id)

    assert "Boomi API error" in str(exc_info.value)
    assert "404" in str(exc_info.value)


@patch("requests.Session.request")
def test_get_folder_bulk_returns_folders(mock_request, boomi_client):
    """Test that get_folder_bulk retrieves multiple folders by IDs."""
    folder_ids = ["folder-1", "folder-2", "folder-3"]

    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {
        "result": [
            {"id": "folder-1", "name": "Folder1"},
            {"id": "folder-2", "name": "Folder2"},
            {"id": "folder-3", "name": "Folder3"},
        ]
    }
    mock_request.return_value = mock_response

    result = boomi_client.get_folder_bulk(folder_ids)

    assert "result" in result
    assert len(result["result"]) == 3
    assert result["result"][0]["id"] == "folder-1"
    assert result["result"][1]["id"] == "folder-2"
    assert result["result"][2]["id"] == "folder-3"
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "POST"
    assert "Folder/bulk" in kwargs["url"]
    assert kwargs["json"] == {"ids": folder_ids}


@patch("requests.Session.request")
def test_query_folder_returns_filtered_results(mock_request, boomi_client):
    """Test that query_folder posts filter payload and returns results."""
    filters = {"name": "MyFolder"}

    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {
        "result": [{"id": "folder-123", "name": "MyFolder"}]
    }
    mock_request.return_value = mock_response

    result = boomi_client.query_folder(filters)

    assert "result" in result
    assert result["result"][0]["name"] == "MyFolder"
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "POST"
    assert "Folder/query" in kwargs["url"]
    assert kwargs["json"] == filters


@patch("requests.Session.request")
def test_query_folder_without_filters(mock_request, boomi_client):
    """Test that query_folder works without filters (uses empty dict)."""
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {
        "result": [
            {"id": "folder-1", "name": "Folder1"},
            {"id": "folder-2", "name": "Folder2"},
        ]
    }
    mock_request.return_value = mock_response

    result = boomi_client.query_folder()

    assert "result" in result
    assert len(result["result"]) == 2
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "POST"
    assert "Folder/query" in kwargs["url"]
    assert kwargs["json"] == {}


@patch("requests.Session.request")
def test_query_more_folders_uses_query_more_endpoint(mock_request, boomi_client):
    """Test that query_more_folders posts token with text/plain content type."""
    token = "next-page-token"

    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {
        "result": [{"id": "folder-4", "name": "NextPageFolder"}]
    }
    mock_request.return_value = mock_response

    result = boomi_client.query_more_folders(token)

    assert "result" in result
    assert result["result"][0]["name"] == "NextPageFolder"
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "POST"
    assert "Folder/queryMore" in kwargs["url"]
    assert kwargs["data"] == token
    assert kwargs["headers"]["Content-Type"] == "text/plain"


@patch("requests.Session.request")
def test_create_and_delete_folder_sequence(mock_request, boomi_client):
    """Test a complete sequence of creating and deleting a folder."""
    folder_name = "TestFolder"
    created_folder_id = "folder-created-123"

    # Mock responses: create (new folder), delete (success)
    create_response = MagicMock()
    create_response.ok = True
    create_response.headers = {"Content-Type": "application/json"}
    create_response.json.return_value = {
        "id": created_folder_id,
        "name": folder_name,
        "parentId": None,
    }

    delete_response = MagicMock()
    delete_response.ok = True
    delete_response.headers = {"Content-Type": "application/json"}
    delete_response.json.return_value = {
        "id": created_folder_id,
        "status": "deleted",
    }

    mock_request.side_effect = [create_response, delete_response]

    # Create folder
    created = boomi_client.create_folder(folder_name)
    assert created["id"] == created_folder_id
    assert created["name"] == folder_name

    # Delete the folder
    deleted = boomi_client.delete_folder(created_folder_id)
    assert deleted["id"] == created_folder_id
    assert deleted["status"] == "deleted"

    assert mock_request.call_count == 2
    # Validate create call
    create_call = mock_request.call_args_list[0][1]
    assert create_call["method"] == "POST"
    assert "Folder" in create_call["url"]
    assert create_call["json"]["name"] == folder_name

    # Validate delete call
    delete_call = mock_request.call_args_list[1][1]
    assert delete_call["method"] == "DELETE"
    assert f"Folder/{created_folder_id}" in delete_call["url"]


@patch("requests.Session.request")
def test_get_folder_handles_500_error(mock_request, boomi_client):
    """Test that get_folder properly handles server errors."""
    folder_id = "folder-error"

    mock_response = MagicMock()
    mock_response.ok = False
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"
    mock_response.json.side_effect = ValueError("Not JSON")
    mock_request.return_value = mock_response

    with pytest.raises(Exception) as exc_info:
        boomi_client.get_folder(folder_id)

    assert "Boomi API error" in str(exc_info.value)
    assert "500" in str(exc_info.value)


# Component API Tests
@patch("requests.Session.request")
def test_create_component_with_xml(mock_request, boomi_client):
    """Test that create_component creates a component from XML content."""
    component_xml = """<?xml version="1.0" encoding="UTF-8"?>
<Process>
    <name>TestProcess</name>
    <type>process</type>
</Process>"""
    created_component_xml = """<?xml version="1.0" encoding="UTF-8"?>
<Process>
    <id>component-12345</id>
    <name>TestProcess</name>
    <type>process</type>
</Process>"""

    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.status_code = 200
    mock_response.headers = {"Content-Type": "application/xml"}
    mock_response.text = created_component_xml
    mock_request.return_value = mock_response

    result = boomi_client.create_component(component_xml)

    assert isinstance(result, str)
    assert "<?xml" in result
    assert "component-12345" in result
    assert "TestProcess" in result
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "POST"
    assert "Component" in kwargs["url"]
    assert kwargs["data"] == component_xml
    assert kwargs["headers"]["Content-Type"] == "application/xml"
    assert kwargs["headers"]["Accept"] == "application/xml"


@patch("requests.Session.request")
def test_create_component_with_folder_id(mock_request, boomi_client):
    """Test that create_component creates a component in a specific folder."""
    component_xml = """<?xml version="1.0" encoding="UTF-8"?>
<Process>
    <name>TestProcess</name>
    <type>process</type>
</Process>"""
    folder_id = "folder-123"
    created_component_xml = """<?xml version="1.0" encoding="UTF-8"?>
<Process>
    <id>component-67890</id>
    <name>TestProcess</name>
    <type>process</type>
</Process>"""

    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.status_code = 200
    mock_response.headers = {"Content-Type": "application/xml"}
    mock_response.text = created_component_xml
    mock_request.return_value = mock_response

    result = boomi_client.create_component(component_xml, folder_id=folder_id)

    assert isinstance(result, str)
    assert "component-67890" in result
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "POST"
    assert f"Component?folderId={folder_id}" in kwargs["url"]
    assert kwargs["data"] == component_xml
    assert kwargs["headers"]["Content-Type"] == "application/xml"
    assert kwargs["headers"]["Accept"] == "application/xml"


@patch("requests.Session.request")
def test_create_component_handles_400_error(mock_request, boomi_client):
    """Test that create_component properly handles 400 Bad Request errors."""
    invalid_xml = "<Invalid>XML</Invalid>"

    mock_response = MagicMock()
    mock_response.ok = False
    mock_response.status_code = 400
    mock_response.text = "Invalid component XML"
    mock_response.json.side_effect = ValueError("Not JSON")
    mock_request.return_value = mock_response

    with pytest.raises(Exception) as exc_info:
        boomi_client.create_component(invalid_xml)

    assert "Boomi API error" in str(exc_info.value)
    assert "400" in str(exc_info.value)

    # Verify headers were still set correctly
    args, kwargs = mock_request.call_args
    assert kwargs["headers"]["Content-Type"] == "application/xml"
    assert kwargs["headers"]["Accept"] == "application/xml"


@patch("requests.Session.request")
def test_create_component_handles_404_error(mock_request, boomi_client):
    """Test that create_component properly handles 404 Not Found errors (e.g., folder not found)."""
    component_xml = """<?xml version="1.0" encoding="UTF-8"?>
<Process>
    <name>TestProcess</name>
</Process>"""
    folder_id = "nonexistent-folder"

    mock_response = MagicMock()
    mock_response.ok = False
    mock_response.status_code = 404
    mock_response.text = "Folder not found"
    mock_response.json.side_effect = ValueError("Not JSON")
    mock_request.return_value = mock_response

    with pytest.raises(Exception) as exc_info:
        boomi_client.create_component(component_xml, folder_id=folder_id)

    assert "Boomi API error" in str(exc_info.value)
    assert "404" in str(exc_info.value)


@patch("requests.Session.request")
def test_create_component_handles_500_error(mock_request, boomi_client):
    """Test that create_component properly handles server errors."""
    component_xml = """<?xml version="1.0" encoding="UTF-8"?>
<Process>
    <name>TestProcess</name>
</Process>"""

    mock_response = MagicMock()
    mock_response.ok = False
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"
    mock_response.json.side_effect = ValueError("Not JSON")
    mock_request.return_value = mock_response

    with pytest.raises(Exception) as exc_info:
        boomi_client.create_component(component_xml)

    assert "Boomi API error" in str(exc_info.value)
    assert "500" in str(exc_info.value)


@patch("requests.Session.request")
def test_create_component_with_connection_xml(mock_request, boomi_client):
    """Test that create_component works with different component types (e.g., Connection)."""
    connection_xml = """<?xml version="1.0" encoding="UTF-8"?>
<Connection>
    <name>TestConnection</name>
    <type>connection</type>
</Connection>"""
    created_connection_xml = """<?xml version="1.0" encoding="UTF-8"?>
<Connection>
    <id>connection-11111</id>
    <name>TestConnection</name>
    <type>connection</type>
</Connection>"""

    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.status_code = 200
    mock_response.headers = {"Content-Type": "application/xml"}
    mock_response.text = created_connection_xml
    mock_request.return_value = mock_response

    result = boomi_client.create_component(connection_xml)

    assert isinstance(result, str)
    assert "connection-11111" in result
    assert "TestConnection" in result
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "POST"
    assert "Component" in kwargs["url"]
    assert kwargs["data"] == connection_xml


@patch("requests.Session.request")
def test_update_component(mock_request, boomi_client):
    """Test that update_component updates a component from XML content."""
    component_id = "component-12345"
    component_xml = """<?xml version="1.0" encoding="UTF-8"?>
<Process>
    <id>component-12345</id>
    <name>UpdatedProcess</name>
    <type>process</type>
</Process>"""
    updated_component_xml = """<?xml version="1.0" encoding="UTF-8"?>
<Process>
    <id>component-12345</id>
    <name>UpdatedProcess</name>
    <type>process</type>
    <version>2.0.0</version>
</Process>"""

    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.status_code = 200
    mock_response.headers = {"Content-Type": "application/xml"}
    mock_response.text = updated_component_xml
    mock_request.return_value = mock_response

    result = boomi_client.update_component(component_id, component_xml)

    assert isinstance(result, str)
    assert "<?xml" in result
    assert component_id in result
    assert "UpdatedProcess" in result
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "POST"
    assert f"Component/{component_id}" in kwargs["url"]
    assert kwargs["data"] == component_xml
    assert kwargs["headers"]["Content-Type"] == "application/xml"
    assert kwargs["headers"]["Accept"] == "application/xml"


@patch("requests.Session.request")
def test_update_component_handles_400_error(mock_request, boomi_client):
    """Test that update_component properly handles 400 Bad Request errors."""
    component_id = "component-12345"
    invalid_xml = "<Invalid>XML</Invalid>"

    mock_response = MagicMock()
    mock_response.ok = False
    mock_response.status_code = 400
    mock_response.text = "Invalid component XML"
    mock_response.json.side_effect = ValueError("Not JSON")
    mock_request.return_value = mock_response

    with pytest.raises(Exception) as exc_info:
        boomi_client.update_component(component_id, invalid_xml)

    assert "Boomi API error" in str(exc_info.value)
    assert "400" in str(exc_info.value)

    # Verify headers were still set correctly
    args, kwargs = mock_request.call_args
    assert kwargs["headers"]["Content-Type"] == "application/xml"
    assert kwargs["headers"]["Accept"] == "application/xml"


@patch("requests.Session.request")
def test_update_component_handles_404_error(mock_request, boomi_client):
    """Test that update_component properly handles 404 Not Found errors."""
    component_id = "nonexistent-component"
    component_xml = """<?xml version="1.0" encoding="UTF-8"?>
<Process>
    <name>TestProcess</name>
</Process>"""

    mock_response = MagicMock()
    mock_response.ok = False
    mock_response.status_code = 404
    mock_response.text = "Component not found"
    mock_response.json.side_effect = ValueError("Not JSON")
    mock_request.return_value = mock_response

    with pytest.raises(Exception) as exc_info:
        boomi_client.update_component(component_id, component_xml)

    assert "Boomi API error" in str(exc_info.value)
    assert "404" in str(exc_info.value)


@patch("requests.Session.request")
def test_get_component_bulk(mock_request, boomi_client):
    """Test that get_component_bulk retrieves multiple components by their IDs."""
    component_ids = ["component-1", "component-2", "component-3"]
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {
        "result": [
            {"id": "component-1", "name": "Process1"},
            {"id": "component-2", "name": "Process2"},
            {"id": "component-3", "name": "Process3"},
        ]
    }
    mock_request.return_value = mock_response

    result = boomi_client.get_component_bulk(component_ids)

    assert "result" in result
    assert len(result["result"]) == 3
    assert result["result"][0]["id"] == "component-1"
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "POST"
    assert "Component/bulk" in kwargs["url"]
    assert kwargs["json"] == {"ids": component_ids}


@patch("requests.Session.request")
def test_get_component_bulk_handles_empty_list(mock_request, boomi_client):
    """Test that get_component_bulk handles empty component ID list."""
    component_ids = []
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"result": []}
    mock_request.return_value = mock_response

    result = boomi_client.get_component_bulk(component_ids)

    assert "result" in result
    assert result["result"] == []
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["json"] == {"ids": []}


@patch("requests.Session.request")
def test_get_component_bulk_handles_error(mock_request, boomi_client):
    """Test that get_component_bulk properly handles API errors."""
    component_ids = ["component-1", "component-2"]
    mock_response = MagicMock()
    mock_response.ok = False
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"
    mock_response.json.side_effect = ValueError("Not JSON")
    mock_request.return_value = mock_response

    with pytest.raises(Exception) as exc_info:
        boomi_client.get_component_bulk(component_ids)

    assert "Boomi API error" in str(exc_info.value)
    assert "500" in str(exc_info.value)


# Retry-After and Rate Limiting Tests
@patch("requests.Session.request")
@patch("time.sleep")
def test_request_respects_retry_after_header_429(
    mock_sleep, mock_request, boomi_client
):
    """Test that _request respects Retry-After header for 429 responses."""
    # First response: 429 with Retry-After header
    rate_limit_response = MagicMock()
    rate_limit_response.status_code = 429
    rate_limit_response.ok = False
    rate_limit_response.headers = {"Retry-After": "2.5"}
    rate_limit_response.text = "Rate limit exceeded"
    rate_limit_response.json.side_effect = ValueError("Not JSON")

    # Second response: success
    success_response = MagicMock()
    success_response.ok = True
    success_response.status_code = 200
    success_response.headers = {"Content-Type": "application/json"}
    success_response.json.return_value = {"result": "success"}

    mock_request.side_effect = [rate_limit_response, success_response]

    result = boomi_client._request("GET", "TestEndpoint")

    assert result == {"result": "success"}
    assert mock_request.call_count == 2
    # Verify sleep was called with Retry-After value
    mock_sleep.assert_called_once_with(2.5)


@patch("requests.Session.request")
@patch("time.sleep")
def test_request_respects_retry_after_header_503(
    mock_sleep, mock_request, boomi_client
):
    """Test that _request respects Retry-After header for 503 responses."""
    # First response: 503 with Retry-After header
    service_unavailable_response = MagicMock()
    service_unavailable_response.status_code = 503
    service_unavailable_response.ok = False
    service_unavailable_response.headers = {"Retry-After": "5.0"}
    service_unavailable_response.text = "Service unavailable"
    service_unavailable_response.json.side_effect = ValueError("Not JSON")

    # Second response: success
    success_response = MagicMock()
    success_response.ok = True
    success_response.status_code = 200
    success_response.headers = {"Content-Type": "application/json"}
    success_response.json.return_value = {"result": "success"}

    mock_request.side_effect = [service_unavailable_response, success_response]

    result = boomi_client._request("GET", "TestEndpoint")

    assert result == {"result": "success"}
    assert mock_request.call_count == 2
    # Verify sleep was called with Retry-After value
    mock_sleep.assert_called_once_with(5.0)


@patch("requests.Session.request")
@patch("time.sleep")
def test_request_falls_back_to_exponential_backoff_when_no_retry_after(
    mock_sleep, mock_request, boomi_client
):
    """Test that _request uses exponential backoff when Retry-After header is missing."""
    # First response: 429 without Retry-After header
    rate_limit_response = MagicMock()
    rate_limit_response.status_code = 429
    rate_limit_response.ok = False
    rate_limit_response.headers = {}  # No Retry-After header
    rate_limit_response.text = "Rate limit exceeded"
    rate_limit_response.json.side_effect = ValueError("Not JSON")

    # Second response: success
    success_response = MagicMock()
    success_response.ok = True
    success_response.status_code = 200
    success_response.headers = {"Content-Type": "application/json"}
    success_response.json.return_value = {"result": "success"}

    mock_request.side_effect = [rate_limit_response, success_response]

    result = boomi_client._request("GET", "TestEndpoint")

    assert result == {"result": "success"}
    assert mock_request.call_count == 2
    # Verify sleep was called with backoff_factor (1.5)
    mock_sleep.assert_called_once_with(1.5)


@patch("requests.Session.request")
@patch("time.sleep")
def test_request_raises_error_after_max_retries_429(
    mock_sleep, mock_request, boomi_client
):
    """Test that _request raises error after max retries for 429 responses."""
    rate_limit_response = MagicMock()
    rate_limit_response.status_code = 429
    rate_limit_response.ok = False
    rate_limit_response.headers = {"Retry-After": "1.0"}
    rate_limit_response.text = "Rate limit exceeded"
    rate_limit_response.json.side_effect = ValueError("Not JSON")

    # Set max_retries to 2, so we'll retry twice then fail
    mock_request.return_value = rate_limit_response

    with pytest.raises(Exception) as exc_info:
        boomi_client._request("GET", "TestEndpoint", max_retries=2)

    assert "Boomi API rate limit error" in str(exc_info.value)
    assert "429" in str(exc_info.value)
    # Should have tried 3 times (initial + 2 retries)
    assert mock_request.call_count == 3
    assert mock_sleep.call_count == 2


@patch("requests.Session.request")
@patch("time.sleep")
def test_request_handles_invalid_retry_after_header(
    mock_sleep, mock_request, boomi_client
):
    """Test that _request handles invalid Retry-After header values gracefully."""
    # First response: 429 with invalid Retry-After header
    rate_limit_response = MagicMock()
    rate_limit_response.status_code = 429
    rate_limit_response.ok = False
    rate_limit_response.headers = {"Retry-After": "invalid"}
    rate_limit_response.text = "Rate limit exceeded"
    rate_limit_response.json.side_effect = ValueError("Not JSON")

    # Second response: success
    success_response = MagicMock()
    success_response.ok = True
    success_response.status_code = 200
    success_response.headers = {"Content-Type": "application/json"}
    success_response.json.return_value = {"result": "success"}

    mock_request.side_effect = [rate_limit_response, success_response]

    result = boomi_client._request("GET", "TestEndpoint")

    assert result == {"result": "success"}
    # Should fall back to exponential backoff when Retry-After is invalid
    mock_sleep.assert_called_once_with(1.5)


@patch("pyboomi_platform.client.logger")
@patch("requests.Session.request")
@patch("time.sleep")
def test_request_logs_warning_on_429_retry_with_retry_after(
    mock_sleep, mock_request, mock_logger, boomi_client
):
    """Test that logger.warning is called when retrying after 429 with Retry-After header."""
    # First response: 429 with Retry-After header
    rate_limit_response = MagicMock()
    rate_limit_response.status_code = 429
    rate_limit_response.ok = False
    rate_limit_response.headers = {"Retry-After": "2.5"}
    rate_limit_response.text = "Rate limit exceeded"
    rate_limit_response.json.side_effect = ValueError("Not JSON")

    # Second response: success
    success_response = MagicMock()
    success_response.ok = True
    success_response.status_code = 200
    success_response.headers = {"Content-Type": "application/json"}
    success_response.json.return_value = {"result": "success"}

    mock_request.side_effect = [rate_limit_response, success_response]

    result = boomi_client._request("GET", "TestEndpoint")

    assert result == {"result": "success"}
    # Verify logger.warning was called
    mock_logger.warning.assert_called_once()
    warning_call = mock_logger.warning.call_args[0][0]
    assert "Rate limit hit (HTTP 429)" in warning_call
    assert "Retrying in 2.50 seconds" in warning_call
    assert "Attempt 1/3" in warning_call


@patch("pyboomi_platform.client.logger")
@patch("requests.Session.request")
@patch("time.sleep")
def test_request_logs_warning_on_503_retry_with_retry_after(
    mock_sleep, mock_request, mock_logger, boomi_client
):
    """Test that logger.warning is called when retrying after 503 with Retry-After header."""
    # First response: 503 with Retry-After header
    service_unavailable_response = MagicMock()
    service_unavailable_response.status_code = 503
    service_unavailable_response.ok = False
    service_unavailable_response.headers = {"Retry-After": "5.0"}
    service_unavailable_response.text = "Service unavailable"
    service_unavailable_response.json.side_effect = ValueError("Not JSON")

    # Second response: success
    success_response = MagicMock()
    success_response.ok = True
    success_response.status_code = 200
    success_response.headers = {"Content-Type": "application/json"}
    success_response.json.return_value = {"result": "success"}

    mock_request.side_effect = [service_unavailable_response, success_response]

    result = boomi_client._request("GET", "TestEndpoint")

    assert result == {"result": "success"}
    # Verify logger.warning was called
    mock_logger.warning.assert_called_once()
    warning_call = mock_logger.warning.call_args[0][0]
    assert "Rate limit hit (HTTP 503)" in warning_call
    assert "Retrying in 5.00 seconds" in warning_call
    assert "Attempt 1/3" in warning_call


@patch("pyboomi_platform.client.logger")
@patch("requests.Session.request")
@patch("time.sleep")
def test_request_logs_warning_on_429_retry_without_retry_after(
    mock_sleep, mock_request, mock_logger, boomi_client
):
    """Test that logger.warning is called when retrying after 429 without Retry-After header."""
    # First response: 429 without Retry-After header
    rate_limit_response = MagicMock()
    rate_limit_response.status_code = 429
    rate_limit_response.ok = False
    rate_limit_response.headers = {}  # No Retry-After header
    rate_limit_response.text = "Rate limit exceeded"
    rate_limit_response.json.side_effect = ValueError("Not JSON")

    # Second response: success
    success_response = MagicMock()
    success_response.ok = True
    success_response.status_code = 200
    success_response.headers = {"Content-Type": "application/json"}
    success_response.json.return_value = {"result": "success"}

    mock_request.side_effect = [rate_limit_response, success_response]

    result = boomi_client._request("GET", "TestEndpoint")

    assert result == {"result": "success"}
    # Verify logger.warning was called with exponential backoff
    mock_logger.warning.assert_called_once()
    warning_call = mock_logger.warning.call_args[0][0]
    assert "Rate limit hit (HTTP 429)" in warning_call
    assert "Retrying in 1.50 seconds" in warning_call  # backoff_factor = 1.5
    assert "Attempt 1/3" in warning_call


@patch("pyboomi_platform.client.logger")
@patch("requests.Session.request")
@patch("time.sleep")
def test_request_logs_warning_on_request_exception_retry(
    mock_sleep, mock_request, mock_logger, boomi_client
):
    """Test that logger.warning is called when retrying after RequestException."""
    # First call: RequestException
    request_exception = requests.exceptions.RequestException("Connection error")
    # Second call: success
    success_response = MagicMock()
    success_response.ok = True
    success_response.status_code = 200
    success_response.headers = {"Content-Type": "application/json"}
    success_response.json.return_value = {"result": "success"}

    mock_request.side_effect = [request_exception, success_response]

    result = boomi_client._request("GET", "TestEndpoint")

    assert result == {"result": "success"}
    # Verify logger.warning was called
    mock_logger.warning.assert_called_once()
    warning_call = mock_logger.warning.call_args[0][0]
    assert "Request error:" in warning_call
    assert "Retrying in 1.50 seconds" in warning_call
    assert "Attempt 1/3" in warning_call


@patch("pyboomi_platform.client.logger")
@patch("requests.Session.request")
@patch("time.sleep")
def test_request_logs_warning_multiple_times_on_multiple_retries(
    mock_sleep, mock_request, mock_logger, boomi_client
):
    """Test that logger.warning is called multiple times when multiple retries occur."""
    # First two responses: 429 rate limit
    rate_limit_response = MagicMock()
    rate_limit_response.status_code = 429
    rate_limit_response.ok = False
    rate_limit_response.headers = {"Retry-After": "1.0"}
    rate_limit_response.text = "Rate limit exceeded"
    rate_limit_response.json.side_effect = ValueError("Not JSON")

    # Third response: success
    success_response = MagicMock()
    success_response.ok = True
    success_response.status_code = 200
    success_response.headers = {"Content-Type": "application/json"}
    success_response.json.return_value = {"result": "success"}

    mock_request.side_effect = [
        rate_limit_response,
        rate_limit_response,
        success_response,
    ]

    result = boomi_client._request("GET", "TestEndpoint", max_retries=2)

    assert result == {"result": "success"}
    # Verify logger.warning was called twice (for two retries)
    assert mock_logger.warning.call_count == 2

    # Check first warning call
    first_warning = mock_logger.warning.call_args_list[0][0][0]
    assert "Rate limit hit (HTTP 429)" in first_warning
    assert "Attempt 1/2" in first_warning

    # Check second warning call
    second_warning = mock_logger.warning.call_args_list[1][0][0]
    assert "Rate limit hit (HTTP 429)" in second_warning
    assert "Attempt 2/2" in second_warning


# Branch API Additional Tests
@patch("requests.Session.request")
def test_create_branch_with_package_id(mock_request, boomi_client):
    """Test that create_branch includes packageId when provided."""
    parent_branch_id = "parent-branch-123"
    branch_name = "test-branch"
    package_id = "package-12345"

    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {
        "id": "branch-123",
        "name": branch_name,
        "parentBranchId": parent_branch_id,
        "packageId": package_id,
        "ready": False,
    }
    mock_request.return_value = mock_response

    result = boomi_client.create_branch(
        parent_branch_id, branch_name, package_id=package_id
    )

    assert result["id"] == "branch-123"
    assert result["packageId"] == package_id
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "POST"
    assert "Branch" in kwargs["url"]
    assert kwargs["json"]["parentBranchId"] == parent_branch_id
    assert kwargs["json"]["name"] == branch_name
    assert kwargs["json"]["packageId"] == package_id


@patch("requests.Session.request")
def test_create_branch_without_package_id(mock_request, boomi_client):
    """Test that create_branch does not include packageId when not provided."""
    parent_branch_id = "parent-branch-123"
    branch_name = "test-branch"

    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {
        "id": "branch-123",
        "name": branch_name,
        "parentBranchId": parent_branch_id,
        "ready": False,
    }
    mock_request.return_value = mock_response

    result = boomi_client.create_branch(parent_branch_id, branch_name)

    assert result["id"] == "branch-123"
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "POST"
    assert "Branch" in kwargs["url"]
    assert kwargs["json"]["parentBranchId"] == parent_branch_id
    assert kwargs["json"]["name"] == branch_name
    assert "packageId" not in kwargs["json"]


@patch("requests.Session.request")
def test_update_branch_name_only(mock_request, boomi_client):
    """Test that update_branch updates only the name when other fields are not provided."""
    branch_id = "branch-123"
    new_name = "UpdatedBranchName"

    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {
        "id": branch_id,
        "name": new_name,
    }
    mock_request.return_value = mock_response

    result = boomi_client.update_branch(branch_id, name=new_name)

    assert result["id"] == branch_id
    assert result["name"] == new_name
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "PUT"
    assert f"Branch/{branch_id}" in kwargs["url"]
    assert kwargs["json"] == {"name": new_name}


@patch("requests.Session.request")
def test_update_branch_description_only(mock_request, boomi_client):
    """Test that update_branch updates only the description when other fields are not provided."""
    branch_id = "branch-123"
    new_description = "Updated description"

    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {
        "id": branch_id,
        "description": new_description,
    }
    mock_request.return_value = mock_response

    result = boomi_client.update_branch(branch_id, description=new_description)

    assert result["id"] == branch_id
    assert result["description"] == new_description
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "PUT"
    assert f"Branch/{branch_id}" in kwargs["url"]
    assert kwargs["json"] == {"description": new_description}


@patch("requests.Session.request")
def test_update_branch_ready_only(mock_request, boomi_client):
    """Test that update_branch updates only the ready flag when other fields are not provided."""
    branch_id = "branch-123"
    ready = True

    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {
        "id": branch_id,
        "ready": ready,
    }
    mock_request.return_value = mock_response

    result = boomi_client.update_branch(branch_id, ready=ready)

    assert result["id"] == branch_id
    assert result["ready"] == ready
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "PUT"
    assert f"Branch/{branch_id}" in kwargs["url"]
    assert kwargs["json"] == {"ready": ready}


# Execution Artifact and Connector API Tests
@patch("requests.Session.request")
def test_query_execution_record(mock_request, boomi_client):
    """Test that query_execution_record queries for execution records by execution ID."""
    execution_id = "exec-12345"

    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {
        "result": [
            {"id": "record-1", "executionId": execution_id},
            {"id": "record-2", "executionId": execution_id},
        ]
    }
    mock_request.return_value = mock_response

    result = boomi_client.query_execution_record(execution_id)

    assert "result" in result
    assert len(result["result"]) == 2
    assert result["result"][0]["executionId"] == execution_id
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "POST"
    assert "ExecutionRecord/query" in kwargs["url"]
    assert (
        kwargs["json"]["QueryFilter"]["expression"]["nestedExpression"][0]["argument"][
            0
        ]
        == execution_id
    )


@patch("requests.Session.request")
def test_query_more_execution_record(mock_request, boomi_client):
    """Test that query_more_execution_record retrieves next page of execution records."""
    query_token = "next-page-token"

    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"result": [{"id": "record-3"}]}
    mock_request.return_value = mock_response

    result = boomi_client.query_more_execution_record(query_token)

    assert "result" in result
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "POST"
    assert "ExecutionRecord/queryMore" in kwargs["url"]
    assert kwargs["data"] == query_token
    assert kwargs["headers"]["Content-Type"] == "text/plain"


@patch("requests.Session.request")
def test_create_execution_artifacts_request(mock_request, boomi_client):
    """Test that create_execution_artifacts_request creates an artifacts request."""
    execution_id = "exec-12345"

    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {
        "url": "https://api.boomi.com/download/artifacts-123",
        "executionId": execution_id,
    }
    mock_request.return_value = mock_response

    result = boomi_client.create_execution_artifacts_request(execution_id)

    assert "url" in result
    assert result["executionId"] == execution_id
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "POST"
    assert "ExecutionArtifacts" in kwargs["url"]
    assert kwargs["json"]["executionId"] == execution_id


@patch("requests.Session.request")
def test_create_process_log_request(mock_request, boomi_client):
    """Test that create_process_log_request creates a process log request."""
    execution_id = "exec-12345"
    log_level = "ALL"

    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {
        "url": "https://api.boomi.com/download/logs-123",
        "executionId": execution_id,
        "logLevel": log_level,
    }
    mock_request.return_value = mock_response

    result = boomi_client.create_process_log_request(execution_id, log_level=log_level)

    assert "url" in result
    assert result["executionId"] == execution_id
    assert result["logLevel"] == log_level
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "POST"
    assert "ProcessLog" in kwargs["url"]
    assert kwargs["json"]["executionId"] == execution_id
    assert kwargs["json"]["logLevel"] == log_level


@patch("requests.Session.request")
def test_create_process_log_request_default_log_level(mock_request, boomi_client):
    """Test that create_process_log_request uses default log level when not provided."""
    execution_id = "exec-12345"

    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {
        "url": "https://api.boomi.com/download/logs-123",
        "executionId": execution_id,
        "logLevel": "INFO",
    }
    mock_request.return_value = mock_response

    result = boomi_client.create_process_log_request(execution_id)

    assert result["logLevel"] == "INFO"
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["json"]["logLevel"] == "INFO"


@patch("requests.Session.request")
def test_query_execution_connector(mock_request, boomi_client):
    """Test that query_execution_connector queries for execution connectors."""
    execution_id = "exec-12345"

    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {
        "result": [
            {"id": "connector-1", "executionId": execution_id},
        ]
    }
    mock_request.return_value = mock_response

    result = boomi_client.query_execution_connector(execution_id)

    assert "result" in result
    assert result["result"][0]["executionId"] == execution_id
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "POST"
    assert "ExecutionConnector/query" in kwargs["url"]
    assert kwargs["json"]["QueryFilter"]["expression"]["argument"][0] == execution_id


@patch("requests.Session.request")
def test_query_more_execution_connector(mock_request, boomi_client):
    """Test that query_more_execution_connector retrieves next page of connectors."""
    query_token = "next-page-token"

    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"result": [{"id": "connector-2"}]}
    mock_request.return_value = mock_response

    result = boomi_client.query_more_execution_connector(query_token)

    assert "result" in result
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "POST"
    assert "ExecutionConnector/queryMore" in kwargs["url"]
    assert kwargs["data"] == query_token
    assert kwargs["headers"]["Content-Type"] == "text/plain"


@patch("requests.Session.request")
def test_query_generic_connector_record(mock_request, boomi_client):
    """Test that query_generic_connector_record queries for generic connector records."""
    execution_id = "exec-12345"
    execution_connector_id = "connector-123"

    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {
        "result": [
            {
                "id": "record-1",
                "executionId": execution_id,
                "executionConnectorId": execution_connector_id,
            }
        ]
    }
    mock_request.return_value = mock_response

    result = boomi_client.query_generic_connector_record(
        execution_id, execution_connector_id
    )

    assert "result" in result
    assert result["result"][0]["executionId"] == execution_id
    assert result["result"][0]["executionConnectorId"] == execution_connector_id
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "POST"
    assert "GenericConnectorRecord/query" in kwargs["url"]
    nested_expr = kwargs["json"]["QueryFilter"]["expression"]["nestedExpression"]
    assert nested_expr[0]["argument"][0] == execution_id
    assert nested_expr[1]["argument"][0] == execution_connector_id


@patch("requests.Session.request")
def test_query_more_generic_connector_record(mock_request, boomi_client):
    """Test that query_more_generic_connector_record retrieves next page."""
    query_token = "next-page-token"

    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"result": [{"id": "record-2"}]}
    mock_request.return_value = mock_response

    result = boomi_client.query_more_generic_connector_record(query_token)

    assert "result" in result
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "POST"
    assert "GenericConnectorRecord/queryMore" in kwargs["url"]
    assert kwargs["data"] == query_token
    assert kwargs["headers"]["Content-Type"] == "text/plain"


@patch("requests.Session.request")
def test_get_connector_document_url(mock_request, boomi_client):
    """Test that get_connector_document_url requests a connector document download URL."""
    generic_connector_record_id = "record-123"

    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {
        "url": "https://api.boomi.com/download/connector-doc-123",
        "genericConnectorRecordId": generic_connector_record_id,
    }
    mock_request.return_value = mock_response

    result = boomi_client.get_connector_document_url(generic_connector_record_id)

    assert "url" in result
    assert result["genericConnectorRecordId"] == generic_connector_record_id
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "POST"
    assert "ConnectorDocument" in kwargs["url"]
    assert kwargs["json"]["genericConnectorRecordId"] == generic_connector_record_id


# Download Helper Tests
@patch("requests.Session.get")
@patch("builtins.open", create=True)
def test_download_to_path_success(mock_open, mock_get, boomi_client):
    """Test that download_to_path successfully downloads content to file."""
    url = "https://api.boomi.com/download/file-123"
    output_path = "/tmp/test-download.txt"
    test_content = b"Test file content"

    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.status_code = 200
    mock_response.iter_content.return_value = [test_content]
    mock_get.return_value = mock_response

    mock_file = MagicMock()
    mock_open.return_value.__enter__.return_value = mock_file

    result = boomi_client.download_to_path(url, output_path)

    assert result == output_path
    mock_get.assert_called_once()
    args, kwargs = mock_get.call_args
    # URL is passed as positional argument
    assert args[0] == url
    assert kwargs["stream"] is True
    mock_file.write.assert_called_once_with(test_content)


@patch("pyboomi_platform.client.logger")
@patch("requests.Session.get")
@patch("time.sleep")
def test_download_to_path_logs_warning_on_429_retry(
    mock_sleep, mock_get, mock_logger, boomi_client
):
    """Test that logger.warning is called when download retries after 429 with Retry-After."""
    import os
    import tempfile

    # First response: 429 with Retry-After header
    rate_limit_response = MagicMock()
    rate_limit_response.status_code = 429
    rate_limit_response.ok = False
    rate_limit_response.headers = {"Retry-After": "2.5"}
    rate_limit_response.text = "Rate limit exceeded"
    rate_limit_response.json.side_effect = ValueError("Not JSON")

    # Second response: success
    success_response = MagicMock()
    success_response.status_code = 200
    success_response.ok = True
    success_response.headers = {"Content-Type": "application/octet-stream"}
    success_response.iter_content.return_value = [b"test data"]

    mock_get.side_effect = [rate_limit_response, success_response]

    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        output_path = tmp_file.name

    try:
        with patch("builtins.open", create=True) as mock_open:
            mock_file = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file

            result = boomi_client.download_to_path(
                "http://example.com/file.zip", output_path
            )

            assert result == output_path
            # Verify logger.warning was called
            mock_logger.warning.assert_called_once()
            warning_call = mock_logger.warning.call_args[0][0]
            assert "Download rate limit/status 429" in warning_call
            assert "Retrying in 2.50 seconds" in warning_call
            assert "Attempt 1/3" in warning_call
    finally:
        if os.path.exists(output_path):
            os.unlink(output_path)


@patch("pyboomi_platform.client.logger")
@patch("requests.Session.get")
@patch("time.sleep")
def test_download_to_path_logs_warning_on_request_exception_retry(
    mock_sleep, mock_get, mock_logger, boomi_client
):
    """Test that logger.warning is called when download retries after RequestException."""
    import os
    import tempfile

    # First call: RequestException
    request_exception = requests.exceptions.RequestException("Connection error")
    # Second call: success
    success_response = MagicMock()
    success_response.status_code = 200
    success_response.ok = True
    success_response.headers = {"Content-Type": "application/octet-stream"}
    success_response.iter_content.return_value = [b"test data"]

    mock_get.side_effect = [request_exception, success_response]

    with tempfile.NamedTemporaryFile(delete=False) as tmp_file:
        output_path = tmp_file.name

    try:
        with patch("builtins.open", create=True) as mock_open:
            mock_file = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file

            result = boomi_client.download_to_path(
                "http://example.com/file.zip", output_path
            )

            assert result == output_path
            # Verify logger.warning was called
            mock_logger.warning.assert_called_once()
            warning_call = mock_logger.warning.call_args[0][0]
            assert "Download error:" in warning_call
            assert "Retrying in 1.50 seconds" in warning_call
            assert "Attempt 1/3" in warning_call
    finally:
        if os.path.exists(output_path):
            os.unlink(output_path)


@patch("requests.Session.get")
@patch("time.sleep")
def test_download_to_path_handles_retry_after(mock_sleep, mock_get, boomi_client):
    """Test that download_to_path respects Retry-After header for retryable statuses."""
    url = "https://api.boomi.com/download/file-123"
    output_path = "/tmp/test-download.txt"

    # First response: 202 (in progress) with Retry-After
    in_progress_response = MagicMock()
    in_progress_response.status_code = 202
    in_progress_response.ok = False
    in_progress_response.headers = {"Retry-After": "1.0"}
    in_progress_response.text = "In progress"
    in_progress_response.json.side_effect = ValueError("Not JSON")

    # Second response: success
    success_response = MagicMock()
    success_response.ok = True
    success_response.status_code = 200
    success_response.iter_content.return_value = [b"content"]

    mock_get.side_effect = [in_progress_response, success_response]

    with patch("builtins.open", create=True) as mock_open:
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        result = boomi_client.download_to_path(url, output_path, retry_statuses=[202])

        assert result == output_path
        assert mock_get.call_count == 2
        # Verify sleep was called with Retry-After value
        mock_sleep.assert_called_once_with(1.0)


# Account API Tests
@patch("requests.Session.request")
def test_get_account(mock_request, boomi_client):
    """Test that get_account retrieves account information."""
    account_id = "account-123"
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"id": account_id, "name": "Test Account"}
    mock_request.return_value = mock_response

    result = boomi_client.get_account(account_id)

    assert result["id"] == account_id
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "GET"
    assert f"Account/{account_id}" in kwargs["url"]


@patch("requests.Session.request")
def test_get_account_uses_default_account_id(mock_request, boomi_client):
    """Test that get_account uses client's account_id when not provided."""
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"id": "account123", "name": "Test Account"}
    mock_request.return_value = mock_response

    result = boomi_client.get_account()

    assert result["id"] == "account123"
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert "Account/account123" in kwargs["url"]


@patch("requests.Session.request")
def test_get_account_bulk(mock_request, boomi_client):
    """Test that get_account_bulk retrieves multiple accounts."""
    account_ids = ["account-1", "account-2"]
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {
        "result": [{"id": "account-1"}, {"id": "account-2"}]
    }
    mock_request.return_value = mock_response

    result = boomi_client.get_account_bulk(account_ids)

    assert "result" in result
    assert len(result["result"]) == 2
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "POST"
    assert "Account/bulk" in kwargs["url"]
    assert kwargs["json"]["type"] == "GET"
    assert len(kwargs["json"]["request"]) == 2


@patch("requests.Session.request")
def test_query_account(mock_request, boomi_client):
    """Test that query_account queries for accounts."""
    filters = {"name": "TestAccount"}
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"result": [{"id": "account-1"}]}
    mock_request.return_value = mock_response

    result = boomi_client.query_account(filters)

    assert "result" in result
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "POST"
    assert "Account/query" in kwargs["url"]
    assert kwargs["json"] == filters


@patch("requests.Session.request")
def test_query_account_without_filters(mock_request, boomi_client):
    """Test that query_account works without filters."""
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"result": []}
    mock_request.return_value = mock_response

    result = boomi_client.query_account()

    assert "result" in result
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["json"] == {}


@patch("requests.Session.request")
def test_query_more_accounts(mock_request, boomi_client):
    """Test that query_more_accounts retrieves next page."""
    token = "next-token"
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"result": [{"id": "account-2"}]}
    mock_request.return_value = mock_response

    result = boomi_client.query_more_accounts(token)

    assert "result" in result
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "POST"
    assert "Account/queryMore" in kwargs["url"]
    assert kwargs["data"] == token
    assert kwargs["headers"]["Content-Type"] == "text/plain"


# Account Group API Tests
@patch("requests.Session.request")
def test_create_account_group(mock_request, boomi_client):
    """Test that create_account_group creates an account group."""
    name = "TestGroup"
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"id": "group-123", "name": name}
    mock_request.return_value = mock_response

    result = boomi_client.create_account_group(name)

    assert result["name"] == name
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "POST"
    assert "AccountGroup" in kwargs["url"]
    assert kwargs["json"]["name"] == name


@patch("requests.Session.request")
def test_create_account_group_with_resources(mock_request, boomi_client):
    """Test that create_account_group includes resources when provided."""
    name = "TestGroup"
    resources = [
        {
            "resourceId": "resource-1",
            "resourceName": "Resource1",
            "objectType": "Process",
        }
    ]
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"id": "group-123", "name": name}
    mock_request.return_value = mock_response

    result = boomi_client.create_account_group(name, resources=resources)

    assert result["name"] == name
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert "Resources" in kwargs["json"]
    assert kwargs["json"]["Resources"]["@type"] == "Resources"


@patch("requests.Session.request")
def test_get_account_group(mock_request, boomi_client):
    """Test that get_account_group retrieves an account group."""
    group_id = "group-123"
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"id": group_id, "name": "TestGroup"}
    mock_request.return_value = mock_response

    result = boomi_client.get_account_group(group_id)

    assert result["id"] == group_id
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "GET"
    assert f"AccountGroup/{group_id}" in kwargs["url"]


@patch("requests.Session.request")
def test_modify_account_group(mock_request, boomi_client):
    """Test that modify_account_group updates an account group."""
    group_id = "group-123"
    new_name = "UpdatedGroup"
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"id": group_id, "name": new_name}
    mock_request.return_value = mock_response

    result = boomi_client.modify_account_group(group_id, name=new_name)

    assert result["name"] == new_name
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "POST"
    assert f"AccountGroup/{group_id}" in kwargs["url"]
    assert kwargs["json"]["name"] == new_name


@patch("requests.Session.request")
def test_get_account_group_bulk(mock_request, boomi_client):
    """Test that get_account_group_bulk retrieves multiple account groups."""
    group_ids = ["group-1", "group-2"]
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"result": [{"id": "group-1"}, {"id": "group-2"}]}
    mock_request.return_value = mock_response

    result = boomi_client.get_account_group_bulk(group_ids)

    assert "result" in result
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "POST"
    assert "AccountGroup/bulk" in kwargs["url"]


@patch("requests.Session.request")
def test_query_account_group(mock_request, boomi_client):
    """Test that query_account_group queries for account groups."""
    filters = {"name": "TestGroup"}
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"result": [{"id": "group-1"}]}
    mock_request.return_value = mock_response

    result = boomi_client.query_account_group(filters)

    assert "result" in result
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "POST"
    assert "AccountGroup/query" in kwargs["url"]
    assert kwargs["json"] == filters


@patch("requests.Session.request")
def test_query_more_account_groups(mock_request, boomi_client):
    """Test that query_more_account_groups retrieves next page."""
    token = "next-token"
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"result": [{"id": "group-2"}]}
    mock_request.return_value = mock_response

    result = boomi_client.query_more_account_groups(token)

    assert "result" in result
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "POST"
    assert "AccountGroup/queryMore" in kwargs["url"]
    assert kwargs["data"] == token


# Client Initialization Edge Cases
@patch.dict("os.environ", {}, clear=True)
def test_client_init_with_config_object():
    """Test client initialization with pre-loaded config object."""
    from pyboomi_platform.config import Config

    config = Config()
    config.config_data = {
        "boomi": {
            "account_id": "config-account",
            "username": "config@example.com",
            "api_token": "config-token",
        }
    }

    client = BoomiPlatformClient(config=config)
    assert client.account_id == "config-account"
    assert client.username == "config@example.com"
    assert client.api_token == "config-token"


def test_client_init_base_url_with_account_id():
    """Test client initialization when base_url already includes account_id."""
    client = BoomiPlatformClient(
        account_id="account123",
        username="user@example.com",
        api_token="token",
        base_url="https://api.boomi.com/api/rest/v1/account123",
    )

    assert client.base_url == "https://api.boomi.com/api/rest/v1/account123"


def test_client_init_base_url_without_account_id():
    """Test client initialization when base_url doesn't include account_id."""
    client = BoomiPlatformClient(
        account_id="account123",
        username="user@example.com",
        api_token="token",
        base_url="https://api.boomi.com/api/rest/v1",
    )

    assert client.base_url == "https://api.boomi.com/api/rest/v1/account123"


def test_client_init_base_url_trailing_slash():
    """Test client initialization with base_url having trailing slash."""
    client = BoomiPlatformClient(
        account_id="account123",
        username="user@example.com",
        api_token="token",
        base_url="https://api.boomi.com/api/rest/v1/",
    )

    assert client.base_url == "https://api.boomi.com/api/rest/v1/account123"


# Error Handling Tests
@patch("requests.Session.request")
def test_request_handles_timeout(mock_request, boomi_client):
    """Test that _request handles timeout exceptions."""
    mock_request.side_effect = requests.exceptions.Timeout("Request timed out")

    with pytest.raises(Exception) as exc_info:
        boomi_client._request("GET", "TestEndpoint")

    assert "timeout" in str(exc_info.value).lower()


@patch("requests.Session.request")
def test_request_handles_connection_error(mock_request, boomi_client):
    """Test that _request handles connection errors."""
    mock_request.side_effect = requests.exceptions.ConnectionError("Connection failed")

    with pytest.raises(Exception) as exc_info:
        boomi_client._request("GET", "TestEndpoint")

    assert "connection error" in str(exc_info.value).lower()


@patch("requests.Session.request")
def test_request_handles_request_exception_with_retries(mock_request, boomi_client):
    """Test that _request retries on RequestException."""
    # First call fails, second succeeds
    mock_request.side_effect = [
        requests.exceptions.RequestException("Temporary error"),
        MagicMock(
            ok=True,
            headers={"Content-Type": "application/json"},
            json=lambda: {"result": "success"},
        ),
    ]

    with patch("time.sleep"):
        result = boomi_client._request("GET", "TestEndpoint", max_retries=1)

    assert result == {"result": "success"}
    assert mock_request.call_count == 2


@patch("requests.Session.request")
def test_request_handles_unexpected_exception(mock_request, boomi_client):
    """Test that _request handles unexpected exceptions."""
    mock_request.side_effect = ValueError("Unexpected error")

    with pytest.raises(Exception) as exc_info:
        boomi_client._request("GET", "TestEndpoint")

    assert "Unexpected error" in str(exc_info.value)


@patch("requests.Session.request")
def test_request_handles_non_json_error_response(mock_request, boomi_client):
    """Test that _request handles non-JSON error responses."""
    mock_response = MagicMock()
    mock_response.ok = False
    mock_response.status_code = 500
    mock_response.text = "Internal Server Error"
    mock_response.json.side_effect = ValueError("Not JSON")
    mock_request.return_value = mock_response

    with pytest.raises(Exception) as exc_info:
        boomi_client._request("GET", "TestEndpoint")

    assert "500" in str(exc_info.value)
    assert "Internal Server Error" in str(exc_info.value)


@patch("requests.Session.request")
def test_request_handles_xml_response(mock_request, boomi_client):
    """Test that _request handles XML responses correctly."""
    xml_content = "<Response><id>123</id></Response>"
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "text/xml"}
    mock_response.text = xml_content
    mock_request.return_value = mock_response

    result = boomi_client._request("GET", "TestEndpoint")

    assert result == xml_content


@patch("requests.Session.request")
def test_request_handles_unknown_content_type(mock_request, boomi_client):
    """Test that _request handles unknown content types."""
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/octet-stream"}
    mock_response.content = b"binary data"
    mock_response.text = "binary data"
    mock_request.return_value = mock_response

    result = boomi_client._request("GET", "TestEndpoint")

    assert "content" in result
    assert result["content"] == b"binary data"
    assert "headers" in result


# Account SSO Config Tests
@patch("requests.Session.request")
def test_get_account_sso_config(mock_request, boomi_client):
    """Test that get_account_sso_config retrieves SSO configuration."""
    account_id = "account-123"
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"accountId": account_id, "ssoEnabled": True}
    mock_request.return_value = mock_response

    result = boomi_client.get_account_sso_config(account_id)

    assert result["accountId"] == account_id
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "GET"
    assert f"AccountSSOConfig/{account_id}" in kwargs["url"]


@patch("requests.Session.request")
def test_modify_account_sso_config(mock_request, boomi_client):
    """Test that modify_account_sso_config updates SSO configuration."""
    account_id = "account-123"
    sso_config = {"ssoEnabled": True, "samlEndpoint": "https://example.com/saml"}
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"accountId": account_id, **sso_config}
    mock_request.return_value = mock_response

    result = boomi_client.modify_account_sso_config(account_id, sso_config)

    assert result["ssoEnabled"] is True
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "POST"
    assert f"AccountSSOConfig/{account_id}" in kwargs["url"]
    assert kwargs["json"] == sso_config


@patch("requests.Session.request")
def test_get_account_sso_config_bulk(mock_request, boomi_client):
    """Test that get_account_sso_config_bulk retrieves multiple SSO configs."""
    account_ids = ["account-1", "account-2"]
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"result": [{"accountId": "account-1"}]}
    mock_request.return_value = mock_response

    result = boomi_client.get_account_sso_config_bulk(account_ids)

    assert "result" in result
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "POST"
    assert "AccountSSOConfig/bulk" in kwargs["url"]


@patch("requests.Session.request")
def test_query_account_sso_config(mock_request, boomi_client):
    """Test that query_account_sso_config queries for SSO configs."""
    filters = {"ssoEnabled": True}
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"result": []}
    mock_request.return_value = mock_response

    result = boomi_client.query_account_sso_config(filters)

    assert "result" in result
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "POST"
    assert "AccountSSOConfig/query" in kwargs["url"]


@patch("requests.Session.request")
def test_query_more_account_sso_configs(mock_request, boomi_client):
    """Test that query_more_account_sso_configs retrieves next page."""
    token = "next-token"
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"result": []}
    mock_request.return_value = mock_response

    result = boomi_client.query_more_account_sso_configs(token)

    assert "result" in result
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["data"] == token
    assert kwargs["headers"]["Content-Type"] == "text/plain"


# Account User Federation Tests
@patch("requests.Session.request")
def test_create_account_user_federation(mock_request, boomi_client):
    """Test that create_account_user_federation creates a user federation."""
    federation_id = "federation-123"
    user_id = "user-123"
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {
        "federationId": federation_id,
        "userId": user_id,
    }
    mock_request.return_value = mock_response

    result = boomi_client.create_account_user_federation(federation_id, user_id)

    assert result["federationId"] == federation_id
    assert result["userId"] == user_id
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "POST"
    assert "AccountUserFederation" in kwargs["url"]


@patch("requests.Session.request")
def test_query_account_user_federation(mock_request, boomi_client):
    """Test that query_account_user_federation queries for user federations."""
    filters = {"userId": "user-123"}
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"result": []}
    mock_request.return_value = mock_response

    result = boomi_client.query_account_user_federation(filters)

    assert "result" in result
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "POST"
    assert "AccountUserFederation/query" in kwargs["url"]


@patch("requests.Session.request")
def test_query_more_account_user_federations(mock_request, boomi_client):
    """Test that query_more_account_user_federations retrieves next page."""
    token = "next-token"
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"result": []}
    mock_request.return_value = mock_response

    result = boomi_client.query_more_account_user_federations(token)

    assert "result" in result
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["data"] == token


@patch("requests.Session.request")
def test_modify_account_user_federation(mock_request, boomi_client):
    """Test that modify_account_user_federation updates a user federation."""
    id = "federation-user-account-id"
    federation_id = "federation-123"
    user_id = "user-123"
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {
        "id": id,
        "federationId": federation_id,
        "userId": user_id,
    }
    mock_request.return_value = mock_response

    result = boomi_client.modify_account_user_federation(id, federation_id, user_id)

    assert result["id"] == id
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "POST"
    assert f"AccountUserFederation/{id}" in kwargs["url"]
    assert kwargs["json"]["federationId"] == federation_id
    assert kwargs["json"]["userId"] == user_id


@patch("requests.Session.request")
def test_delete_account_user_federation(mock_request, boomi_client):
    """Test that delete_account_user_federation deletes a user federation."""
    id = "federation-user-account-id"
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"id": id, "status": "deleted"}
    mock_request.return_value = mock_response

    result = boomi_client.delete_account_user_federation(id)

    assert result["id"] == id
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "DELETE"
    assert f"AccountUserFederation/{id}" in kwargs["url"]


# Account User Role Tests
@patch("requests.Session.request")
def test_create_account_user_role(mock_request, boomi_client):
    """Test that create_account_user_role creates a user role."""
    first_name = "John"
    last_name = "Doe"
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {
        "id": "role-123",
        "firstName": first_name,
        "lastName": last_name,
    }
    mock_request.return_value = mock_response

    result = boomi_client.create_account_user_role(first_name, last_name)

    assert result["firstName"] == first_name
    assert result["lastName"] == last_name
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "POST"
    assert "AccountUserRole" in kwargs["url"]
    assert kwargs["json"]["firstName"] == first_name
    assert kwargs["json"]["lastName"] == last_name
    assert kwargs["json"]["notifyUser"] is False


@patch("requests.Session.request")
def test_create_account_user_role_with_notify(mock_request, boomi_client):
    """Test that create_account_user_role can notify user."""
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"id": "role-123"}
    mock_request.return_value = mock_response

    result = boomi_client.create_account_user_role(
        "John", "Doe", notifyUser=True, roleId="role-123", userId="user-123"
    )

    assert result["id"] == "role-123"
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["json"]["notifyUser"] is True
    assert kwargs["json"]["roleId"] == "role-123"
    assert kwargs["json"]["userId"] == "user-123"


@patch("requests.Session.request")
def test_query_account_user_role(mock_request, boomi_client):
    """Test that query_account_user_role queries for user roles."""
    filters = {"userId": "user-123"}
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"result": []}
    mock_request.return_value = mock_response

    result = boomi_client.query_account_user_role(filters)

    assert "result" in result
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "POST"
    assert "AccountUserRole/query" in kwargs["url"]


@patch("requests.Session.request")
def test_query_more_account_user_roles(mock_request, boomi_client):
    """Test that query_more_account_user_roles retrieves next page."""
    token = "next-token"
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"result": []}
    mock_request.return_value = mock_response

    result = boomi_client.query_more_account_user_roles(token)

    assert "result" in result
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["data"] == token


@patch("requests.Session.request")
def test_delete_account_user_role(mock_request, boomi_client):
    """Test that delete_account_user_role deletes a user role."""
    id = "role-123"
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"id": id, "status": "deleted"}
    mock_request.return_value = mock_response

    result = boomi_client.delete_account_user_role(id)

    assert result["id"] == id
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "DELETE"
    assert f"AccountUserRole/{id}" in kwargs["url"]


# API Usage Count Tests
@patch("requests.Session.request")
def test_query_api_usage_count(mock_request, boomi_client):
    """Test that query_api_usage_count queries for API usage counts."""
    filters = {"accountId": "account-123"}
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"result": []}
    mock_request.return_value = mock_response

    result = boomi_client.query_api_usage_count(filters)

    assert "result" in result
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "POST"
    assert "ApiUsageCount/query" in kwargs["url"]


@patch("requests.Session.request")
def test_query_more_api_usage_counts(mock_request, boomi_client):
    """Test that query_more_api_usage_counts retrieves next page."""
    token = "next-token"
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"result": []}
    mock_request.return_value = mock_response

    result = boomi_client.query_more_api_usage_counts(token)

    assert "result" in result
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["data"] == token


# Audit Log Tests
@patch("requests.Session.request")
def test_get_audit_log(mock_request, boomi_client):
    """Test that get_audit_log retrieves an audit log."""
    audit_log_id = "audit-123"
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"id": audit_log_id, "action": "CREATE"}
    mock_request.return_value = mock_response

    result = boomi_client.get_audit_log(audit_log_id)

    assert result["id"] == audit_log_id
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "GET"
    assert f"AuditLog/{audit_log_id}" in kwargs["url"]


@patch("requests.Session.request")
def test_get_audit_log_bulk(mock_request, boomi_client):
    """Test that get_audit_log_bulk retrieves multiple audit logs."""
    audit_log_ids = ["audit-1", "audit-2"]
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"result": [{"id": "audit-1"}, {"id": "audit-2"}]}
    mock_request.return_value = mock_response

    result = boomi_client.get_audit_log_bulk(audit_log_ids)

    assert "result" in result
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "POST"
    assert "AuditLog/bulk" in kwargs["url"]


@patch("requests.Session.request")
def test_query_audit_log(mock_request, boomi_client):
    """Test that query_audit_log queries for audit logs."""
    filters = {"action": "CREATE"}
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"result": []}
    mock_request.return_value = mock_response

    result = boomi_client.query_audit_log(filters)

    assert "result" in result
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "POST"
    assert "AuditLog/query" in kwargs["url"]


@patch("requests.Session.request")
def test_query_more_audit_logs(mock_request, boomi_client):
    """Test that query_more_audit_logs retrieves next page."""
    token = "next-token"
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"result": []}
    mock_request.return_value = mock_response

    result = boomi_client.query_more_audit_logs(token)

    assert "result" in result
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["data"] == token


# Connection Licensing Report Tests
@patch("requests.Session.request")
def test_create_connection_licensing_report(mock_request, boomi_client):
    """Test that create_connection_licensing_report creates a report request."""
    filters = {"environmentId": "env-123"}
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {
        "@type": "ConnectionLicensingDownload",
        "url": "https://api.boomi.com/download/report-123",
        "statusCode": 202,
    }
    mock_request.return_value = mock_response

    result = boomi_client.create_connection_licensing_report(filters)

    assert "url" in result
    assert result["@type"] == "ConnectionLicensingDownload"
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "POST"
    assert "ConnectionLicensingReport" in kwargs["url"]
    assert kwargs["json"] == filters


@patch("requests.Session.request")
def test_create_connection_licensing_report_without_filters(mock_request, boomi_client):
    """Test that create_connection_licensing_report works without filters."""
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {
        "@type": "ConnectionLicensingDownload",
        "url": "https://api.boomi.com/download/report-123",
    }
    mock_request.return_value = mock_response

    result = boomi_client.create_connection_licensing_report()

    assert "url" in result
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["json"] == {}


@patch("requests.Session.request")
def test_get_connection_licensing_report_200(mock_request, boomi_client):
    """Test that get_connection_licensing_report handles 200 response."""
    url = "https://api.boomi.com/download/report-123"
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"status": "complete", "data": "report data"}
    mock_response.text = '{"status": "complete"}'
    mock_response.content = b"report data"
    mock_request.return_value = mock_response

    result = boomi_client.get_connection_licensing_report(url)

    assert result["status_code"] == 200
    assert result["status"] == "complete"
    assert "data" in result
    mock_request.assert_called_once()


@patch("requests.Session.request")
def test_get_connection_licensing_report_202(mock_request, boomi_client):
    """Test that get_connection_licensing_report handles 202 response."""
    url = "https://api.boomi.com/download/report-123"
    mock_response = MagicMock()
    mock_response.status_code = 202
    mock_response.headers = {}
    mock_response.text = ""
    mock_response.content = None
    mock_request.return_value = mock_response

    result = boomi_client.get_connection_licensing_report(url)

    assert result["status_code"] == 202
    assert result["status"] == "in_progress"
    assert result["content"] is None


@patch("requests.Session.request")
def test_get_connection_licensing_report_204(mock_request, boomi_client):
    """Test that get_connection_licensing_report handles 204 response."""
    url = "https://api.boomi.com/download/report-123"
    mock_response = MagicMock()
    mock_response.status_code = 204
    mock_response.headers = {}
    mock_response.text = ""
    mock_response.content = None
    mock_request.return_value = mock_response

    result = boomi_client.get_connection_licensing_report(url)

    assert result["status_code"] == 204
    assert result["status"] == "no_content"


@patch("requests.Session.request")
def test_get_connection_licensing_report_404(mock_request, boomi_client):
    """Test that get_connection_licensing_report handles 404 response."""
    url = "https://api.boomi.com/download/report-123"
    mock_response = MagicMock()
    mock_response.status_code = 404
    mock_response.headers = {}
    mock_response.text = ""
    mock_response.content = None
    mock_request.return_value = mock_response

    result = boomi_client.get_connection_licensing_report(url)

    assert result["status_code"] == 404
    assert result["status"] == "not_found"


@patch("requests.Session.request")
def test_get_connection_licensing_report_504(mock_request, boomi_client):
    """Test that get_connection_licensing_report handles 504 response."""
    url = "https://api.boomi.com/download/report-123"
    mock_response = MagicMock()
    mock_response.status_code = 504
    mock_response.headers = {}
    mock_response.text = ""
    mock_response.content = None
    mock_request.return_value = mock_response

    result = boomi_client.get_connection_licensing_report(url)

    assert result["status_code"] == 504
    assert result["status"] == "timeout"


@patch("requests.Session.request")
@patch("time.sleep")
def test_download_connection_licensing_report(mock_sleep, mock_request, boomi_client):
    """Test that download_connection_licensing_report manages the download process."""
    # First call: create report
    create_response = MagicMock()
    create_response.ok = True
    create_response.headers = {"Content-Type": "application/json"}
    create_response.json.return_value = {
        "@type": "ConnectionLicensingDownload",
        "url": "https://api.boomi.com/download/report-123",
    }

    # Second call: get report (202 in progress)
    in_progress_response = MagicMock()
    in_progress_response.status_code = 202
    in_progress_response.headers = {}
    in_progress_response.text = ""
    in_progress_response.content = None

    # Third call: get report (200 complete)
    complete_response = MagicMock()
    complete_response.status_code = 200
    complete_response.headers = {"Content-Type": "application/json"}
    complete_response.json.return_value = {"status": "complete", "data": "report"}
    complete_response.text = '{"status": "complete"}'
    complete_response.content = b"report data"

    mock_request.side_effect = [
        create_response,
        in_progress_response,
        complete_response,
    ]

    result = boomi_client.download_connection_licensing_report(
        delay=0.1, max_attempts=5
    )

    assert result["status_code"] == 200
    assert result["status"] == "complete"
    assert mock_request.call_count == 3


# Role API Tests
@patch("requests.Session.request")
def test_get_assignable_roles(mock_request, boomi_client):
    """Test that get_assignable_roles retrieves assignable roles."""
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"result": [{"name": "Admin"}, {"name": "User"}]}
    mock_request.return_value = mock_response

    result = boomi_client.get_assignable_roles()

    assert "result" in result
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "GET"
    assert "AssignableRole" in kwargs["url"]


@patch("requests.Session.request")
def test_create_role(mock_request, boomi_client):
    """Test that create_role creates a role."""
    name = "TestRole"
    privileges = ["READ", "WRITE"]
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"id": "role-123", "name": name}
    mock_request.return_value = mock_response

    result = boomi_client.create_role(name, privileges)

    assert result["name"] == name
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "POST"
    assert "Role" in kwargs["url"]
    assert kwargs["json"]["name"] == name
    assert "Privileges" in kwargs["json"]


@patch("requests.Session.request")
def test_create_role_with_description(mock_request, boomi_client):
    """Test that create_role includes description when provided."""
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"id": "role-123"}
    mock_request.return_value = mock_response

    result = boomi_client.create_role(
        "TestRole", ["READ"], description="Test description", parent_id="parent-123"
    )

    assert result["id"] == "role-123"
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["json"]["Description"] == "Test description"
    assert kwargs["json"]["parentId"] == "parent-123"


@patch("requests.Session.request")
def test_get_role(mock_request, boomi_client):
    """Test that get_role retrieves a role."""
    role_id = "role-123"
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"id": role_id, "name": "TestRole"}
    mock_request.return_value = mock_response

    result = boomi_client.get_role(role_id)

    assert result["id"] == role_id
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "GET"
    assert f"Role/{role_id}" in kwargs["url"]


@patch("requests.Session.request")
def test_modify_role(mock_request, boomi_client):
    """Test that modify_role updates a role."""
    role_id = "role-123"
    new_name = "UpdatedRole"
    new_privileges = ["READ", "WRITE", "DELETE"]
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"id": role_id, "name": new_name}
    mock_request.return_value = mock_response

    result = boomi_client.modify_role(role_id, name=new_name, privileges=new_privileges)

    assert result["name"] == new_name
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "POST"
    assert f"Role/{role_id}" in kwargs["url"]
    assert kwargs["json"]["name"] == new_name
    assert "Privileges" in kwargs["json"]


@patch("requests.Session.request")
def test_delete_role(mock_request, boomi_client):
    """Test that delete_role deletes a role."""
    role_id = "role-123"
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"id": role_id, "status": "deleted"}
    mock_request.return_value = mock_response

    result = boomi_client.delete_role(role_id)

    assert result["id"] == role_id
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "DELETE"
    assert f"Role/{role_id}" in kwargs["url"]


@patch("requests.Session.request")
def test_query_role(mock_request, boomi_client):
    """Test that query_role queries for roles."""
    filters = {"name": "TestRole"}
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"result": [{"id": "role-123"}]}
    mock_request.return_value = mock_response

    result = boomi_client.query_role(filters)

    assert "result" in result
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "POST"
    assert "Role/query" in kwargs["url"]


@patch("requests.Session.request")
def test_query_more_roles(mock_request, boomi_client):
    """Test that query_more_roles retrieves next page."""
    token = "next-token"
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"result": []}
    mock_request.return_value = mock_response

    result = boomi_client.query_more_roles(token)

    assert "result" in result
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["data"] == token


@patch("requests.Session.request")
def test_get_role_bulk(mock_request, boomi_client):
    """Test that get_role_bulk retrieves multiple roles."""
    role_ids = ["role-1", "role-2"]
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"result": [{"id": "role-1"}, {"id": "role-2"}]}
    mock_request.return_value = mock_response

    result = boomi_client.get_role_bulk(role_ids)

    assert "result" in result
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "POST"
    assert "Role/bulk" in kwargs["url"]


# Environment API Tests
@patch("requests.Session.request")
def test_get_environment(mock_request, boomi_client):
    """Test that get_environment retrieves an environment."""
    environment_id = "env-123"
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"id": environment_id, "name": "TestEnv"}
    mock_request.return_value = mock_response

    result = boomi_client.get_environment(environment_id)

    assert result["id"] == environment_id
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "GET"
    assert f"Environment/{environment_id}" in kwargs["url"]


@patch("requests.Session.request")
def test_get_environment_bulk(mock_request, boomi_client):
    """Test that get_environment_bulk retrieves multiple environments."""
    environment_ids = ["env-1", "env-2"]
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"result": [{"id": "env-1"}, {"id": "env-2"}]}
    mock_request.return_value = mock_response

    result = boomi_client.get_environment_bulk(environment_ids)

    assert "result" in result
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "POST"
    assert "Environment/bulk" in kwargs["url"]


@patch("requests.Session.request")
def test_query_environments(mock_request, boomi_client):
    """Test that query_environments queries for environments."""
    filters = {"name": "TestEnv"}
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"result": [{"id": "env-123"}]}
    mock_request.return_value = mock_response

    result = boomi_client.query_environments(filters)

    assert "result" in result
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "POST"
    assert "Environment/query" in kwargs["url"]


@patch("requests.Session.request")
def test_query_more_environments(mock_request, boomi_client):
    """Test that query_more_environments retrieves next page."""
    token = "next-token"
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"result": []}
    mock_request.return_value = mock_response

    result = boomi_client.query_more_environments(token)

    assert "result" in result
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["data"] == token


@patch("requests.Session.request")
def test_create_environment(mock_request, boomi_client):
    """Test that create_environment creates an environment."""
    name = "TestEnv"
    classification = "PRODUCTION"
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"id": "env-123", "name": name}
    mock_request.return_value = mock_response

    result = boomi_client.create_environment(name, classification=classification)

    assert result["name"] == name
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "POST"
    assert "Environment" in kwargs["url"]
    assert kwargs["json"]["name"] == name
    assert kwargs["json"]["classification"] == classification


@patch("requests.Session.request")
def test_create_environment_without_classification(mock_request, boomi_client):
    """Test that create_environment works without classification."""
    name = "TestEnv"
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"id": "env-123", "name": name}
    mock_request.return_value = mock_response

    result = boomi_client.create_environment(name)

    assert result["name"] == name
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["json"]["classification"] is None


# Packaged Component Tests
@patch("requests.Session.request")
def test_create_packaged_component(mock_request, boomi_client):
    """Test that create_packaged_component creates a packaged component."""
    component_id = "component-123"
    package_version = "1.0.0"
    notes = "Test package"
    branch_name = "main"
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"id": "package-123", "componentId": component_id}
    mock_request.return_value = mock_response

    result = boomi_client.create_packaged_component(
        component_id,
        package_version=package_version,
        notes=notes,
        branch_name=branch_name,
    )

    assert result["componentId"] == component_id
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "POST"
    assert "PackagedComponent" in kwargs["url"]
    assert kwargs["json"]["componentId"] == component_id
    assert kwargs["json"]["packageVersion"] == package_version
    assert kwargs["json"]["notes"] == notes
    assert kwargs["json"]["branchName"] == branch_name


@patch("requests.Session.request")
def test_get_packaged_component(mock_request, boomi_client):
    """Test that get_packaged_component retrieves a packaged component."""
    package_id = "package-123"
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"id": package_id, "version": "1.0.0"}
    mock_request.return_value = mock_response

    result = boomi_client.get_packaged_component(package_id)

    assert result["id"] == package_id
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "GET"
    assert f"PackagedComponent/{package_id}" in kwargs["url"]


@patch("requests.Session.request")
def test_query_packaged_components(mock_request, boomi_client):
    """Test that query_packaged_components queries for packaged components."""
    filters = {"componentId": "component-123"}
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"result": [{"id": "package-123"}]}
    mock_request.return_value = mock_response

    result = boomi_client.query_packaged_components(filters)

    assert "result" in result
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "POST"
    assert "PackagedComponent/query" in kwargs["url"]


@patch("requests.Session.request")
def test_query_more_packaged_components(mock_request, boomi_client):
    """Test that query_more_packaged_components retrieves next page."""
    token = "next-token"
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"result": []}
    mock_request.return_value = mock_response

    result = boomi_client.query_more_packaged_components(token)

    assert "result" in result
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["data"] == token


# Deployed Package Tests
@patch("requests.Session.request")
def test_create_deployed_package(mock_request, boomi_client):
    """Test that create_deployed_package creates a deployed package."""
    package_id = "package-123"
    environment_id = "env-123"
    listener_status = "STARTED"
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {
        "id": "deployed-123",
        "packageId": package_id,
        "environmentId": environment_id,
    }
    mock_request.return_value = mock_response

    result = boomi_client.create_deployed_package(
        package_id, environment_id, listener_status=listener_status
    )

    assert result["packageId"] == package_id
    assert result["environmentId"] == environment_id
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "POST"
    assert "DeployedPackage" in kwargs["url"]
    assert kwargs["json"]["packageId"] == package_id
    assert kwargs["json"]["environmentId"] == environment_id
    assert kwargs["json"]["listenerStatus"] == listener_status


@patch("requests.Session.request")
def test_get_deployed_package(mock_request, boomi_client):
    """Test that get_deployed_package retrieves a deployed package."""
    deployed_package_id = "deployed-123"
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"id": deployed_package_id, "status": "DEPLOYED"}
    mock_request.return_value = mock_response

    result = boomi_client.get_deployed_package(deployed_package_id)

    assert result["id"] == deployed_package_id
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "GET"
    assert f"DeployedPackage/{deployed_package_id}" in kwargs["url"]


@patch("requests.Session.request")
def test_query_deployed_packages(mock_request, boomi_client):
    """Test that query_deployed_packages queries for deployed packages."""
    filters = {"environmentId": "env-123"}
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"result": [{"id": "deployed-123"}]}
    mock_request.return_value = mock_response

    result = boomi_client.query_deployed_packages(filters)

    assert "result" in result
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "POST"
    assert "DeployedPackage/query" in kwargs["url"]


@patch("requests.Session.request")
def test_query_more_deployed_packages(mock_request, boomi_client):
    """Test that query_more_deployed_packages retrieves next page."""
    token = "next-token"
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"result": []}
    mock_request.return_value = mock_response

    result = boomi_client.query_more_deployed_packages(token)

    assert "result" in result
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["data"] == token


# Component Metadata Tests
@patch("requests.Session.request")
def test_query_component_metadata(mock_request, boomi_client):
    """Test that query_component_metadata queries for component metadata."""
    filters = {"type": "process"}
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {
        "result": [{"id": "comp-123", "type": "process"}]
    }
    mock_request.return_value = mock_response

    result = boomi_client.query_component_metadata(filters)

    assert "result" in result
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "POST"
    assert "ComponentMetadata/query" in kwargs["url"]
    assert kwargs["json"] == filters


@patch("requests.Session.request")
def test_query_component_metadata_without_filters(mock_request, boomi_client):
    """Test that query_component_metadata works without filters."""
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"result": []}
    mock_request.return_value = mock_response

    result = boomi_client.query_component_metadata()

    assert "result" in result
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["json"] is None


@patch("requests.Session.request")
def test_query_more_component_metadata(mock_request, boomi_client):
    """Test that query_more_component_metadata retrieves next page."""
    token = "next-token"
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"result": []}
    mock_request.return_value = mock_response

    result = boomi_client.query_more_component_metadata(token)

    assert "result" in result
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "POST"
    assert "ComponentMetadata/queryMore" in kwargs["url"]
    assert kwargs["data"] == token
    assert kwargs["headers"]["Content-Type"] == "text/plain"


@patch("requests.Session.request")
def test_get_component_metadata(mock_request, boomi_client):
    """Test that get_component_metadata retrieves component metadata."""
    component_id = "component-123"
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"id": component_id, "type": "process"}
    mock_request.return_value = mock_response

    result = boomi_client.get_component_metadata(component_id)

    assert result["id"] == component_id
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "GET"
    assert f"ComponentMetadata/{component_id}" in kwargs["url"]


@patch("requests.Session.request")
def test_get_component_metadata_with_branch(mock_request, boomi_client):
    """Test that get_component_metadata includes branch ID when provided."""
    component_id = "component-123"
    branch_id = "branch-123"
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"id": component_id, "branchId": branch_id}
    mock_request.return_value = mock_response

    result = boomi_client.get_component_metadata(component_id, branch_id=branch_id)

    assert result["id"] == component_id
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert f"ComponentMetadata/{component_id}~{branch_id}" in kwargs["url"]


# Custom Tracked Fields Tests
@patch("requests.Session.request")
def test_query_custom_tracked_fields(mock_request, boomi_client):
    """Test that query_custom_tracked_fields queries for custom tracked fields."""
    filters = {"name": "CustomField"}
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"result": []}
    mock_request.return_value = mock_response

    result = boomi_client.query_custom_tracked_fields(filters)

    assert "result" in result
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "POST"
    assert "CustomTrackedField/query" in kwargs["url"]


@patch("requests.Session.request")
def test_query_more_custom_tracked_fields(mock_request, boomi_client):
    """Test that query_more_custom_tracked_fields retrieves next page."""
    token = "next-token"
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"result": []}
    mock_request.return_value = mock_response

    result = boomi_client.query_more_custom_tracked_fields(token)

    assert "result" in result
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["data"] == token


# Event Tests
@patch("requests.Session.request")
def test_query_event(mock_request, boomi_client):
    """Test that query_event queries for events."""
    filters = {"type": "EXECUTION"}
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"result": []}
    mock_request.return_value = mock_response

    result = boomi_client.query_event(filters)

    assert "result" in result
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "POST"
    assert "Event/query" in kwargs["url"]


@patch("requests.Session.request")
def test_query_more_events(mock_request, boomi_client):
    """Test that query_more_events retrieves next page."""
    token = "next-token"
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"result": []}
    mock_request.return_value = mock_response

    result = boomi_client.query_more_events(token)

    assert "result" in result
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["data"] == token


# Additional Error Handling Tests
@patch("requests.Session.request")
def test_request_handles_error_with_message_in_dict(mock_request, boomi_client):
    """Test that _request extracts message from error dict correctly."""
    mock_response = MagicMock()
    mock_response.ok = False
    mock_response.status_code = 400
    mock_response.json.return_value = {"message": "Bad request error"}
    mock_response.text = '{"message": "Bad request error"}'
    mock_request.return_value = mock_response

    with pytest.raises(Exception) as exc_info:
        boomi_client._request("GET", "TestEndpoint")

    assert "400" in str(exc_info.value)
    assert "Bad request error" in str(exc_info.value)


@patch("requests.Session.request")
def test_request_handles_error_with_non_dict_json(mock_request, boomi_client):
    """Test that _request handles non-dict JSON error responses."""
    mock_response = MagicMock()
    mock_response.ok = False
    mock_response.status_code = 400
    mock_response.json.return_value = "Error string"
    mock_response.text = '"Error string"'
    mock_request.return_value = mock_response

    with pytest.raises(Exception) as exc_info:
        boomi_client._request("GET", "TestEndpoint")

    assert "400" in str(exc_info.value)
    assert "Error string" in str(exc_info.value)


@patch("requests.Session.request")
def test_request_handles_rate_limit_error_with_message(mock_request, boomi_client):
    """Test that _request extracts message from rate limit error dict."""
    mock_response = MagicMock()
    mock_response.status_code = 429
    mock_response.ok = False
    mock_response.headers = {}
    mock_response.json.return_value = {"message": "Rate limit exceeded"}
    mock_response.text = '{"message": "Rate limit exceeded"}'
    mock_request.return_value = mock_response

    with pytest.raises(Exception) as exc_info:
        boomi_client._request("GET", "TestEndpoint", max_retries=0)

    assert "429" in str(exc_info.value)
    assert "Rate limit exceeded" in str(exc_info.value)


@patch("requests.Session.request")
def test_request_handles_rate_limit_error_with_non_dict_json(
    mock_request, boomi_client
):
    """Test that _request handles non-dict JSON in rate limit error."""
    mock_response = MagicMock()
    mock_response.status_code = 429
    mock_response.ok = False
    mock_response.headers = {}
    mock_response.json.return_value = "Rate limit"
    mock_response.text = '"Rate limit"'
    mock_request.return_value = mock_response

    with pytest.raises(Exception) as exc_info:
        boomi_client._request("GET", "TestEndpoint", max_retries=0)

    assert "429" in str(exc_info.value)
    assert "Rate limit" in str(exc_info.value)


@patch("requests.Session.request")
def test_download_connection_licensing_report_max_attempts_exceeded(
    mock_request, boomi_client
):
    """Test that download_connection_licensing_report raises error when max_attempts exceeded."""
    create_response = MagicMock()
    create_response.ok = True
    create_response.headers = {"Content-Type": "application/json"}
    create_response.json.return_value = {
        "@type": "ConnectionLicensingDownload",
        "url": "https://api.boomi.com/download/report-123",
    }

    in_progress_response = MagicMock()
    in_progress_response.status_code = 202
    in_progress_response.headers = {}
    in_progress_response.text = ""
    in_progress_response.content = None

    mock_request.side_effect = [
        create_response,
        in_progress_response,
        in_progress_response,
    ]

    with patch("time.sleep"):
        with pytest.raises(Exception) as exc_info:
            boomi_client.download_connection_licensing_report(delay=0.1, max_attempts=2)

    assert "Maximum polling attempts" in str(exc_info.value)
    assert "2" in str(exc_info.value)


@patch("requests.Session.request")
def test_download_connection_licensing_report_missing_url(mock_request, boomi_client):
    """Test that download_connection_licensing_report raises error when URL is missing."""
    create_response = MagicMock()
    create_response.ok = True
    create_response.headers = {"Content-Type": "application/json"}
    create_response.json.return_value = {"@type": "ConnectionLicensingDownload"}
    mock_request.return_value = create_response

    with pytest.raises(Exception) as exc_info:
        boomi_client.download_connection_licensing_report()

    assert "missing 'url' field" in str(exc_info.value)


@patch("requests.Session.request")
def test_download_connection_licensing_report_unexpected_status(
    mock_request, boomi_client
):
    """Test that download_connection_licensing_report handles unexpected status codes."""
    create_response = MagicMock()
    create_response.ok = True
    create_response.headers = {"Content-Type": "application/json"}
    create_response.json.return_value = {
        "@type": "ConnectionLicensingDownload",
        "url": "https://api.boomi.com/download/report-123",
    }

    unexpected_response = MagicMock()
    unexpected_response.status_code = 500
    unexpected_response.headers = {}
    unexpected_response.text = "Server error"
    unexpected_response.content = None

    mock_request.side_effect = [create_response, unexpected_response]

    with patch("time.sleep"):
        with pytest.raises(Exception) as exc_info:
            boomi_client.download_connection_licensing_report(delay=0.1, max_attempts=1)

    assert "Unexpected status code" in str(exc_info.value)
    assert "500" in str(exc_info.value)


# Additional Download Helper Tests
@patch("requests.Session.get")
@patch("time.sleep")
def test_download_url_with_retries_max_retries_exceeded(
    mock_sleep, mock_get, boomi_client
):
    """Test that _download_url_with_retries raises error after max retries."""
    url = "https://api.boomi.com/download/file-123"
    output_path = "/tmp/test-download.txt"

    retry_response = MagicMock()
    retry_response.status_code = 202
    retry_response.ok = False
    retry_response.headers = {"Retry-After": "1.0"}
    retry_response.text = "In progress"
    retry_response.json.side_effect = ValueError("Not JSON")

    mock_get.return_value = retry_response

    with patch("builtins.open", create=True):
        with pytest.raises(Exception) as exc_info:
            boomi_client._download_url_with_retries(
                url, output_path, max_retries=1, retry_statuses=[202]
            )

        assert "max retries exceeded" in str(exc_info.value).lower()
        assert mock_get.call_count == 2  # Initial + 1 retry


@patch("requests.Session.get")
def test_download_url_with_retries_non_ok_response(mock_get, boomi_client):
    """Test that _download_url_with_retries handles non-ok responses."""
    url = "https://api.boomi.com/download/file-123"
    output_path = "/tmp/test-download.txt"

    error_response = MagicMock()
    error_response.ok = False
    error_response.status_code = 500
    error_response.text = "Server error"
    error_response.json.side_effect = ValueError("Not JSON")

    mock_get.return_value = error_response

    with patch("builtins.open", create=True):
        with pytest.raises(Exception) as exc_info:
            boomi_client._download_url_with_retries(url, output_path)

        assert "500" in str(exc_info.value)


@patch("requests.Session.get")
@patch("time.sleep")
def test_download_url_with_retries_request_exception(
    mock_sleep, mock_get, boomi_client
):
    """Test that _download_url_with_retries retries on RequestException."""
    url = "https://api.boomi.com/download/file-123"
    output_path = "/tmp/test-download.txt"

    # First call fails, second succeeds
    mock_get.side_effect = [
        requests.exceptions.RequestException("Temporary error"),
        MagicMock(
            ok=True,
            status_code=200,
            iter_content=lambda chunk_size: [b"content"],
        ),
    ]

    with patch("builtins.open", create=True) as mock_open:
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        result = boomi_client._download_url_with_retries(
            url, output_path, max_retries=1
        )

        assert result == output_path
        assert mock_get.call_count == 2


@patch("requests.Session.get")
def test_download_url_with_retries_timeout(mock_get, boomi_client):
    """Test that _download_url_with_retries handles timeout."""
    url = "https://api.boomi.com/download/file-123"
    output_path = "/tmp/test-download.txt"

    mock_get.side_effect = requests.exceptions.Timeout("Request timed out")

    with patch("builtins.open", create=True):
        with pytest.raises(Exception) as exc_info:
            boomi_client._download_url_with_retries(url, output_path)

        assert "timeout" in str(exc_info.value).lower()


@patch("requests.Session.get")
def test_download_url_with_retries_connection_error(mock_get, boomi_client):
    """Test that _download_url_with_retries handles connection errors."""
    url = "https://api.boomi.com/download/file-123"
    output_path = "/tmp/test-download.txt"

    mock_get.side_effect = requests.exceptions.ConnectionError("Connection failed")

    with patch("builtins.open", create=True):
        with pytest.raises(Exception) as exc_info:
            boomi_client._download_url_with_retries(url, output_path)

        assert "connection error" in str(exc_info.value).lower()


@patch("requests.Session.get")
def test_download_url_with_retries_unexpected_exception(mock_get, boomi_client):
    """Test that _download_url_with_retries handles unexpected exceptions."""
    url = "https://api.boomi.com/download/file-123"
    output_path = "/tmp/test-download.txt"

    mock_get.side_effect = ValueError("Unexpected error")

    with patch("builtins.open", create=True):
        with pytest.raises(Exception) as exc_info:
            boomi_client._download_url_with_retries(url, output_path)

        assert "Unexpected download error" in str(exc_info.value)


@patch("requests.Session.get")
@patch("time.sleep")
def test_download_url_with_retries_max_retries_request_exception(
    mock_sleep, mock_get, boomi_client
):
    """Test that _download_url_with_retries raises error after max retries for RequestException."""
    url = "https://api.boomi.com/download/file-123"
    output_path = "/tmp/test-download.txt"

    mock_get.side_effect = requests.exceptions.RequestException("Temporary error")

    with patch("builtins.open", create=True):
        with pytest.raises(Exception) as exc_info:
            boomi_client._download_url_with_retries(url, output_path, max_retries=1)

        assert "failed after" in str(exc_info.value).lower()
        assert mock_get.call_count == 2  # Initial + 1 retry


@patch("requests.Session.get")
def test_download_url_with_retries_error_with_message(mock_get, boomi_client):
    """Test that _download_url_with_retries extracts message from error dict."""
    url = "https://api.boomi.com/download/file-123"
    output_path = "/tmp/test-download.txt"

    error_response = MagicMock()
    error_response.ok = False
    error_response.status_code = 500
    error_response.json.return_value = {"message": "Server error"}
    error_response.text = '{"message": "Server error"}'

    mock_get.return_value = error_response

    with patch("builtins.open", create=True):
        with pytest.raises(Exception) as exc_info:
            boomi_client._download_url_with_retries(url, output_path)

        assert "500" in str(exc_info.value)
        assert "Server error" in str(exc_info.value)


@patch("requests.Session.get")
def test_download_url_with_retries_error_with_non_dict_json(mock_get, boomi_client):
    """Test that _download_url_with_retries handles non-dict JSON error."""
    url = "https://api.boomi.com/download/file-123"
    output_path = "/tmp/test-download.txt"

    error_response = MagicMock()
    error_response.ok = False
    error_response.status_code = 500
    error_response.json.return_value = "Error string"
    error_response.text = '"Error string"'

    mock_get.return_value = error_response

    with patch("builtins.open", create=True):
        with pytest.raises(Exception) as exc_info:
            boomi_client._download_url_with_retries(url, output_path)

        assert "500" in str(exc_info.value)
        assert "Error string" in str(exc_info.value)


@patch("requests.Session.get")
def test_download_url_with_retries_creates_directory(mock_get, boomi_client):
    """Test that _download_url_with_retries creates parent directories."""
    url = "https://api.boomi.com/download/file-123"
    output_path = "/tmp/subdir/test-download.txt"

    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.status_code = 200
    mock_response.iter_content.return_value = [b"content"]
    mock_get.return_value = mock_response

    with patch("builtins.open", create=True) as mock_open:
        with patch("os.makedirs") as mock_makedirs:
            mock_file = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file

            result = boomi_client._download_url_with_retries(url, output_path)

            assert result == output_path
            mock_makedirs.assert_called_once_with("/tmp/subdir", exist_ok=True)


@patch("requests.Session.get")
def test_download_url_with_retries_no_directory_needed(mock_get, boomi_client):
    """Test that _download_url_with_retries handles files without parent directory."""
    url = "https://api.boomi.com/download/file-123"
    output_path = "test-download.txt"  # No parent directory

    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.status_code = 200
    mock_response.iter_content.return_value = [b"content"]
    mock_get.return_value = mock_response

    with patch("builtins.open", create=True) as mock_open:
        with patch("os.makedirs") as mock_makedirs:
            mock_file = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file

            result = boomi_client._download_url_with_retries(url, output_path)

            assert result == output_path
            # Should not call makedirs when there's no parent directory
            mock_makedirs.assert_not_called()


# Additional Connection Licensing Report Tests
@patch("requests.Session.request")
def test_get_connection_licensing_report_with_json_content(mock_request, boomi_client):
    """Test that get_connection_licensing_report handles JSON content in 200 response."""
    url = "https://api.boomi.com/download/report-123"
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"status": "complete", "data": "report data"}
    mock_response.text = '{"status": "complete"}'
    mock_response.content = b'{"status": "complete"}'
    mock_request.return_value = mock_response

    result = boomi_client.get_connection_licensing_report(url)

    assert result["status_code"] == 200
    assert result["status"] == "complete"
    assert "data" in result
    assert result["data"] == {"status": "complete", "data": "report data"}


@patch("requests.Session.request")
def test_get_connection_licensing_report_with_non_json_content(
    mock_request, boomi_client
):
    """Test that get_connection_licensing_report handles non-JSON content in 200 response."""
    url = "https://api.boomi.com/download/report-123"
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.headers = {"Content-Type": "text/csv"}
    mock_response.text = "col1,col2\nval1,val2"
    mock_response.content = b"col1,col2\nval1,val2"
    mock_response.json.side_effect = ValueError("Not JSON")
    mock_request.return_value = mock_response

    result = boomi_client.get_connection_licensing_report(url)

    assert result["status_code"] == 200
    assert result["status"] == "complete"
    assert "content" in result
    assert result["text"] == "col1,col2\nval1,val2"


@patch("requests.Session.request")
def test_get_connection_licensing_report_error_with_message(mock_request, boomi_client):
    """Test that get_connection_licensing_report extracts message from error."""
    url = "https://api.boomi.com/download/report-123"
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.headers = {}
    mock_response.json.return_value = {"message": "Server error"}
    mock_response.text = '{"message": "Server error"}'
    mock_response.content = None
    mock_request.return_value = mock_response

    with pytest.raises(Exception) as exc_info:
        boomi_client.get_connection_licensing_report(url)

    assert "500" in str(exc_info.value)
    assert "Server error" in str(exc_info.value)


@patch("requests.Session.request")
def test_get_connection_licensing_report_error_with_text(mock_request, boomi_client):
    """Test that get_connection_licensing_report handles error with text but no JSON."""
    url = "https://api.boomi.com/download/report-123"
    mock_response = MagicMock()
    mock_response.status_code = 500
    mock_response.headers = {}
    mock_response.json.side_effect = ValueError("Not JSON")
    mock_response.text = "Server error text"
    mock_response.content = None
    mock_request.return_value = mock_response

    with pytest.raises(Exception) as exc_info:
        boomi_client.get_connection_licensing_report(url)

    assert "500" in str(exc_info.value)
    assert "Server error text" in str(exc_info.value)


@patch("requests.Session.request")
@patch("time.sleep")
def test_download_connection_licensing_report_204_terminal(
    mock_sleep, mock_request, boomi_client
):
    """Test that download_connection_licensing_report handles 204 as terminal state."""
    create_response = MagicMock()
    create_response.ok = True
    create_response.headers = {"Content-Type": "application/json"}
    create_response.json.return_value = {
        "@type": "ConnectionLicensingDownload",
        "url": "https://api.boomi.com/download/report-123",
    }

    no_content_response = MagicMock()
    no_content_response.status_code = 204
    no_content_response.headers = {}
    no_content_response.text = ""
    no_content_response.content = None

    mock_request.side_effect = [create_response, no_content_response]

    result = boomi_client.download_connection_licensing_report(delay=0.1)

    assert result["status_code"] == 204
    assert result["status"] == "no_content"
    # Should sleep once before returning 204
    assert mock_sleep.call_count == 1


@patch("requests.Session.request")
@patch("time.sleep")
def test_download_connection_licensing_report_504_terminal(
    mock_sleep, mock_request, boomi_client
):
    """Test that download_connection_licensing_report handles 504 as terminal state."""
    create_response = MagicMock()
    create_response.ok = True
    create_response.headers = {"Content-Type": "application/json"}
    create_response.json.return_value = {
        "@type": "ConnectionLicensingDownload",
        "url": "https://api.boomi.com/download/report-123",
    }

    timeout_response = MagicMock()
    timeout_response.status_code = 504
    timeout_response.headers = {}
    timeout_response.text = ""
    timeout_response.content = None

    mock_request.side_effect = [create_response, timeout_response]

    result = boomi_client.download_connection_licensing_report(delay=0.1)

    assert result["status_code"] == 504
    assert result["status"] == "timeout"


@patch("requests.Session.request")
def test_get_connection_licensing_report_timeout(mock_request, boomi_client):
    """Test that get_connection_licensing_report handles timeout exceptions."""
    url = "https://api.boomi.com/download/report-123"
    mock_request.side_effect = requests.exceptions.Timeout("Request timed out")

    with pytest.raises(Exception) as exc_info:
        boomi_client.get_connection_licensing_report(url)

    assert "timeout" in str(exc_info.value).lower()


@patch("requests.Session.request")
def test_get_connection_licensing_report_connection_error(mock_request, boomi_client):
    """Test that get_connection_licensing_report handles connection errors."""
    url = "https://api.boomi.com/download/report-123"
    mock_request.side_effect = requests.exceptions.ConnectionError("Connection failed")

    with pytest.raises(Exception) as exc_info:
        boomi_client.get_connection_licensing_report(url)

    assert "connection error" in str(exc_info.value).lower()


@patch("requests.Session.request")
def test_get_connection_licensing_report_request_exception(mock_request, boomi_client):
    """Test that get_connection_licensing_report handles request exceptions."""
    url = "https://api.boomi.com/download/report-123"
    mock_request.side_effect = requests.exceptions.RequestException("Request failed")

    with pytest.raises(Exception) as exc_info:
        boomi_client.get_connection_licensing_report(url)

    assert "Request failed" in str(exc_info.value)


@patch("requests.Session.request")
def test_get_connection_licensing_report_unexpected_exception(
    mock_request, boomi_client
):
    """Test that get_connection_licensing_report handles unexpected exceptions."""
    url = "https://api.boomi.com/download/report-123"
    mock_request.side_effect = ValueError("Unexpected error")

    with pytest.raises(Exception) as exc_info:
        boomi_client.get_connection_licensing_report(url)

    assert "Unexpected error" in str(exc_info.value)


# Additional Client Initialization Tests
@patch.dict("os.environ", {}, clear=True)
@patch("pyboomi_platform.client.get_config")
def test_client_init_missing_all_params(mock_get_config):
    """Test that client raises ValueError when all params are missing."""
    # Mock get_config to return None (no config available)
    mock_get_config.return_value = None

    with pytest.raises(ValueError) as exc_info:
        BoomiPlatformClient()

    assert "account_id, username, and api_token must be provided" in str(exc_info.value)


@patch("requests.Session.request")
@patch("time.sleep")
def test_request_max_retries_exceeded_request_exception(
    mock_sleep, mock_request, boomi_client
):
    """Test that _request logs error and raises when max retries exceeded for RequestException."""
    mock_request.side_effect = requests.exceptions.RequestException("Temporary error")

    with pytest.raises(Exception) as exc_info:
        boomi_client._request("GET", "TestEndpoint", max_retries=1)

    assert "failed after" in str(exc_info.value).lower()
    assert "1 retries" in str(exc_info.value)
    assert mock_request.call_count == 2  # Initial + 1 retry


# Account Group Edge Cases
@patch("requests.Session.request")
def test_create_account_group_with_account_id_param(mock_request, boomi_client):
    """Test that create_account_group uses provided account_id parameter."""
    name = "TestGroup"
    account_id = "custom-account-123"
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"id": "group-123", "name": name}
    mock_request.return_value = mock_response

    result = boomi_client.create_account_group(name, account_id=account_id)

    assert result["name"] == name
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["json"]["accountId"] == account_id


@patch("requests.Session.request")
def test_create_account_group_with_auto_subscribe(mock_request, boomi_client):
    """Test that create_account_group includes auto_subscribe_alert_level when provided."""
    name = "TestGroup"
    alert_level = "none"
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"id": "group-123"}
    mock_request.return_value = mock_response

    result = boomi_client.create_account_group(
        name, auto_subscribe_alert_level=alert_level
    )

    assert result["id"] == "group-123"
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["json"]["autoSubscribeAlertLevel"] == alert_level


@patch("requests.Session.request")
def test_create_account_group_with_default_group(mock_request, boomi_client):
    """Test that create_account_group includes default_group when provided."""
    name = "TestGroup"
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"id": "group-123"}
    mock_request.return_value = mock_response

    result = boomi_client.create_account_group(name, default_group=True)

    assert result["id"] == "group-123"
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["json"]["defaultGroup"] is True


@patch("requests.Session.request")
def test_modify_account_group_with_name(mock_request, boomi_client):
    """Test that modify_account_group includes name when provided."""
    group_id = "group-123"
    new_name = "UpdatedGroup"
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"id": group_id, "name": new_name}
    mock_request.return_value = mock_response

    result = boomi_client.modify_account_group(group_id, name=new_name)

    assert result["name"] == new_name
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["json"]["name"] == new_name


@patch("requests.Session.request")
def test_modify_account_group_with_account_id_param(mock_request, boomi_client):
    """Test that modify_account_group uses provided account_id parameter."""
    group_id = "group-123"
    account_id = "custom-account-123"
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"id": group_id}
    mock_request.return_value = mock_response

    result = boomi_client.modify_account_group(group_id, account_id=account_id)

    assert result["id"] == group_id
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["json"]["accountId"] == account_id


@patch("requests.Session.request")
def test_modify_account_group_with_resources(mock_request, boomi_client):
    """Test that modify_account_group includes resources when provided."""
    group_id = "group-123"
    resources = [
        {
            "resourceId": "resource-1",
            "resourceName": "Resource1",
            "objectType": "Process",
        }
    ]
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"id": group_id}
    mock_request.return_value = mock_response

    result = boomi_client.modify_account_group(group_id, resources=resources)

    assert result["id"] == group_id
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert "Resources" in kwargs["json"]


# Query Process Test
@patch("requests.Session.request")
def test_query_process(mock_request, boomi_client):
    """Test that query_process queries for processes."""
    filters = {"name": "TestProcess"}
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"result": [{"id": "process-123"}]}
    mock_request.return_value = mock_response

    result = boomi_client.query_process(filters)

    assert "result" in result
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["method"] == "POST"
    assert "Process/query" in kwargs["url"]
    assert kwargs["json"] == filters


@patch("requests.Session.request")
def test_query_process_without_filters(mock_request, boomi_client):
    """Test that query_process works without filters."""
    mock_response = MagicMock()
    mock_response.ok = True
    mock_response.headers = {"Content-Type": "application/json"}
    mock_response.json.return_value = {"result": []}
    mock_request.return_value = mock_response

    result = boomi_client.query_process()

    assert "result" in result
    mock_request.assert_called_once()
    args, kwargs = mock_request.call_args
    assert kwargs["json"] == {}


# Config YAML Availability Tests
@patch.dict("os.environ", {}, clear=True)
def test_config_yaml_unavailable():
    """Test config behavior when YAML is not available."""
    import pyboomi_platform.config

    # Mock YAML_AVAILABLE to False
    original_value = pyboomi_platform.config.YAML_AVAILABLE
    pyboomi_platform.config.YAML_AVAILABLE = False

    try:
        config = pyboomi_platform.config.Config()
        boomi_config = config.get_boomi_config()

        # Should return empty/default values
        assert boomi_config["account_id"] is None
        assert boomi_config["username"] is None
        assert boomi_config["api_token"] is None
    finally:
        pyboomi_platform.config.YAML_AVAILABLE = original_value


# Additional Error Path Tests
@patch("requests.Session.request")
def test_request_handles_error_response_with_empty_text(mock_request, boomi_client):
    """Test that _request handles error response with empty text."""
    mock_response = MagicMock()
    mock_response.ok = False
    mock_response.status_code = 500
    mock_response.text = ""
    mock_response.json.side_effect = ValueError("Not JSON")
    mock_request.return_value = mock_response

    with pytest.raises(Exception) as exc_info:
        boomi_client._request("GET", "TestEndpoint")

    assert "500" in str(exc_info.value)


@patch("requests.Session.get")
@patch("time.sleep")
def test_download_url_retries_with_retry_after_message(
    mock_sleep, mock_get, boomi_client
):
    """Test that _download_url_with_retries extracts message from retry error."""
    url = "https://api.boomi.com/download/file-123"
    output_path = "/tmp/test.txt"

    retry_response = MagicMock()
    retry_response.status_code = 202
    retry_response.ok = False
    retry_response.headers = {"Retry-After": "1.0"}
    retry_response.json.return_value = {"message": "In progress"}
    retry_response.text = '{"message": "In progress"}'

    success_response = MagicMock()
    success_response.ok = True
    success_response.status_code = 200
    success_response.iter_content.return_value = [b"content"]

    mock_get.side_effect = [retry_response, success_response]

    with patch("builtins.open", create=True) as mock_open:
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        result = boomi_client._download_url_with_retries(
            url, output_path, max_retries=1, retry_statuses=[202]
        )

        assert result == output_path


@patch("requests.Session.get")
@patch("time.sleep")
def test_download_url_retries_with_non_dict_json_error(
    mock_sleep, mock_get, boomi_client
):
    """Test that _download_url_with_retries handles non-dict JSON in retry error."""
    url = "https://api.boomi.com/download/file-123"
    output_path = "/tmp/test.txt"

    retry_response = MagicMock()
    retry_response.status_code = 202
    retry_response.ok = False
    retry_response.headers = {"Retry-After": "1.0"}
    retry_response.json.return_value = "Error string"
    retry_response.text = '"Error string"'

    success_response = MagicMock()
    success_response.ok = True
    success_response.status_code = 200
    success_response.iter_content.return_value = [b"content"]

    mock_get.side_effect = [retry_response, success_response]

    with patch("builtins.open", create=True) as mock_open:
        mock_file = MagicMock()
        mock_open.return_value.__enter__.return_value = mock_file

        result = boomi_client._download_url_with_retries(
            url, output_path, max_retries=1, retry_statuses=[202]
        )

        assert result == output_path
