#!/usr/bin/env python3
#
# PyBoomi Platform - Configuration Tests
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

"""Tests for configuration management functionality."""

import os
import tempfile
import unittest
from unittest.mock import patch

from pyboomi_platform import BoomiPlatformClient
from pyboomi_platform.config import Config


class TestConfig(unittest.TestCase):
    """Test configuration loading and management."""

    def test_config_with_direct_parameters(self):
        """Test client initialization with direct parameters."""
        client = BoomiPlatformClient(
            account_id="test-account",
            username="test@example.com",
            api_token="test-token",
        )

        self.assertEqual(client.account_id, "test-account")
        self.assertEqual(client.username, "test@example.com")
        self.assertEqual(client.api_token, "test-token")
        self.assertIsNotNone(client.session)

    @patch.dict(
        os.environ,
        {
            "BOOMI_ACCOUNT_ID": "env-account",
            "BOOMI_USERNAME": "env@example.com",
            "BOOMI_API_TOKEN": "env-token",
        },
    )
    def test_config_with_environment_variables(self):
        """Test client initialization with environment variables."""
        client = BoomiPlatformClient()

        self.assertEqual(client.account_id, "env-account")
        self.assertEqual(client.username, "env@example.com")
        self.assertEqual(client.api_token, "env-token")

    @patch.dict(
        os.environ,
        {
            "BOOMI_ACCOUNT_ID": "env-account",
            "BOOMI_CLIENT_ID": "env@example.com",  # Test alternative naming
            "BOOMI_CLIENT_SECRET": "env-token",  # Test alternative naming
        },
    )
    def test_config_with_alternative_env_names(self):
        """Test client initialization with alternative environment variable names."""
        client = BoomiPlatformClient()

        self.assertEqual(client.account_id, "env-account")
        self.assertEqual(client.username, "env@example.com")
        self.assertEqual(client.api_token, "env-token")

    @patch.dict(
        os.environ,
        {
            "BOOMIACCT": "boomiacct-account",
            "BOOMI_USERNAME": "env@example.com",
            "BOOMI_API_TOKEN": "env-token",
        },
    )
    def test_config_with_boomiacct_env_var(self):
        """Test client initialization with BOOMIACCT environment variable."""
        client = BoomiPlatformClient()

        self.assertEqual(client.account_id, "boomiacct-account")
        self.assertEqual(client.username, "env@example.com")
        self.assertEqual(client.api_token, "env-token")

    @patch.dict(os.environ, {}, clear=True)
    def test_config_yaml_loading(self):
        """Test YAML configuration file loading."""
        yaml_content = """
boomi:
  account_id: "yaml-account"
  username: "yaml@example.com"
  api_token: "yaml-token"
  timeout: 45
  max_retries: 5
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            f.flush()

            try:
                config = Config(f.name)
                boomi_config = config.get_boomi_config()

                self.assertEqual(boomi_config["account_id"], "yaml-account")
                self.assertEqual(boomi_config["username"], "yaml@example.com")
                self.assertEqual(boomi_config["api_token"], "yaml-token")
                self.assertEqual(boomi_config["timeout"], 45)
                self.assertEqual(boomi_config["max_retries"], 5)
            finally:
                os.unlink(f.name)

    def test_config_priority_env_over_yaml(self):
        """Test that environment variables take precedence over YAML config."""
        yaml_content = """
