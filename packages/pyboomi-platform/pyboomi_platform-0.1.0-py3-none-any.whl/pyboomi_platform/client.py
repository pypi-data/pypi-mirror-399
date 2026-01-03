#!/usr/bin/env python3
#
# PyBoomi Platform - Client Module
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
Boomi Platform Client

This module defines a client class to interact with the Boomi Platform API
using platform API tokens for authentication. It includes built-in retry logic
for rate-limiting scenarios and supports basic query operations such as folder
and process retrieval.
"""

__author__ = "Robert Little"
__copyright__ = "Copyright 2025, Robert Little"
__license__ = "Apache 2.0"
__version__ = "0.1.0"

import logging
import os
import time
from typing import Any, Dict, List, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from .auth import BoomiAuth
from .config import Config, get_config
from .exceptions import BoomiAPIError

# Set up logger for this module
logger = logging.getLogger(__name__)


class BoomiPlatformClient:
    """
    A client for interacting with the Boomi Platform API.

    Supports both direct parameter initialization and configuration file/environment
    variable initialization for flexible deployment scenarios.
    """

    DEFAULT_BASE_URL = "https://api.boomi.com/api/rest/v1"
    DEFAULT_TIMEOUT = 30
    DEFAULT_MAX_RETRIES = 3
    DEFAULT_BACKOFF_FACTOR = 1.5
    # Status codes for automatic retry (excluding 429, 503 which are handled manually)
    RETRYABLE_STATUS_CODES = [500, 502, 504]
    # Status codes that should respect Retry-After header (handled manually)
    RATE_LIMIT_STATUS_CODES = [429, 503]

    def __init__(
        self,
        account_id: Optional[str] = None,
        username: Optional[str] = None,
        api_token: Optional[str] = None,
        base_url: Optional[str] = None,
        timeout: Optional[int] = None,
        max_retries: Optional[int] = None,
        backoff_factor: Optional[float] = None,
        config: Optional[Config] = None,
        config_path: Optional[str] = None,
    ):
        """
        Initialize the Boomi Platform API client.

        :param account_id: Boomi account ID.
        :param username: Boomi username/email associated with the API token.
        :param api_token: Boomi Platform API token value.
        :param base_url: Optional custom base URL (defaults to Boomi public API).
        :param timeout: Request timeout in seconds.
        :param max_retries: Maximum number of retry attempts.
        :param backoff_factor: Backoff factor for retry delays.
        :param config: Pre-loaded configuration object.
        :param config_path: Path to configuration file.
        """
        # Load configuration if not provided directly
        if config is None and (
            account_id is None or username is None or api_token is None
        ):
            config = get_config(config_path)

        if config:
            boomi_config = config.get_boomi_config()
            self.account_id = account_id or boomi_config.get("account_id")
            self.username = username or boomi_config.get("username")
            self.api_token = api_token or boomi_config.get("api_token")
            self.timeout = timeout or boomi_config.get("timeout", self.DEFAULT_TIMEOUT)
            self.max_retries = max_retries or boomi_config.get(
                "max_retries", self.DEFAULT_MAX_RETRIES
            )
            self.backoff_factor = backoff_factor or boomi_config.get(
                "backoff_factor", self.DEFAULT_BACKOFF_FACTOR
            )
            base_api_url = base_url or boomi_config.get(
                "base_url", self.DEFAULT_BASE_URL
            )
        else:
            # Direct parameter initialization (backward compatibility)
            if not all([account_id, username, api_token]):
                raise ValueError(
                    "account_id, username, and api_token must be provided either directly or via configuration"
                )

            self.account_id = account_id
            self.username = username
            self.api_token = api_token
            self.timeout = timeout or self.DEFAULT_TIMEOUT
            self.max_retries = max_retries or self.DEFAULT_MAX_RETRIES
            self.backoff_factor = backoff_factor or self.DEFAULT_BACKOFF_FACTOR
            base_api_url = base_url or self.DEFAULT_BASE_URL

        # Validate required parameters
        if not self.account_id:
            raise ValueError("Boomi account_id must be provided")
        if not self.username:
            raise ValueError("Boomi username must be provided")
        if not self.api_token:
            raise ValueError("Boomi api_token must be provided")

        # Construct full base URL with account ID
        base_api_url = base_api_url.rstrip("/")
        if not base_api_url.endswith(f"/{self.account_id}"):
            self.base_url = f"{base_api_url}/{self.account_id}"
        else:
            self.base_url = base_api_url

        # Initialize authentication
        self.auth = BoomiAuth(self.username, self.api_token)

        # Create session with retry configuration
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """
        Create a requests session with retry configuration and authentication.

        :return: Configured requests session.
        """
        session = requests.Session()

        # Configure retry strategy
        retry_strategy = Retry(
            total=self.max_retries,
            backoff_factor=self.backoff_factor,
            status_forcelist=self.RETRYABLE_STATUS_CODES,
            allowed_methods=["HEAD", "GET", "POST", "PUT", "DELETE", "OPTIONS"],
        )

        # Mount adapter with retry strategy
        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("https://", adapter)
        session.mount("http://", adapter)

        # Set default headers
        auth_headers = self.auth.get_auth_header()
        session.headers.update(auth_headers)
        session.headers.update(
            {"Content-Type": "application/json", "Accept": "application/json"}
        )

        return session

    def _request(
        self,
        method: str,
        endpoint: str,
        headers: Optional[Dict[str, str]] = None,
        data: Any = None,
        json: Any = None,
        timeout: Optional[int] = None,
        max_retries: Optional[int] = None,
    ) -> Any:
        """
        Make an API request using the configured session with enhanced retry logic.

        This method handles rate limiting by respecting the Retry-After header
        when present, while falling back to exponential backoff for other retryable
        errors. The session's automatic retry mechanism handles most cases, but
        rate limiting (429, 503) is handled manually to respect server timing hints.

        :param method: HTTP method to use (e.g., "GET", "POST").
        :param endpoint: API path (e.g., "Folder/query").
        :param headers: Optional headers to override default headers.
        :param data: Raw request body for non-JSON payloads (e.g., pagination token).
        :param json: JSON request body for API operations.
        :param timeout: Request timeout (uses instance default if not provided).
        :param max_retries: Maximum retry attempts for rate limiting (uses instance default if not provided).
        :return: Parsed JSON response or a dict with raw content if not JSON.
        :raises BoomiAPIError: If the request fails after retries.
        """
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        request_timeout = timeout or self.timeout
        retry_limit = max_retries or self.max_retries
        retries = 0
        backoff = self.backoff_factor

        # Prepare headers
        request_headers = {}
        if headers:
            request_headers.update(headers)

        while retries <= retry_limit:
            try:
                # Make request using session (which handles automatic retries for most errors)
                response = self.session.request(
                    method=method,
                    url=url,
                    headers=request_headers,
                    data=data,
                    json=json,
                    timeout=request_timeout,
                )

                # Handle rate limiting with Retry-After header support
                if response.status_code in self.RATE_LIMIT_STATUS_CODES:
                    # Check if we've exceeded retry limit
                    if retries >= retry_limit:
                        error_msg = f"Boomi API rate limit error: HTTP {response.status_code} (max retries exceeded)"
                        try:
                            error_detail = response.json()
                            if (
                                isinstance(error_detail, dict)
                                and "message" in error_detail
                            ):
                                error_msg += f" - {error_detail['message']}"
                            else:
                                error_msg += f" - {error_detail}"
                        except (ValueError, KeyError):
                            error_msg += f" - {response.text}"

                        raise BoomiAPIError(
                            error_msg,
                            status_code=response.status_code,
                            response_body=response.text,
                        )

                    # Get retry-after header if available, otherwise use exponential backoff
                    retry_after = response.headers.get("Retry-After")
                    if retry_after:
                        try:
                            sleep_time = float(retry_after)
                        except (ValueError, TypeError):
                            # Invalid Retry-After value, fall back to exponential backoff
                            sleep_time = backoff
                    else:
                        sleep_time = backoff

                    retries += 1
                    logger.warning(
                        f"Rate limit hit (HTTP {response.status_code}). "
                        f"Retrying in {sleep_time:.2f} seconds... "
                        f"(Attempt {retries}/{retry_limit})"
                    )
                    time.sleep(sleep_time)
                    backoff *= 2  # Exponential backoff for next attempt
                    continue

                # Check for other HTTP errors
                if not response.ok:
                    error_msg = f"Boomi API error: HTTP {response.status_code}"
                    try:
                        error_detail = response.json()
                        if isinstance(error_detail, dict) and "message" in error_detail:
                            error_msg += f" - {error_detail['message']}"
                        else:
                            error_msg += f" - {error_detail}"
                    except (ValueError, KeyError):
                        error_msg += f" - {response.text}"

                    raise BoomiAPIError(
                        error_msg,
                        status_code=response.status_code,
                        response_body=response.text,
                    )

                # Success - parse response
                content_type = response.headers.get("Content-Type", "")
                if content_type.startswith("application/json"):
                    return response.json()
                elif content_type.startswith(
                    "application/xml"
                ) or content_type.startswith("text/xml"):
                    return response.text
                else:
                    return {
                        "content": response.content,
                        "headers": dict(response.headers),
                    }

            except BoomiAPIError:
                # Re-raise BoomiAPIError as-is (already handled above)
                raise
            except requests.exceptions.Timeout:
                raise BoomiAPIError(f"Request timeout after {request_timeout} seconds")
            except requests.exceptions.ConnectionError as e:
                raise BoomiAPIError(f"Connection error: {e}")
            except requests.exceptions.RequestException as e:
                # For other request exceptions, check if we should retry
                retries += 1
                if retries > retry_limit:
                    logger.error(
                        f"Maximum retries ({retry_limit}) exceeded. Last error: {e}"
                    )
                    raise BoomiAPIError(
                        f"Request failed after {retry_limit} retries: {e}"
                    )

                sleep_time = backoff
                logger.warning(
                    f"Request error: {e}. Retrying in {sleep_time:.2f} seconds... "
                    f"(Attempt {retries}/{retry_limit})"
                )
                time.sleep(sleep_time)
                backoff *= 2  # Exponential backoff
            except Exception as e:
                raise BoomiAPIError(f"Unexpected error: {e}")

        # This should not be reached due to exceptions in the loop
        raise BoomiAPIError("Unexpected error in request retry loop")

    def get_account(self, account_id: Optional[str] = None) -> Any:
        """
        Retrieves the account information for the current Boomi account.
        :param account_id: The ID of the account to retrieve. If not provided, uses the account_id configured in the client.
        :return: JSON response containing the account information.
        """
        account_id_to_use = account_id or self.account_id
        return self._request("GET", f"Account/{account_id_to_use}")

    def get_account_bulk(self, account_ids: List[str]) -> Any:
        """
        The bulk GET operation returns multiple Account objects based on the supplied account IDs, to a maximum of 100.
        :param account_ids: The IDs of the accounts to retrieve.
        :return: JSON response containing the account information.
        """
        payload = {
            "type": "GET",
            "request": [{"id": account_id} for account_id in account_ids],
        }
        return self._request("POST", "Account/bulk", json=payload)

    def query_account(self, filters: Optional[Dict[str, Any]] = None) -> Any:
        """
        Queries for Account objects using optional filter criteria.
        :param filters: Dictionary of query fields (e.g., {"name": "MyAccount"}).
        :return: JSON response containing matched Account objects.
        """
        return self._request("POST", "Account/query", json=filters or {})

    def query_more_accounts(self, token: str) -> Any:
        """
        Retrieves the next page of Account results using a continuation token.
        :param token: Pagination token returned from a previous Account query.
        :return: JSON response with the next set of Account results.
        """
        headers = {"Content-Type": "text/plain"}
        return self._request("POST", "Account/queryMore", data=token, headers=headers)

    def create_account_group(
        self,
        name: str,
        account_id: Optional[str] = None,
        auto_subscribe_alert_level: Optional[str] = None,
        default_group: Optional[bool] = None,
        resources: Optional[List[Dict[str, str]]] = None,
    ) -> Any:
        """
        Creates a new account group.
        :param name: The name of the account group (required).
        :param account_id: The ID of the account. If not provided, uses the account_id configured in the client.
        :param auto_subscribe_alert_level: Alert level for auto-subscribe (e.g., "none").
        :param default_group: Whether this is the default group.
        :param resources: List of resource dictionaries, each with resourceId, resourceName, and objectType.
        :return: JSON response containing the created account group.
        """
        payload: Dict[str, Any] = {"name": name}

        if account_id:
            payload["accountId"] = account_id
        elif self.account_id:
            payload["accountId"] = self.account_id

        if auto_subscribe_alert_level is not None:
            payload["autoSubscribeAlertLevel"] = auto_subscribe_alert_level

        if default_group is not None:
            payload["defaultGroup"] = default_group

        if resources:
            resource_list = [
                {
                    "@type": "Resource",
                    "resourceId": resource.get("resourceId", ""),
                    "resourceName": resource.get("resourceName", ""),
                    "objectType": resource.get("objectType", ""),
                }
                for resource in resources
            ]
            payload["Resources"] = {
                "@type": "Resources",
                "Resource": resource_list,
            }

        return self._request("POST", "AccountGroup", json=payload)

    def get_account_group(self, account_group_id: str) -> Any:
        """
        Retrieves an account group.
        :param account_group_id: The ID of the account group to retrieve.
        :return: JSON response containing the account group.
        """
        return self._request("GET", f"AccountGroup/{account_group_id}")

    def modify_account_group(
        self,
        account_group_id: str,
        name: Optional[str] = None,
        account_id: Optional[str] = None,
        auto_subscribe_alert_level: Optional[str] = None,
        default_group: Optional[bool] = None,
        resources: Optional[List[Dict[str, str]]] = None,
    ) -> Any:
        """
        Modifies an account group.
        :param account_group_id: The ID of the account group to modify.
        :param name: The name of the account group.
        :param account_id: The ID of the account. If not provided, uses the account_id configured in the client.
        :param auto_subscribe_alert_level: Alert level for auto-subscribe (e.g., "none").
        :param default_group: Whether this is the default group.
        :param resources: List of resource dictionaries, each with resourceId, resourceName, and objectType.
        :return: JSON response containing the modified account group.
        """
        payload: Dict[str, Any] = {}

        if name is not None:
            payload["name"] = name

        if account_id:
            payload["accountId"] = account_id
        elif self.account_id:
            payload["accountId"] = self.account_id

        if auto_subscribe_alert_level is not None:
            payload["autoSubscribeAlertLevel"] = auto_subscribe_alert_level

        if default_group is not None:
            payload["defaultGroup"] = default_group

        if resources:
            resource_list = [
                {
                    "@type": "Resource",
                    "resourceId": resource.get("resourceId", ""),
                    "resourceName": resource.get("resourceName", ""),
                    "objectType": resource.get("objectType", ""),
                }
                for resource in resources
            ]
            payload["Resources"] = {
                "@type": "Resources",
                "Resource": resource_list,
            }

        return self._request("POST", f"AccountGroup/{account_group_id}", json=payload)

    def get_account_group_bulk(self, account_group_ids: List[str]) -> Any:
        """
        The bulk GET operation returns multiple AccountGroup objects based on the supplied account group IDs, to a maximum of 100.
        :param account_group_ids: The IDs of the account groups to retrieve.
        :return: JSON response containing the account groups.
        """
        payload = {
            "type": "GET",
            "request": [
                {"id": account_group_id} for account_group_id in account_group_ids
            ],
        }
        return self._request("POST", "AccountGroup/bulk", json=payload)

    def query_account_group(self, filters: Optional[Dict[str, Any]] = None) -> Any:
        """
        Queries for AccountGroup objects using optional filter criteria.
        :param filters: Dictionary of query fields (e.g., {"name": "MyAccountGroup"}).
        :return: JSON response containing matched AccountGroup objects.
        """
        return self._request("POST", "AccountGroup/query", json=filters or {})

    def query_more_account_groups(self, token: str) -> Any:
        """
        Retrieves the next page of AccountGroup results using a continuation token.
        :param token: Pagination token returned from a previous AccountGroup query.
        :return: JSON response with the next set of AccountGroup results.
        """
        headers = {"Content-Type": "text/plain"}
        return self._request(
            "POST", "AccountGroup/queryMore", data=token, headers=headers
        )

    def get_account_sso_config(self, account_id: str) -> Any:
        """
        Retrieves the SSO configuration for an account.
        :param account_id: The ID of the account to retrieve the SSO configuration for.
        :return: JSON response containing the SSO configuration.
        """
        account_id_to_use = account_id or self.account_id
        return self._request("GET", f"AccountSSOConfig/{account_id_to_use}")

    def modify_account_sso_config(
        self, account_id: str, sso_config: Dict[str, Any]
    ) -> Any:
        """
        Modifies the SSO configuration for an account.
        :param account_id: The ID of the account to modify the SSO configuration for.
        :param sso_config: The SSO configuration to modify.
        :return: JSON response containing the modified SSO configuration.
        """
        account_id_to_use = account_id or self.account_id
        return self._request(
            "POST", f"AccountSSOConfig/{account_id_to_use}", json=sso_config
        )

    def get_account_sso_config_bulk(self, account_ids: List[str]) -> Any:
        """
        The bulk GET operation returns multiple AccountSSOConfig objects based on the supplied account IDs, to a maximum of 100.
        :param account_ids: The IDs of the accounts to retrieve the SSO configuration for.
        :return: JSON response containing the SSO configurations.
        """
        payload = {
            "type": "GET",
            "request": [{"id": account_id} for account_id in account_ids],
        }
        return self._request("POST", "AccountSSOConfig/bulk", json=payload)

    def query_account_sso_config(self, filters: Optional[Dict[str, Any]] = None) -> Any:
        """
        Queries for AccountSSOConfig objects using optional filter criteria.
        :param filters: Dictionary of query fields (e.g., {"name": "MyAccountSSOConfig"}).
        :return: JSON response containing matched AccountSSOConfig objects.
        """
        return self._request("POST", "AccountSSOConfig/query", json=filters or {})

    def query_more_account_sso_configs(self, token: str) -> Any:
        """
        Retrieves the next page of AccountSSOConfig results using a continuation token.
        :param token: Pagination token returned from a previous AccountSSOConfig query.
        :return: JSON response with the next set of AccountSSOConfig results.
        """
        headers = {"Content-Type": "text/plain"}
        return self._request(
            "POST", "AccountSSOConfig/queryMore", data=token, headers=headers
        )

    def create_account_user_federation(
        self,
        federation_id: str,
        user_id: str,
        account_id: Optional[str] = None,
    ) -> Any:
        """
        Creates a new account user federation.
        :param federation_id: The federation ID for the user federation.
        :param user_id: The user ID for the user federation.
        :param account_id: The ID of the account to create the user federation for. If not provided, uses the account_id configured in the client.
        :return: JSON response containing the created user federation.
        """
        account_id_to_use = account_id or self.account_id
        payload = {
            "federationId": federation_id,
            "userId": user_id,
            "accountId": account_id_to_use,
        }
        return self._request("POST", "AccountUserFederation", json=payload)

    def query_account_user_federation(
        self, filters: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Queries for AccountUserFederation objects using optional filter criteria.
        :param filters: Dictionary of query fields (e.g., {"name": "MyAccountUserFederation"}).
        :return: JSON response containing matched AccountUserFederation objects.
        """
        return self._request("POST", "AccountUserFederation/query", json=filters or {})

    def query_more_account_user_federations(self, token: str) -> Any:
        """
        Retrieves the next page of AccountUserFederation results using a continuation token.
        :param token: Pagination token returned from a previous AccountUserFederation query.
        :return: JSON response with the next set of AccountUserFederation results.
        """
        headers = {"Content-Type": "text/plain"}
        return self._request(
            "POST", "AccountUserFederation/queryMore", data=token, headers=headers
        )

    def modify_account_user_federation(
        self,
        id: str,
        federation_id: str,
        user_id: str,
        account_id: Optional[str] = None,
    ) -> Any:
        """
        Modifies an account user federation.
        :param id: The object's conceptual ID, which is synthesized from the federation, user, and account IDs.
        :param federation_id: The federation ID for the user federation.
        :param user_id: The user ID for the user federation.
        :param account_id: The ID of the account to modify the user federation for. If not provided, uses the account_id configured in the client.
        :return: JSON response containing the modified user federation.
        """
        account_id_to_use = account_id or self.account_id
        payload = {
            "federationId": federation_id,
            "userId": user_id,
            "accountId": account_id_to_use,
        }
        return self._request("POST", f"AccountUserFederation/{id}", json=payload)

    def delete_account_user_federation(self, id: str) -> Any:
        """
        Deletes an account user federation.
        :param id: The object's conceptual ID, which is synthesized from the federation, user, and account IDs.
        :return: JSON response containing the deleted user federation.
        """
        return self._request("DELETE", f"AccountUserFederation/{id}")

    def create_account_user_role(
        self,
        firstName: str,
        lastName: str,
        notifyUser: bool = False,
        roleId: Optional[str] = None,
        userId: Optional[str] = None,
        account_id: Optional[str] = None,
    ) -> Any:
        """
        Creates a new account user role.
        :param firstName: The first name of the user.
        :param lastName: The last name of the user.
        :param notifyUser: Whether to notify the user.
        :param roleId: The ID of the role to create the user role for.
        :param user_id: The ID of the user to create the user role for.
        :param account_id: The ID of the account to create the user role for. If not provided, uses the account_id configured in the client.
        :return: JSON response containing the created user role.
        """
        account_id_to_use = account_id or self.account_id
        payload = {
            "firstName": firstName,
            "lastName": lastName,
            "notifyUser": notifyUser,
            "roleId": roleId,
            "userId": userId,
            "accountId": account_id_to_use,
        }
        return self._request("POST", "AccountUserRole", json=payload)

    def query_account_user_role(self, filters: Optional[Dict[str, Any]] = None) -> Any:
        """
        Queries for AccountUserRole objects using optional filter criteria.
        :param filters: Dictionary of query fields (e.g., {"name": "MyAccountUserRole"}).
        :return: JSON response containing matched AccountUserRole objects.
        """
        return self._request("POST", "AccountUserRole/query", json=filters or {})

    def query_more_account_user_roles(self, token: str) -> Any:
        """
        Retrieves the next page of AccountUserRole results using a continuation token.
        :param token: Pagination token returned from a previous AccountUserRole query.
        :return: JSON response with the next set of AccountUserRole results.
        """
        headers = {"Content-Type": "text/plain"}
        return self._request(
            "POST", "AccountUserRole/queryMore", data=token, headers=headers
        )

    def delete_account_user_role(self, id: str) -> Any:
        """
        Deletes an account user role.
        :param id: The ID of the account user role to delete.
        :return: JSON response containing the deleted user role.
        """
        return self._request("DELETE", f"AccountUserRole/{id}")

    def query_api_usage_count(self, filters: Optional[Dict[str, Any]] = None) -> Any:
        """
        Queries for ApiUsageCount objects using optional filter criteria.
        :param filters: Dictionary of query fields (e.g., {"name": "MyApiUsageCount"}).
        :return: JSON response containing matched ApiUsageCount objects.
        """
        return self._request("POST", "ApiUsageCount/query", json=filters or {})

    def query_more_api_usage_counts(self, token: str) -> Any:
        """
        Retrieves the next page of ApiUsageCount results using a continuation token.
        :param token: Pagination token returned from a previous ApiUsageCount query.
        :return: JSON response with the next set of ApiUsageCount results.
        """
        headers = {"Content-Type": "text/plain"}
        return self._request(
            "POST", "ApiUsageCount/queryMore", data=token, headers=headers
        )

    def get_audit_log(self, audit_log_id: str) -> Any:
        """
        Retrieves an audit log.
        :param audit_log_id: The ID of the audit log to retrieve.
        :return: JSON response containing the audit log.
        """
        return self._request("GET", f"AuditLog/{audit_log_id}")

    def get_audit_log_bulk(self, audit_log_ids: List[str]) -> Any:
        """
        The bulk GET operation returns multiple AuditLog objects based on the supplied audit log IDs, to a maximum of 100.
        :param audit_log_ids: The IDs of the audit logs to retrieve.
        :return: JSON response containing the audit logs.
        """
        payload = {
            "type": "GET",
            "request": [{"id": audit_log_id} for audit_log_id in audit_log_ids],
        }
        return self._request("POST", "AuditLog/bulk", json=payload)

    def query_audit_log(self, filters: Optional[Dict[str, Any]] = None) -> Any:
        """
        Queries for AuditLog objects using optional filter criteria.
        :param filters: Dictionary of query fields (e.g., {"name": "MyAuditLog"}).
        :return: JSON response containing matched AuditLog objects.
        """
        return self._request("POST", "AuditLog/query", json=filters or {})

    def query_more_audit_logs(self, token: str) -> Any:
        """
        Retrieves the next page of AuditLog results using a continuation token.
        :param token: Pagination token returned from a previous AuditLog query.
        :return: JSON response with the next set of AuditLog results.
        """
        headers = {"Content-Type": "text/plain"}
        return self._request("POST", "AuditLog/queryMore", data=token, headers=headers)

    def query_process(self, filters: Optional[Dict[str, Any]] = None) -> Any:
        """
        Queries for Process objects using optional filter criteria.

        :param filters: Dictionary of query fields (e.g., {"name": "MyProcess"}).
        :return: JSON response containing matched Process objects.
        """
        return self._request("POST", "Process/query", json=filters or {})

    def create_folder(self, name: str, parent_id: Optional[str] = None) -> Any:
        """
        Creates a folder.
        :param name: The name of the folder to create.
        :param parent_id: The ID of the parent folder to create the folder under.
        :return: JSON response containing the created folder.
        """
        return self._request(
            "POST",
            "Folder",
            json={"@type": "Folder", "name": name, "parentId": parent_id},
        )

    def get_folder(self, folder_id: str) -> Any:
        """
        Retrieves a folder by its ID.
        :param folder_id: The ID of the folder to retrieve.
        :return: JSON response containing the folder.
        """
        return self._request("GET", f"Folder/{folder_id}")

    def update_folder(
        self,
        folder_id: str,
        name: Optional[str] = None,
        parent_id: Optional[str] = None,
    ) -> Any:
        """
        Updates a folder.
        :param folder_id: The ID of the folder to update.
        :param name: The name of the folder to update.
        :param parent_id: The ID of the parent folder to update the folder under.
        :return: JSON response containing the updated folder.
        """
        return self._request(
            "POST", f"Folder/{folder_id}", json={"name": name, "parentId": parent_id}
        )

    def delete_folder(self, folder_id: str) -> Any:
        """
        Deletes a folder.
        :param folder_id: The ID of the folder to delete.
        :return: JSON response containing the deleted folder.
        """
        return self._request("DELETE", f"Folder/{folder_id}")

    def get_folder_bulk(self, folder_ids: List[str]) -> Any:
        """
        Retrieves a list of folders by their IDs.
        :param folder_ids: The IDs of the folders to retrieve.
        :return: JSON response containing the folders.
        """
        return self._request("POST", "Folder/bulk", json={"ids": folder_ids})

    def query_folder(self, filters: Optional[Dict[str, Any]] = None) -> Any:
        """
        Queries for Folder objects using optional filter criteria.
        :param filters: Dictionary of query fields (e.g., {"name": "MyFolder"}).
        :return: JSON response containing matched Folder objects.
        """
        return self._request("POST", "Folder/query", json=filters or {})

    def query_folders(self, filters: Optional[Dict[str, Any]] = None) -> Any:
        """
        Queries for Folder objects using optional filter criteria.

        :param filters: Dictionary of query fields (e.g., {"name": "MyFolder"}).
        :return: JSON response containing matched Folder objects.
        """
        return self._request("POST", "Folder/query", json=filters or {})

    def query_more_folders(self, token: str) -> Any:
        """
        Retrieves the next page of folder results using a continuation token.

        :param token: Pagination token returned from a previous folder query.
        :return: JSON response with the next set of Folder results.
        """
        headers = {"Content-Type": "text/plain"}
        return self._request("POST", "Folder/queryMore", data=token, headers=headers)

    def query_component_metadata(self, filters: Optional[Dict[str, Any]] = None) -> Any:
        """
        Queries ComponentMetadata using the provided filter criteria.
        :param query_filter: Dictionary containing the query filter structure.
        :return: JSON response containing matched ComponentMetadata objects.
        """
        return self._request("POST", "ComponentMetadata/query", json=filters)

    def query_more_component_metadata(self, token: str) -> Any:
        """
        Retrieves the next page of ComponentMetadata results using a continuation token.

        :param token: Pagination token returned from a previous ComponentMetadata query.
        :return: JSON response with the next set of ComponentMetadata results.
        """
        headers = {"Content-Type": "text/plain"}
        return self._request(
            "POST", "ComponentMetadata/queryMore", data=token, headers=headers
        )

    def get_component_metadata(
        self, component_id: str, branch_id: Optional[str] = None
    ) -> Any:
        """
        Retrieves the metadata for a specific component.
        :param component_id: The ID of the component to retrieve metadata for.
        :param branch_id: The ID of the branch to retrieve metadata for.
        :return: JSON response containing the component metadata.
        """
        endpoint = f"ComponentMetadata/{component_id}"
        if branch_id:
            endpoint = f"{endpoint}~{branch_id}"
        return self._request("GET", endpoint)

    def create_component(
        self,
        component_xml: str,
        folder_id: Optional[str] = None,
    ) -> Any:
        """
        Creates a component from XML content.

        The Component endpoint requires XML content and expects Content-Type
        and Accept headers to be set to application/xml.

        :param component_xml: The XML content representing the component to create.
            This should be a valid Boomi component XML structure (e.g., Process, Connection, etc.).
        :param folder_id: Optional ID of the folder to create the component in.
            If not provided, the component will be created in the default location.
        :return: XML response containing the created component.
        """
        headers = {
            "Content-Type": "application/xml",
            "Accept": "application/xml",
        }
        endpoint = "Component"
        if folder_id:
            endpoint = f"{endpoint}?folderId={folder_id}"
        return self._request("POST", endpoint, data=component_xml, headers=headers)

    def update_component(self, component_id: str, component_xml: str) -> Any:
        """
        Updates a component by its ID.
        :param component_id: The ID of the component to update.
        :param component_xml: The XML content representing the component to update.
        :return: XML response containing the updated component.
        """
        headers = {
            "Content-Type": "application/xml",
            "Accept": "application/xml",
        }
        return self._request(
            "POST", f"Component/{component_id}", data=component_xml, headers=headers
        )

    def get_component(self, component_id: str) -> Any:
        """
        Retrieves a component by its ID.

        The Component endpoint can ONLY return XML, so we must set the Accept
        header to application/xml to avoid 406 Not Acceptable errors.

        :param component_id: The ID of the component to retrieve.
        :return: XML response as text string.
        """
        headers = {"Accept": "application/xml"}
        return self._request("GET", f"Component/{component_id}", headers=headers)

    def get_component_bulk(self, component_ids: List[str]) -> Any:
        """
        Retrieves a list of components by their IDs.
        :param component_ids: The IDs of the components to retrieve.
        :return: JSON response containing the components.
        """
        return self._request("POST", "Component/bulk", json={"ids": component_ids})

    def create_packaged_component(
        self,
        component_id: str,
        package_version: Optional[str] = None,
        notes: Optional[str] = None,
        branch_name: Optional[str] = None,
    ) -> Any:
        """
        Creates a packaged component.
        :param component_id: The ID of the component to create a packaged component for.
        :param package_version: The version of the package to create a packaged component for.
        :param notes: The notes for the packaged component.
        :param branch_name: The name of the branch to create a packaged component for.
        :return: JSON response containing the packaged component.
        """
        return self._request(
            "POST",
            "PackagedComponent",
            json={
                "componentId": component_id,
                "packageVersion": package_version,
                "notes": notes,
                "branchName": branch_name,
            },
        )

    def get_packaged_component(self, packaged_component_id: str) -> Any:
        """
        Retrieves a packaged component.
        :param packaged_component_id: The ID of the packaged component to retrieve.
        :return: JSON response containing the packaged component.
        """
        return self._request("GET", f"PackagedComponent/{packaged_component_id}")

    def query_packaged_components(
        self, filters: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Queries for PackagedComponent objects using optional filter criteria.
        :param filters: Dictionary of query fields (e.g., {"name": "MyPackagedComponent"}).
        :return: JSON response containing matched PackagedComponent objects.
        """
        return self._request("POST", "PackagedComponent/query", json=filters or {})

    def query_more_packaged_components(self, token: str) -> Any:
        """
        Retrieves the next page of PackagedComponent results using a continuation token.
        :param token: Pagination token returned from a previous PackagedComponent query.
        :return: JSON response with the next set of PackagedComponent results.
        """
        headers = {"Content-Type": "text/plain"}
        return self._request(
            "POST", "PackagedComponent/queryMore", data=token, headers=headers
        )

    def create_deployed_package(
        self,
        package_id: str,
        environment_id: str,
        listener_status: Optional[str] = None,
    ) -> Any:
        """
        Creates a deployed package.
        :param environment_id: The ID of the environment to create a deployed package for.
        :param package_id: The ID of the package to create a deployed package for.
        :param listener_status: The status of the listener to create a deployed package for.
        :return: JSON response containing the deployed package.
        """
        return self._request(
            "POST",
            "DeployedPackage",
            json={
                "environmentId": environment_id,
                "packageId": package_id,
                "listenerStatus": listener_status,
            },
        )

    def get_deployed_package(self, deployed_package_id: str) -> Any:
        """
        Retrieves a deployed package.
        :param deployed_package_id: The ID of the deployed package to retrieve.
        :return: JSON response containing the deployed package.
        """
        return self._request("GET", f"DeployedPackage/{deployed_package_id}")

    def query_deployed_packages(self, filters: Optional[Dict[str, Any]] = None) -> Any:
        """
        Queries for DeployedPackage objects using optional filter criteria.
        :param filters: Dictionary of query fields (e.g., {"name": "MyDeployedPackage"}).
        :return: JSON response containing matched DeployedPackage objects.
        """
        return self._request("POST", "DeployedPackage/query", json=filters or {})

    def query_more_deployed_packages(self, token: str) -> Any:
        """
        Retrieves the next page of DeployedPackage results using a continuation token.
        :param token: Pagination token returned from a previous DeployedPackage query.
        :return: JSON response with the next set of DeployedPackage results.
        """
        headers = {"Content-Type": "text/plain"}
        return self._request(
            "POST", "DeployedPackage/queryMore", data=token, headers=headers
        )

    def create_connection_licensing_report(
        self, filters: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Creates a connection licensing report request.

        Returns a payload containing a URL that can be used to download the connection
        licensing report. The response includes:
        - @type: "ConnectionLicensingDownload"
        - url: The URL to retrieve the report
        - message: Status message
        - statusCode: HTTP status code (typically "202")

        :param filters: Optional dictionary of filter criteria for the report.
        :return: JSON response containing the report download URL and metadata.
        """
        return self._request("POST", "ConnectionLicensingReport", json=filters or {})

    def get_connection_licensing_report(self, url: str) -> Any:
        """
        Retrieves the connection licensing report from the provided URL.

        This method downloads the report from the URL returned by
        create_connection_licensing_report. The URL is typically in the format:
        https://<environment>.boomi.com/account/<accountId>/api/download/ConnectionLicensing-<id>

        Note: The download URL is valid for a single request. After a successful
        response (200, 204, or 504), the URL becomes inactive and subsequent
        requests will return 404.

        Response codes:
        - 200 (OK): Download complete, report is in the response body.
        - 202 (Accepted): Download is in progress. Multiple 202 responses may be
          returned before the final response.
        - 204 (No Content): Log data is not available.
        - 404 (Not Found): URL was already used in a previous request (after 200, 204, or 504).
        - 504 (Gateway Timeout): Runtime is unavailable or timed out.

        :param url: The full URL returned in the create_connection_licensing_report response.
        :return: Dictionary with status information and report content (if available).
          Format: {
            "status_code": int,
            "status": str,  # "complete", "in_progress", "no_content", "not_found", "timeout", or "error"
            "content": bytes | None,
            "text": str | None,
            "message": str,
            "headers": dict
          }
        :raises BoomiAPIError: If an unexpected error occurs.
        """
        request_timeout = self.timeout

        try:
            # Use the session to make the request to the external URL
            # The session already has authentication headers configured
            response = self.session.request(
                method="GET",
                url=url,
                timeout=request_timeout,
            )

            status_code = response.status_code
            content_type = response.headers.get("Content-Type", "")

            # Handle 200: Download complete
            if status_code == 200:
                result = {
                    "status_code": 200,
                    "status": "complete",
                    "message": "Download is complete. Report is in the response body.",
                    "headers": dict(response.headers),
                }
                if content_type.startswith("application/json"):
                    result["content"] = response.content
                    result["text"] = response.text
                    result["data"] = response.json()
                else:
                    result["content"] = response.content
                    result["text"] = response.text
                return result

            # Handle 202: Download in progress
            elif status_code == 202:
                return {
                    "status_code": 202,
                    "status": "in_progress",
                    "message": "Download is in progress. You may receive multiple 202 responses before the final response.",
                    "content": None,
                    "text": None,
                    "headers": dict(response.headers),
                }

            # Handle 204: No content available
            elif status_code == 204:
                return {
                    "status_code": 204,
                    "status": "no_content",
                    "message": "Log data is not available.",
                    "content": None,
                    "text": None,
                    "headers": dict(response.headers),
                }

            # Handle 404: URL already used (after 200, 204, or 504)
            elif status_code == 404:
                return {
                    "status_code": 404,
                    "status": "not_found",
                    "message": "URL was already used in a previous request. The download URL is valid for a single request only.",
                    "content": None,
                    "text": None,
                    "headers": dict(response.headers),
                }

            # Handle 504: Gateway timeout / Runtime unavailable
            elif status_code == 504:
                return {
                    "status_code": 504,
                    "status": "timeout",
                    "message": "Runtime is unavailable. It might have timed out.",
                    "content": None,
                    "text": None,
                    "headers": dict(response.headers),
                }

            # Handle unexpected status codes
            else:
                error_msg = f"Unexpected status code when retrieving connection licensing report: HTTP {status_code}"
                try:
                    error_detail = response.json()
                    if isinstance(error_detail, dict) and "message" in error_detail:
                        error_msg += f" - {error_detail['message']}"
                    else:
                        error_msg += f" - {error_detail}"
                except (ValueError, KeyError):
                    if response.text:
                        error_msg += f" - {response.text}"

                raise BoomiAPIError(
                    error_msg,
                    status_code=status_code,
                    response_body=response.text,
                )

        except BoomiAPIError:
            # Re-raise BoomiAPIError as-is
            raise
        except requests.exceptions.Timeout:
            raise BoomiAPIError(f"Request timeout after {request_timeout} seconds")
        except requests.exceptions.ConnectionError as e:
            raise BoomiAPIError(f"Connection error: {e}")
        except requests.exceptions.RequestException as e:
            raise BoomiAPIError(f"Request failed: {e}")
        except Exception as e:
            raise BoomiAPIError(f"Unexpected error: {e}")

    def _download_url_with_retries(
        self,
        url: str,
        output_path: str,
        max_retries: Optional[int] = None,
        backoff_factor: Optional[float] = None,
        chunk_size: int = 8192,
        retry_statuses: Optional[List[int]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> str:
        """
        Download a URL to disk with retry logic and Retry-After support.

        :param url: Full URL to download.
        :param output_path: Path on disk to save the file.
        :param max_retries: Optional override for retry attempts.
        :param backoff_factor: Optional override for backoff factor.
        :param chunk_size: Chunk size for streaming download.
        :param retry_statuses: HTTP status codes to treat as retryable.
        :param headers: Optional request headers (merged with session headers).
        :return: The output path used for the download.
        """
        retry_limit = max_retries or self.max_retries
        backoff = backoff_factor or self.backoff_factor
        retries = 0
        request_timeout = self.timeout
        retryable_statuses = retry_statuses or [202, 401, 429, 503, 504]

        # Ensure parent directories exist
        directory_path = os.path.dirname(output_path)
        if directory_path:
            os.makedirs(directory_path, exist_ok=True)

        request_headers: Dict[str, str] = {}
        if headers:
            request_headers.update(headers)

        while retries <= retry_limit:
            try:
                response = self.session.get(
                    url, headers=request_headers, stream=True, timeout=request_timeout
                )

                if response.status_code in retryable_statuses:
                    if retries >= retry_limit:
                        error_msg = (
                            f"Download failed: HTTP {response.status_code} "
                            f"(max retries exceeded)"
                        )
                        try:
                            error_detail = response.json()
                            if (
                                isinstance(error_detail, dict)
                                and "message" in error_detail
                            ):
                                error_msg += f" - {error_detail['message']}"
                            else:
                                error_msg += f" - {error_detail}"
                        except (ValueError, KeyError):
                            error_msg += f" - {response.text}"
                        raise BoomiAPIError(
                            error_msg,
                            status_code=response.status_code,
                            response_body=response.text,
                        )

                    retry_after = response.headers.get("Retry-After")
                    if retry_after:
                        try:
                            sleep_time = float(retry_after)
                        except (ValueError, TypeError):
                            sleep_time = backoff
                    else:
                        sleep_time = backoff

                    retries += 1
                    logger.warning(
                        f"Download rate limit/status {response.status_code}. "
                        f"Retrying in {sleep_time:.2f} seconds... "
                        f"(Attempt {retries}/{retry_limit})"
                    )
                    time.sleep(sleep_time)
                    backoff *= 2
                    continue

                if not response.ok:
                    error_msg = f"Download error: HTTP {response.status_code}"
                    try:
                        error_detail = response.json()
                        if isinstance(error_detail, dict) and "message" in error_detail:
                            error_msg += f" - {error_detail['message']}"
                        else:
                            error_msg += f" - {error_detail}"
                    except (ValueError, KeyError):
                        error_msg += f" - {response.text}"
                    raise BoomiAPIError(
                        error_msg,
                        status_code=response.status_code,
                        response_body=response.text,
                    )

                with open(output_path, "wb") as handle:
                    for chunk in response.iter_content(chunk_size=chunk_size):
                        if chunk:
                            handle.write(chunk)

                return output_path

            except BoomiAPIError:
                raise
            except requests.exceptions.Timeout:
                raise BoomiAPIError(f"Download timeout after {request_timeout} seconds")
            except requests.exceptions.ConnectionError as e:
                raise BoomiAPIError(f"Download connection error: {e}")
            except requests.exceptions.RequestException as e:
                retries += 1
                if retries > retry_limit:
                    logger.error(
                        f"Maximum retries ({retry_limit}) exceeded during download. "
                        f"Last error: {e}"
                    )
                    raise BoomiAPIError(
                        f"Download failed after {retry_limit} retries: {e}"
                    )

                sleep_time = backoff
                logger.warning(
                    f"Download error: {e}. Retrying in {sleep_time:.2f} seconds... "
                    f"(Attempt {retries}/{retry_limit})"
                )
                time.sleep(sleep_time)
                backoff *= 2
            except Exception as e:
                raise BoomiAPIError(f"Unexpected download error: {e}")

        raise BoomiAPIError("Unexpected error in download retry loop")

    def download_connection_licensing_report(
        self,
        filters: Optional[Dict[str, Any]] = None,
        delay: float = 5.0,
        max_attempts: Optional[int] = None,
    ) -> Any:
        """
        Downloads a connection licensing report by managing the creation and polling process.

        This method simplifies the download process by:
        1. Creating a connection licensing report request
        2. Polling the download URL until the report is ready (200) or a terminal
           state is reached (204, 404, 504)

        The method will automatically retry polling when it receives a 202 (in progress)
        response, waiting the specified delay between attempts.

        :param filters: Optional dictionary of filter criteria for the report.
        :param delay: Delay in seconds between polling attempts when status is 202 or after 204.
          Defaults to 5.0 seconds.
        :param max_attempts: Maximum number of polling attempts. If None, polling continues
          until a terminal state is reached. Defaults to None.
        :return: Dictionary with status information and report content (if available).
          Same format as get_connection_licensing_report return value.
        :raises BoomiAPIError: If the request fails or max_attempts is exceeded.
        """
        # Step 1: Create the connection licensing report request
        create_response = self.create_connection_licensing_report(filters)

        # Extract the URL from the response
        if not isinstance(create_response, dict) or "url" not in create_response:
            raise BoomiAPIError(
                "Invalid response from create_connection_licensing_report: missing 'url' field"
            )

        download_url = create_response["url"]

        # Step 2: Poll for the report until terminal state is reached
        attempts = 0
        last_status_code = None

        while True:
            attempts += 1

            # Check max_attempts if specified
            if max_attempts is not None and attempts > max_attempts:
                raise BoomiAPIError(
                    f"Maximum polling attempts ({max_attempts}) exceeded. "
                    f"Last status code: {last_status_code}"
                )

            # Get the report status
            result = self.get_connection_licensing_report(download_url)
            status_code = result["status_code"]
            last_status_code = status_code

            # Terminal states: stop polling and return
            if status_code == 200:
                # Success - report is ready
                return result
            elif status_code == 204:
                # No content available - terminal state
                # Wait before returning (as per requirements)
                time.sleep(delay)
                return result
            elif status_code == 404:
                # URL already used - terminal state
                return result
            elif status_code == 504:
                # Runtime unavailable - terminal state
                return result

            # Non-terminal state: 202 (in progress) - wait and retry
            elif status_code == 202:
                time.sleep(delay)
                continue

            # Unexpected status code - raise error
            else:
                raise BoomiAPIError(
                    f"Unexpected status code during polling: {status_code}. "
                    f"Result: {result}"
                )

    def query_custom_tracked_fields(
        self, filters: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Queries for CustomTrackedField objects using optional filter criteria.
        :param filters: Dictionary of query fields (e.g., {"name": "MyCustomTrackedField"}).
        :return: JSON response containing matched CustomTrackedField objects.
        """
        return self._request("POST", "CustomTrackedField/query", json=filters or {})

    def query_more_custom_tracked_fields(self, token: str) -> Any:
        """
        Retrieves the next page of CustomTrackedField results using a continuation token.
        :param token: Pagination token returned from a previous CustomTrackedField query.
        :return: JSON response with the next set of CustomTrackedField results.
        """
        headers = {"Content-Type": "text/plain"}
        return self._request(
            "POST", "CustomTrackedField/queryMore", data=token, headers=headers
        )

    def query_event(self, filters: Optional[Dict[str, Any]] = None) -> Any:
        """
        Queries for Event objects using optional filter criteria.
        :param filters: Dictionary of query fields (e.g., {"name": "MyEvent"}).
        :return: JSON response containing matched Event objects.
        """
        return self._request("POST", "Event/query", json=filters or {})

    def query_more_events(self, token: str) -> Any:
        """
        Retrieves the next page of Event results using a continuation token.
        :param token: Pagination token returned from a previous Event query.
        :return: JSON response with the next set of Event results.
        """
        headers = {"Content-Type": "text/plain"}
        return self._request("POST", "Event/queryMore", data=token, headers=headers)

    def get_assignable_roles(self) -> Any:
        """
        Retrieves the assignable roles for the current account.
        :return: JSON response containing the assignable roles.
        """
        return self._request("GET", "AssignableRole")

    def create_role(
        self,
        name: str,
        privileges: List[str],
        account_id: Optional[str] = None,
        description: Optional[str] = None,
        parent_id: Optional[str] = None,
    ) -> Any:
        """
        Creates a new role.

        :param name: The name of the role (required).
        :param privileges: List of privilege names (required). Each privilege will be
          added to the Privileges.Privilege array.
        :param account_id: The ID of the account. If not provided, uses the account_id
          configured in the client.
        :param description: Optional description of the role.
        :param parent_id: Optional parent role ID.
        :return: JSON response containing the created role.
        """
        # Build privileges structure
        privilege_list = [{"name": privilege} for privilege in privileges]
        privileges_obj = {"Privilege": privilege_list}

        # Build payload
        payload: Dict[str, Any] = {
            "name": name,
            "Privileges": privileges_obj,
        }

        # Add optional fields
        account_id_to_use = account_id or self.account_id
        if account_id_to_use:
            payload["accountId"] = account_id_to_use

        if description is not None:
            payload["Description"] = description

        if parent_id is not None:
            payload["parentId"] = parent_id

        return self._request("POST", "Role", json=payload)

    def get_role(self, role_id: str) -> Any:
        """
        Retrieves a role.
        :param role_id: The ID of the role to retrieve.
        :return: JSON response containing the role.
        """
        return self._request("GET", f"Role/{role_id}")

    def modify_role(
        self,
        role_id: str,
        name: Optional[str] = None,
        privileges: Optional[List[str]] = None,
        account_id: Optional[str] = None,
        description: Optional[str] = None,
        parent_id: Optional[str] = None,
    ) -> Any:
        """
        Modifies a role.
        :param role_id: The ID of the role to modify.
        :param name: The name of the role.
        :param privileges: List of privilege names.
        :param account_id: The ID of the account. If not provided, uses the account_id configured in the client.
        :param description: The description of the role.
        :param parent_id: The ID of the parent role.
        :return: JSON response containing the modified role.
        """
        payload: Dict[str, Any] = {}

        # Add optional fields if provided
        if name is not None:
            payload["name"] = name

        if privileges is not None:
            privilege_list = [{"name": privilege} for privilege in privileges]
            payload["Privileges"] = {"Privilege": privilege_list}

        account_id_to_use = account_id or self.account_id
        if account_id_to_use:
            payload["accountId"] = account_id_to_use

        if description is not None:
            payload["Description"] = description

        if parent_id is not None:
            payload["parentId"] = parent_id

        return self._request("POST", f"Role/{role_id}", json=payload)

    def delete_role(self, role_id: str) -> Any:
        """
        Deletes a role.
        :param role_id: The ID of the role to delete.
        :return: JSON response containing the deleted role.
        """
        return self._request("DELETE", f"Role/{role_id}")

    def query_role(self, filters: Optional[Dict[str, Any]] = None) -> Any:
        """
        Queries for Role objects using optional filter criteria.
        :param filters: Dictionary of query fields (e.g., {"name": "MyRole"}).
        :return: JSON response containing matched Role objects.
        """
        return self._request("POST", "Role/query", json=filters or {})

    def query_more_roles(self, token: str) -> Any:
        """
        Retrieves the next page of Role results using a continuation token.
        :param token: Pagination token returned from a previous Role query.
        :return: JSON response with the next set of Role results.
        """
        headers = {"Content-Type": "text/plain"}
        return self._request("POST", "Role/queryMore", data=token, headers=headers)

    def get_role_bulk(self, role_ids: List[str]) -> Any:
        """
        Retrieves the roles for the current account.
        :param role_ids: The IDs of the roles to retrieve.
        :return: JSON response containing the roles.
        """
        payload = {
            "type": "GET",
            "request": [{"id": role_id} for role_id in role_ids],
        }
        return self._request("POST", "Role/bulk", json=payload)

    def get_environment(self, environment_id: str) -> Any:
        """
        Retrieves an environment.
        :param environment_id: The ID of the environment to retrieve.
        :return: JSON response containing the environment.
        """
        return self._request("GET", f"Environment/{environment_id}")

    def get_environment_bulk(self, environment_ids: List[str]) -> Any:
        """
        Retrieves the environments for the current account.
        :param environment_ids: The IDs of the environments to retrieve.
        :return: JSON response containing the environments.
        """
        payload = {
            "type": "GET",
            "request": [{"id": environment_id} for environment_id in environment_ids],
        }
        return self._request("POST", "Environment/bulk", json=payload)

    def query_environments(self, filters: Optional[Dict[str, Any]] = None) -> Any:
        """
        Queries for Environment objects using optional filter criteria.
        :param filters: Dictionary of query fields (e.g., {"name": "MyEnvironment"}).
        :return: JSON response containing matched Environment objects.
        """
        return self._request("POST", "Environment/query", json=filters or {})

    def query_more_environments(self, token: str) -> Any:
        """
        Retrieves the next page of Environment results using a continuation token.
        :param token: Pagination token returned from a previous Environment query.
        :return: JSON response with the next set of Environment results.
        """
        headers = {"Content-Type": "text/plain"}
        return self._request(
            "POST", "Environment/queryMore", data=token, headers=headers
        )

    def create_environment(
        self, name: str, classification: Optional[str] = None
    ) -> Any:
        """
        Creates an environment.
        :param name: The name of the environment.
        :param classification: The classification of the environment.
        :return: JSON response containing the created environment.
        """
        payload = {
            "name": name,
            "classification": classification,
        }
        return self._request("POST", "Environment", json=payload)

    def get_packaged_component_manifest(self, package_id: str) -> Any:
        """
        Retrieves the manifest for a packaged component.
        :param package_id: The ID of the packaged component to retrieve the manifest for.
        :return: JSON response containing the manifest.
        """
        return self._request("GET", f"PackagedComponentManifest/{package_id}")

    def get_packaged_component_manifest_bulk(self, package_ids: List[str]) -> Any:
        """
        Retrieves the manifests for a list of packaged components.
        :param package_ids: The IDs of the packaged components to retrieve the manifests for.
        :return: JSON response containing the manifests.
        """
        payload = {
            "type": "GET",
            "request": [{"id": package_id} for package_id in package_ids],
        }
        return self._request("POST", "PackagedComponentManifest/bulk", json=payload)

    def create_branch(
        self, parent_branch_id: str, branch_name: str, package_id: Optional[str] = None
    ) -> Any:
        """
        Creates a branch.

        According to the Boomi Platform Branch API, new branches remain with
        ``ready`` set to ``false`` until the creation stage completes. Branches
        can be created either directly from another branch (default) or from a
        packaged component or deployment by supplying the packaged component or
        deployment ID as ``packageId``.

        :param parent_branch_id: The ID of the branch to branch from.
        :param branch_name: The name of the branch to create.
        :param package_id: Optional packaged component or deployment ID to
            create the branch from (maps to API field packageId).
        :return: JSON response containing the created branch.
        """
        payload: Dict[str, Any] = {
            "parentBranchId": parent_branch_id,
            "name": branch_name,
        }

        if package_id:
            payload["packageId"] = package_id

        return self._request("POST", "Branch", json=payload)

    def get_branch(self, branch_id: str) -> Any:
        """
        Retrieves a branch.
        :param branch_id: The ID of the branch to retrieve.
        :return: JSON response containing the branch.
        """
        return self._request("GET", f"Branch/{branch_id}")

    def update_branch(
        self,
        branch_id: str,
        name: Optional[str] = None,
        description: Optional[str] = None,
        ready: Optional[bool] = None,
    ) -> Any:
        """
        Modifies an existing branch per the Branch Update API.

        The Branch update operation allows changing branch metadata and marking
        it ready once creation is complete.

        :param branch_id: The ID of the branch to modify.
        :param name: Optional new branch name.
        :param description: Optional branch description.
        :param ready: Optional readiness flag (set to True when the branch is ready).
        :return: JSON response containing the modified branch.
        """
        payload: Dict[str, Any] = {}

        if name is not None:
            payload["name"] = name
        if description is not None:
            payload["description"] = description
        if ready is not None:
            payload["ready"] = ready

        return self._request("PUT", f"Branch/{branch_id}", json=payload)

    def delete_branch(self, branch_id: str) -> Any:
        """
        Deletes a branch.
        :param branch_id: The ID of the branch to delete.
        :return: JSON response containing the deleted branch.
        """
        return self._request("DELETE", f"Branch/{branch_id}")

    def get_branch_bulk(self, branch_ids: List[str]) -> Any:
        """
        Retrieves the branches for the current account.
        :param branch_ids: The IDs of the branches to retrieve.
        :return: JSON response containing the branches.
        """
        payload = {
            "type": "GET",
            "request": [{"id": branch_id} for branch_id in branch_ids],
        }
        return self._request("POST", "Branch/bulk", json=payload)

    def query_branches(self, filters: Optional[Dict[str, Any]] = None) -> Any:
        """
        Queries for Branch objects using optional filter criteria.
        :param filters: Dictionary of query fields (e.g., {"name": "MyBranch"}).
        :return: JSON response containing matched Branch objects.
        """
        return self._request("POST", "Branch/query", json=filters or {})

    def query_more_branches(self, token: str) -> Any:
        """
        Retrieves the next page of Branch results using a continuation token.
        :param token: Pagination token returned from a previous Branch query.
        :return: JSON response with the next set of Branch results.
        """
        headers = {"Content-Type": "text/plain"}
        return self._request("POST", "Branch/queryMore", data=token, headers=headers)

    # -------------------------------------------------------------------------
    # Execution artifact and connector APIs
    # -------------------------------------------------------------------------

    def query_execution_record(self, execution_id: str) -> Any:
        """
        Queries ExecutionRecord objects for a specific execution ID.

        :param execution_id: The execution ID to query.
        :return: JSON response containing matching execution records.
        """
        payload = {
            "QueryFilter": {
                "expression": {
                    "operator": "and",
                    "nestedExpression": [
                        {
                            "argument": [execution_id],
                            "operator": "EQUALS",
                            "property": "executionId",
                        }
                    ],
                }
            }
        }
        return self._request("POST", "ExecutionRecord/query", json=payload)

    def query_more_execution_record(self, query_token: str) -> Any:
        """
        Retrieves the next page of ExecutionRecord results.

        :param query_token: Pagination token from a previous ExecutionRecord query.
        :return: JSON response containing the next page.
        """
        headers = {"Content-Type": "text/plain"}
        return self._request(
            "POST", "ExecutionRecord/queryMore", data=query_token, headers=headers
        )

    def create_execution_artifacts_request(self, execution_id: str) -> Any:
        """
        Creates an execution artifacts request for a given execution ID.

        The response contains a download URL for the artifacts zip.

        :param execution_id: The execution ID to gather artifacts for.
        :return: JSON response containing the download URL and metadata.
        """
        payload = {"executionId": execution_id}
        return self._request("POST", "ExecutionArtifacts", json=payload)

    def create_process_log_request(
        self, execution_id: str, log_level: str = "INFO"
    ) -> Any:
        """
        Requests a process log download URL for a given execution ID.

        :param execution_id: The execution ID.
        :param log_level: Log level to request (e.g., INFO, ALL).
        :return: JSON response containing the download URL and metadata.
        """
        payload = {"executionId": execution_id, "logLevel": log_level}
        return self._request("POST", "ProcessLog", json=payload)

    def query_execution_connector(self, execution_id: str) -> Any:
        """
        Queries ExecutionConnector records for a given execution ID.

        :param execution_id: The execution ID to filter by.
        :return: JSON response containing matched connectors.
        """
        payload = {
            "QueryFilter": {
                "expression": {
                    "argument": [execution_id],
                    "operator": "EQUALS",
                    "property": "executionId",
                }
            }
        }
        return self._request("POST", "ExecutionConnector/query", json=payload)

    def query_more_execution_connector(self, query_token: str) -> Any:
        """
        Retrieves the next page of ExecutionConnector results.

        :param query_token: Pagination token from a previous ExecutionConnector query.
        :return: JSON response containing the next page.
        """
        headers = {"Content-Type": "text/plain"}
        return self._request(
            "POST", "ExecutionConnector/queryMore", data=query_token, headers=headers
        )

    def query_generic_connector_record(
        self, execution_id: str, execution_connector_id: str
    ) -> Any:
        """
        Queries GenericConnectorRecord objects for a given execution and connector.

        :param execution_id: Execution ID to filter by.
        :param execution_connector_id: Execution connector ID to filter by.
        :return: JSON response containing matched records.
        """
        payload = {
            "QueryFilter": {
                "expression": {
                    "operator": "and",
                    "nestedExpression": [
                        {
                            "argument": [execution_id],
                            "operator": "EQUALS",
                            "property": "executionId",
                        },
                        {
                            "argument": [execution_connector_id],
                            "operator": "EQUALS",
                            "property": "executionConnectorId",
                        },
                    ],
                }
            }
        }
        return self._request("POST", "GenericConnectorRecord/query", json=payload)

    def query_more_generic_connector_record(self, query_token: str) -> Any:
        """
        Retrieves the next page of GenericConnectorRecord results.

        :param query_token: Pagination token from a previous GenericConnectorRecord query.
        :return: JSON response containing the next page.
        """
        headers = {"Content-Type": "text/plain"}
        return self._request(
            "POST",
            "GenericConnectorRecord/queryMore",
            data=query_token,
            headers=headers,
        )

    def get_connector_document_url(self, generic_connector_record_id: str) -> Any:
        """
        Requests a connector document download URL for a given generic connector record.

        :param generic_connector_record_id: The record ID to retrieve the document for.
        :return: JSON response containing the download URL.
        """
        payload = {"genericConnectorRecordId": generic_connector_record_id}
        return self._request("POST", "ConnectorDocument", json=payload)

    def download_to_path(
        self,
        url: str,
        output_path: str,
        max_retries: Optional[int] = None,
        backoff_factor: Optional[float] = None,
        chunk_size: int = 8192,
        retry_statuses: Optional[List[int]] = None,
        headers: Optional[Dict[str, str]] = None,
    ) -> str:
        """
        Downloads the content at the given URL to the specified path with retry logic.

        :param url: URL to download.
        :param output_path: Path on disk to save the file.
        :param max_retries: Optional override for retry attempts.
        :param backoff_factor: Optional override for backoff factor.
        :param chunk_size: Chunk size for streaming.
        :param retry_statuses: Optional list of HTTP status codes to retry.
        :param headers: Optional headers to include for the request.
        :return: The output path used for the download.
        """
        return self._download_url_with_retries(
            url=url,
            output_path=output_path,
            max_retries=max_retries,
            backoff_factor=backoff_factor,
            chunk_size=chunk_size,
            retry_statuses=retry_statuses,
            headers=headers,
        )
