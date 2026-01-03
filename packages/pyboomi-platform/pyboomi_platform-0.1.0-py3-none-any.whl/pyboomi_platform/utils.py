#!/usr/bin/env python3
#
# PyBoomi Platform - Utilities Module
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
Utility functions for building Boomi API-compatible query filters.
"""

__author__ = "Robert Little"
__copyright__ = "Copyright 2025, Robert Little"
__license__ = "Apache 2.0"
__version__ = "0.1.0"

from typing import Any, Dict


def build_query_filter(filters: Dict[str, Any]) -> Dict[str, Any]:
    """
    Build a Boomi API-compliant QueryFilter structure from a simple key-value dictionary.

    :param filters: Dictionary of filters like {"name": "Shared"}
    :return: Dictionary structured for Boomi API QueryFilter
    """
    if not filters:
        return {}

    expressions = []
    for prop, value in filters.items():
        if isinstance(value, list):
            argument = value
        else:
            argument = [value]

        expressions.append(
            {"property": prop, "operator": "EQUALS", "argument": argument}
        )

    if len(expressions) == 1:
        return {"QueryFilter": {"expression": expressions[0]}}
    else:
        return {
            "QueryFilter": {
                "expression": {"operator": "and", "nestedExpression": expressions}
            }
        }