boomi:
  account_id: "yaml-account"
  username: "yaml@example.com"
  api_token: "yaml-token"
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            f.flush()

            try:
                with patch.dict(
                    os.environ,
                    {
                        "BOOMI_ACCOUNT_ID": "env-account",
                        "BOOMI_USERNAME": "env@example.com",
                    },
                ):
                    config = Config(f.name)
                    boomi_config = config.get_boomi_config()

                    # Environment variables should override YAML
                    self.assertEqual(boomi_config["account_id"], "env-account")
                    self.assertEqual(boomi_config["username"], "env@example.com")
                    # YAML value should be used when env var not set
                    self.assertEqual(boomi_config["api_token"], "yaml-token")
            finally:
                os.unlink(f.name)

    @patch.dict(os.environ, {}, clear=True)
    def test_missing_required_parameters(self):
        """Test that missing required parameters raise ValueError."""
        with self.assertRaises(ValueError):
            BoomiPlatformClient(
                account_id="test", username="test@example.com"
            )  # Missing api_token

        with self.assertRaises(ValueError):
            BoomiPlatformClient(
                account_id="test", api_token="token"
            )  # Missing username

        with self.assertRaises(ValueError):
            BoomiPlatformClient(
                username="test@example.com", api_token="token"
            )  # Missing account_id

    @patch.dict(os.environ, {}, clear=True)
    @patch("pyboomi_platform.config.YAML_AVAILABLE", False)
    def test_config_without_yaml(self):
        """Test config loading when PyYAML is not available."""
        # Reload the module to get the updated YAML_AVAILABLE value
        import importlib

        import pyboomi_platform.config

        importlib.reload(pyboomi_platform.config)

        config = pyboomi_platform.config.Config()
        boomi_config = config.get_boomi_config()

        # Should return empty/default values when YAML not available
        assert boomi_config["account_id"] is None
        assert boomi_config["username"] is None
        assert boomi_config["api_token"] is None

    @patch.dict(os.environ, {}, clear=True)
    def test_config_file_not_found(self):
        """Test config loading when no config file exists."""
        config = Config("nonexistent-file.yaml")
        boomi_config = config.get_boomi_config()

        # Should return empty/default values
        assert boomi_config["account_id"] is None
        assert boomi_config["username"] is None
        assert boomi_config["api_token"] is None
        assert boomi_config["timeout"] == 30
        assert boomi_config["max_retries"] == 3

    @patch.dict(os.environ, {}, clear=True)
    def test_config_invalid_yaml(self):
        """Test config loading with invalid YAML file."""
        invalid_yaml = "invalid: yaml: content: ["

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(invalid_yaml)
            f.flush()

            try:
                config = Config(f.name)
                boomi_config = config.get_boomi_config()

                # Should handle error gracefully and return empty/default values
                assert boomi_config["account_id"] is None
            finally:
                os.unlink(f.name)

    @patch.dict(os.environ, {}, clear=True)
    def test_config_default_paths(self):
        """Test that config searches default paths."""
        yaml_content = """
boomi:
  account_id: "default-account"
  username: "default@example.com"
  api_token: "default-token"
"""

        # Test with explicit config path
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            f.flush()
            config_path = f.name

            try:
                config = Config(config_path)
                boomi_config = config.get_boomi_config()
                assert boomi_config["account_id"] == "default-account"
            finally:
                os.unlink(config_path)

    @patch.dict(os.environ, {}, clear=True)
    def test_get_config_function(self):
        """Test the get_config convenience function."""
        from pyboomi_platform.config import Config, get_config

        config = get_config()
        assert isinstance(config, Config)

        # Test with config path
        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write("boomi:\n  account_id: test")
            f.flush()

            try:
                config = get_config(f.name)
                assert isinstance(config, Config)
            finally:
                os.unlink(f.name)

    @patch.dict(
        os.environ,
        {
            "BOOMI_TIMEOUT": "60",
            "BOOMI_MAX_RETRIES": "5",
            "BOOMI_BACKOFF_FACTOR": "2.0",
        },
    )
    def test_config_numeric_env_vars(self):
        """Test that numeric environment variables are parsed correctly."""
        config = Config()
        boomi_config = config.get_boomi_config()

        assert boomi_config["timeout"] == 60
        assert boomi_config["max_retries"] == 5
        assert boomi_config["backoff_factor"] == 2.0

    @patch.dict(os.environ, {}, clear=True)
    def test_config_yaml_with_client_id_secret(self):
        """Test YAML config with client_id/client_secret naming."""
        yaml_content = """
boomi:
  account_id: "yaml-account"
  client_id: "yaml@example.com"
  client_secret: "yaml-token"
"""

        with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
            f.write(yaml_content)
            f.flush()

            try:
                config = Config(f.name)
                boomi_config = config.get_boomi_config()

                assert boomi_config["account_id"] == "yaml-account"
                assert boomi_config["username"] == "yaml@example.com"
                assert boomi_config["api_token"] == "yaml-token"
            finally:
                os.unlink(f.name)


if __name__ == "__main__":
    unittest.main()
