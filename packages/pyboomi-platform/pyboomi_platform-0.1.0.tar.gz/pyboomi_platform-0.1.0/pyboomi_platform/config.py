#!/usr/bin/env python3
#
# PyBoomi Platform - Configuration Module
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
Configuration loader for PyBoomi Platform SDK.

This module handles loading configuration from YAML files and environment variables,
with environment variables taking precedence over config file values.
"""

__author__ = "Robert Little"
__copyright__ = "Copyright 2025, Robert Little"
__license__ = "Apache 2.0"
__version__ = "0.1.0"

import os
from pathlib import Path
from typing import Any, Dict, Optional

try:
    import yaml

    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


class Config:
    """Configuration manager for PyBoomi Platform SDK."""

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize configuration loader.

        :param config_path: Path to config.yaml file. If not provided,
                           will look for config.yaml in current directory.
        """
        self.config_data: Dict[str, Any] = {}
        self._load_config(config_path)

    def _load_config(self, config_path: Optional[str] = None) -> None:
        """
        Load configuration from YAML file.

        :param config_path: Path to config file.
        """
        if not YAML_AVAILABLE:
            print("PyYAML not available, using environment variables only")
            self.config_data = {}
            return

        # Default config file locations to check
        default_paths = [
            config_path,
            "config.yaml",
            "pyboomi_config.yaml",
            os.path.expanduser("~/.pyboomi/config.yaml"),
        ]

        config_loaded = False
        for path in default_paths:
            if path and Path(path).exists():
                try:
                    with open(path, "r") as file:
                        self.config_data = yaml.safe_load(file) or {}
                    print(f"✓ Loaded configuration from: {path}")
                    config_loaded = True
                    break
                except Exception as e:
                    print(f"Warning: Failed to load config from {path}: {e}")

        if not config_loaded:
            self.config_data = {}

    def get_boomi_config(self) -> Dict[str, Any]:
        """
        Get Boomi configuration with environment variable overrides.

        :return: Dictionary containing Boomi configuration values.
        """
        boomi_config = self.config_data.get("boomi", {})

        return {
            "username": os.environ.get("BOOMI_USERNAME")
            or os.environ.get("BOOMI_CLIENT_ID")  # Support both names
            or boomi_config.get("username")
            or boomi_config.get("client_id"),
            "api_token": os.environ.get("BOOMI_API_TOKEN")
            or os.environ.get("BOOMI_CLIENT_SECRET")  # Support both names
            or boomi_config.get("api_token")
            or boomi_config.get("client_secret"),
            "account_id": os.environ.get("BOOMI_ACCOUNT_ID")
            or os.environ.get(
                "BOOMIACCT"
            )  # Support standard Boomi environment variable
            or boomi_config.get("account_id"),
            "base_url": os.environ.get("BOOMI_API_BASE_URL")
            or boomi_config.get("base_url", "https://api.boomi.com/api/rest/v1"),
            "timeout": int(
                os.environ.get("BOOMI_TIMEOUT", boomi_config.get("timeout", 30))
            ),
            "max_retries": int(
                os.environ.get("BOOMI_MAX_RETRIES", boomi_config.get("max_retries", 3))
            ),
            "backoff_factor": float(
                os.environ.get(
                    "BOOMI_BACKOFF_FACTOR", boomi_config.get("backoff_factor", 1.5)
                )
            ),
        }


def get_config(config_path: Optional[str] = None) -> Config:
    """
    Get a configuration instance.

    :param config_path: Optional path to config file.
    :return: Config instance.
    """
    return Config(config_path)
