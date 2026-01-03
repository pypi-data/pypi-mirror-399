#!/usr/bin/env python3
#
# PyBoomi Platform - Utilities Tests
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

"""
Tests for the utilities module.
"""

__author__ = "Robert Little"
__copyright__ = "Copyright 2025, Robert Little"
__license__ = "Apache 2.0"
__version__ = "0.1.0"

from pyboomi_platform.utils import build_query_filter


def test_build_query_filter_empty_dict():
    """Test that build_query_filter returns empty dict for empty input."""
    result = build_query_filter({})
    assert result == {}


def test_build_query_filter_single_filter():
    """Test that build_query_filter creates single expression for one filter."""
    filters = {"name": "TestFolder"}
    result = build_query_filter(filters)

    assert "QueryFilter" in result
    assert "expression" in result["QueryFilter"]
    assert result["QueryFilter"]["expression"]["property"] == "name"
    assert result["QueryFilter"]["expression"]["operator"] == "EQUALS"
    assert result["QueryFilter"]["expression"]["argument"] == ["TestFolder"]


def test_build_query_filter_multiple_filters():
    """Test that build_query_filter creates nested expression for multiple filters."""
    filters = {"name": "TestFolder", "type": "folder"}
    result = build_query_filter(filters)

    assert "QueryFilter" in result
    assert "expression" in result["QueryFilter"]
    assert result["QueryFilter"]["expression"]["operator"] == "and"
    assert "nestedExpression" in result["QueryFilter"]["expression"]
    assert len(result["QueryFilter"]["expression"]["nestedExpression"]) == 2

    # Check first expression
    expr1 = result["QueryFilter"]["expression"]["nestedExpression"][0]
    assert expr1["property"] == "name"
    assert expr1["operator"] == "EQUALS"
    assert expr1["argument"] == ["TestFolder"]

    # Check second expression
    expr2 = result["QueryFilter"]["expression"]["nestedExpression"][1]
    assert expr2["property"] == "type"
    assert expr2["operator"] == "EQUALS"
    assert expr2["argument"] == ["folder"]


def test_build_query_filter_with_list_argument():
    """Test that build_query_filter handles list arguments correctly."""
    filters = {"id": ["id1", "id2", "id3"]}
    result = build_query_filter(filters)

    assert "QueryFilter" in result
    assert "expression" in result["QueryFilter"]
    assert result["QueryFilter"]["expression"]["property"] == "id"
    assert result["QueryFilter"]["expression"]["operator"] == "EQUALS"
    assert result["QueryFilter"]["expression"]["argument"] == ["id1", "id2", "id3"]


def test_build_query_filter_mixed_single_and_list():
    """Test that build_query_filter handles mix of single values and lists."""
    filters = {"name": "Test", "ids": ["id1", "id2"]}
    result = build_query_filter(filters)

    assert "QueryFilter" in result
    assert "expression" in result["QueryFilter"]
    assert result["QueryFilter"]["expression"]["operator"] == "and"
    assert len(result["QueryFilter"]["expression"]["nestedExpression"]) == 2

    # Check name filter (single value)
    name_expr = result["QueryFilter"]["expression"]["nestedExpression"][0]
    assert name_expr["property"] == "name"
    assert name_expr["argument"] == ["Test"]

    # Check ids filter (list value)
    ids_expr = result["QueryFilter"]["expression"]["nestedExpression"][1]
    assert ids_expr["property"] == "ids"
    assert ids_expr["argument"] == ["id1", "id2"]


def test_build_query_filter_three_filters():
    """Test that build_query_filter handles three or more filters."""
    filters = {"name": "Test", "type": "folder", "deleted": "false"}
    result = build_query_filter(filters)

    assert "QueryFilter" in result
    assert "expression" in result["QueryFilter"]
    assert result["QueryFilter"]["expression"]["operator"] == "and"
    assert len(result["QueryFilter"]["expression"]["nestedExpression"]) == 3

    properties = [
        expr["property"]
        for expr in result["QueryFilter"]["expression"]["nestedExpression"]
    ]
    assert "name" in properties
    assert "type" in properties
    assert "deleted" in properties
