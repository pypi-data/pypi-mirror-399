#!/usr/bin/env python3
#
# PyBoomi Platform - Authentication Module
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
Handles API token-based authentication for the Boomi Platform API using Basic Auth.
"""

__author__ = "Robert Little"
__copyright__ = "Copyright 2025, Robert Little"
__license__ = "Apache 2.0"
__version__ = "0.1.0"

import base64
from typing import Dict


class BoomiAuth:
    """
    Handles API token-based authentication for the Boomi Platform API using Basic Auth.
    """

    def __init__(self, username: str, api_token: str):
        """
        Initialize with Boomi Platform API token credentials.

        :param username: The Boomi username (e.g., user@company.com).
        :param api_token: The Platform API token generated from the Boomi UI.
        """
        # Strip BOOMI_TOKEN. prefix from username if present to avoid duplication
        prefix = "BOOMI_TOKEN."
        self.username = f"{prefix}{username[len(prefix):] if username.startswith(prefix) else username}"
        self.api_token = api_token

    def get_auth_header(self) -> Dict[str, str]:
        """
        Returns the Authorization header for Basic Auth with the token.

        :return: Dictionary containing the Authorization header.
        """
        credentials = f"{self.username}:{self.api_token}"
        encoded_credentials = base64.b64encode(credentials.encode("utf-8")).decode(
            "utf-8"
        )
        return {"Authorization": f"Basic {encoded_credentials}"}
