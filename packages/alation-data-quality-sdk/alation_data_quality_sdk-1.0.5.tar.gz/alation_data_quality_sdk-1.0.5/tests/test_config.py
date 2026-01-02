"""Tests for the SDK configuration module."""

import os
from unittest.mock import patch

import pytest

from data_quality_sdk.config import SDKConfig
from data_quality_sdk.utils.exceptions import DataQualitySDKError


class TestSDKConfig:
    """Test cases for SDKConfig class."""

    def test_from_env_missing_alation_host(self):
        """Test that missing ALATION_HOST raises an error."""
        with patch.dict(os.environ, {}, clear=True):
            with pytest.raises(
                DataQualitySDKError, match="ALATION_HOST environment variable is required"
            ):
                SDKConfig.from_env()

    def test_from_env_missing_monitor_id(self):
        """Test that missing MONITOR_ID raises an error."""
        with patch.dict(os.environ, {"ALATION_HOST": "https://test.alation.com"}, clear=True):
            with pytest.raises(
                DataQualitySDKError, match="MONITOR_ID environment variable is required"
            ):
                SDKConfig.from_env()

    def test_from_env_missing_client_id(self):
        """Test that missing ALATION_CLIENT_ID raises an error."""
        env_vars = {
            "ALATION_HOST": "https://test.alation.com",
            "MONITOR_ID": "123",
        }
        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(
                DataQualitySDKError, match="ALATION_CLIENT_ID environment variable is required"
            ):
                SDKConfig.from_env()

    def test_from_env_missing_client_secret(self):
        """Test that missing ALATION_CLIENT_SECRET raises an error."""
        env_vars = {
            "ALATION_HOST": "https://test.alation.com",
            "MONITOR_ID": "123",
            "ALATION_CLIENT_ID": "test-client-id",
        }
        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(
                DataQualitySDKError, match="ALATION_CLIENT_SECRET environment variable is required"
            ):
                SDKConfig.from_env()

    def test_from_env_missing_tenant_id(self):
        """Test that missing TENANT_ID raises an error."""
        env_vars = {
            "ALATION_HOST": "https://test.alation.com",
            "MONITOR_ID": "123",
            "ALATION_CLIENT_ID": "test-client-id",
            "ALATION_CLIENT_SECRET": "test-client-secret",
        }
        with patch.dict(os.environ, env_vars, clear=True):
            with pytest.raises(
                DataQualitySDKError, match="TENANT_ID environment variable is required"
            ):
                SDKConfig.from_env()

    def test_from_env_minimal_config(self):
        """Test creating config with minimal required environment variables."""
        env_vars = {
            "ALATION_HOST": "https://test.alation.com",
            "MONITOR_ID": "123",
            "ALATION_CLIENT_ID": "test-client-id",
            "ALATION_CLIENT_SECRET": "test-client-secret",
            "TENANT_ID": "test-tenant-id",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = SDKConfig.from_env()

            assert config.alation_host == "https://test.alation.com"
            assert config.monitor_id == "123"
            assert config.client_id == "test-client-id"
            assert config.client_secret == "test-client-secret"
            assert config.tenant_id == "test-tenant-id"
            assert config.timeout == 30
            assert config.log_level == "INFO"

    def test_from_env_full_config(self):
        """Test creating config with all environment variables."""
        env_vars = {
            "ALATION_HOST": "https://test.alation.com/",  # With trailing slash
            "MONITOR_ID": "456",
            "ALATION_CLIENT_ID": "test-client-id",
            "ALATION_CLIENT_SECRET": "test-client-secret",
            "TENANT_ID": "test-tenant-id",
            "ALATION_TIMEOUT": "60",
            "LOG_LEVEL": "debug",
        }

        with patch.dict(os.environ, env_vars, clear=True):
            config = SDKConfig.from_env()

            assert config.alation_host == "https://test.alation.com"  # Trailing slash removed
            assert config.monitor_id == "456"
            assert config.client_id == "test-client-id"
            assert config.client_secret == "test-client-secret"
            assert config.tenant_id == "test-tenant-id"
            assert config.timeout == 60
            assert config.log_level == "DEBUG"

    def test_validate_valid_config(self):
        """Test validation of a valid configuration."""
        config = SDKConfig(
            alation_host="https://test.alation.com",
            monitor_id="123",
            client_id="test-client-id",
            client_secret="test-client-secret",
            tenant_id="test-tenant-id",
        )

        # Should not raise any exception
        config.validate()

    def test_validate_invalid_host_no_protocol(self):
        """Test validation fails for host without protocol."""
        config = SDKConfig(
            alation_host="test.alation.com",
            monitor_id="123",
            client_id="test-client-id",
            client_secret="test-client-secret",
            tenant_id="test-tenant-id",
        )

        with pytest.raises(DataQualitySDKError, match="ALATION_HOST must start with http://"):
            config.validate()

    def test_validate_invalid_monitor_id(self):
        """Test validation fails for non-numeric monitor ID."""
        config = SDKConfig(
            alation_host="https://test.alation.com",
            monitor_id="abc",
            client_id="test-client-id",
            client_secret="test-client-secret",
            tenant_id="test-tenant-id",
        )

        with pytest.raises(DataQualitySDKError, match="MONITOR_ID must be a numeric value"):
            config.validate()

    def test_validate_invalid_timeout(self):
        """Test validation fails for invalid timeout."""
        config = SDKConfig(
            alation_host="https://test.alation.com",
            monitor_id="123",
            client_id="test-client-id",
            client_secret="test-client-secret",
            tenant_id="test-tenant-id",
            timeout=-1,
        )

        with pytest.raises(DataQualitySDKError, match="ALATION_TIMEOUT must be positive"):
            config.validate()

    def test_validate_invalid_log_level(self):
        """Test validation fails for invalid log level."""
        config = SDKConfig(
            alation_host="https://test.alation.com",
            monitor_id="123",
            client_id="test-client-id",
            client_secret="test-client-secret",
            tenant_id="test-tenant-id",
            log_level="INVALID",
        )

        with pytest.raises(DataQualitySDKError, match="LOG_LEVEL must be one of"):
            config.validate()

    def test_get_checks_endpoint(self):
        """Test checks endpoint URL generation."""
        config = SDKConfig(
            alation_host="https://test.alation.com",
            monitor_id="123",
            client_id="test-client-id",
            client_secret="test-client-secret",
            tenant_id="test-tenant-id",
        )

        assert config.get_checks_endpoint() == "https://test.alation.com/api/checks?monitor_id=123"

    def test_get_metadata_endpoint(self):
        """Test metadata endpoint URL generation."""
        config = SDKConfig(
            alation_host="https://test.alation.com",
            monitor_id="123",
            client_id="test-client-id",
            client_secret="test-client-secret",
            tenant_id="test-tenant-id",
        )

        assert (
            config.get_metadata_endpoint()
            == "https://test.alation.com/api/dq/query_service_metadata"
        )

    def test_get_results_endpoint(self):
        """Test results endpoint URL generation."""
        config = SDKConfig(
            alation_host="https://test.alation.com",
            monitor_id="123",
            client_id="test-client-id",
            client_secret="test-client-secret",
            tenant_id="test-tenant-id",
        )

        assert config.get_results_endpoint() == "https://test.alation.com/api/results/soda"
