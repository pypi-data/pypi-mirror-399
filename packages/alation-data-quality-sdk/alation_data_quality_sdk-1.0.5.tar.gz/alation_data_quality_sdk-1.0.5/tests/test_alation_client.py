"""Tests for the AlationClient class."""

import json
import os
import tempfile
import time
from unittest.mock import Mock, mock_open, patch

import pytest
import requests

from data_quality_sdk.client.alation_client import (
    AlationClient,
    MetricMetadata,
    MonitorCheckResponse,
    SampleFailedRowQuery,
)
from data_quality_sdk.utils.exceptions import AlationAPIError, NetworkError


class TestMetricMetadata:
    """Test cases for MetricMetadata class."""

    def test_init_and_to_dict(self):
        """Test MetricMetadata initialization and to_dict conversion."""
        data = {
            "metric_id": "test_metric",
            "check_definition": "row_count > 0",
            "check_description": "Check row count",
            "ds_id": 1,
            "dbtype": "postgres",
            "schema_name": "public",
            "table_name": "users",
            "column_name": "id",
            "category": "completeness",
            "monitor_id": "123",
        }

        metadata = MetricMetadata(data)
        assert metadata.metric_id == "test_metric"
        assert metadata.check_definition == "row_count > 0"
        assert metadata.ds_id == 1
        assert metadata.dbtype == "postgres"

        result_dict = metadata.to_dict()
        assert result_dict["metric_id"] == "test_metric"
        assert result_dict["check_definition"] == "row_count > 0"


class TestMonitorCheckResponse:
    """Test cases for MonitorCheckResponse class."""

    def test_init_and_to_dict(self):
        """Test MonitorCheckResponse initialization and to_dict conversion."""
        response = MonitorCheckResponse(1, "postgres", "checks: row_count > 0")
        assert response.ds_id == 1
        assert response.dbtype == "postgres"
        assert response.checks == "checks: row_count > 0"

        result_dict = response.to_dict()
        assert result_dict["ds_id"] == 1
        assert result_dict["dbtype"] == "postgres"
        assert result_dict["checks"] == "checks: row_count > 0"


class TestSampleFailedRowQuery:
    """Test cases for SampleFailedRowQuery class."""

    def test_init_and_to_dict(self):
        """Test SampleFailedRowQuery initialization and to_dict conversion."""
        query = SampleFailedRowQuery("metric_1", 1, "SELECT * FROM users WHERE id IS NULL")
        assert query.metric_unique_identifier == "metric_1"
        assert query.ds_id == 1
        assert query.query == "SELECT * FROM users WHERE id IS NULL"

        result_dict = query.to_dict()
        assert result_dict["metric_unique_identifier"] == "metric_1"
        assert result_dict["ds_id"] == 1
        assert result_dict["query"] == "SELECT * FROM users WHERE id IS NULL"


class TestAlationClient:
    """Test cases for AlationClient class."""

    @pytest.fixture
    def mock_jwt_response(self):
        """Mock JWT token response."""
        return {"access_token": "test_jwt_token", "expires_in": 3600, "token_type": "Bearer"}

    @pytest.fixture
    def client_config(self):
        """Basic client configuration."""
        return {
            "base_url": "https://test.alation.com",
            "client_id": "test_client_id",
            "client_secret": "test_client_secret",
            "timeout": 30,
        }

    @patch("data_quality_sdk.client.alation_client.requests.post")
    def test_init_success(self, mock_post, mock_jwt_response, client_config):
        """Test successful AlationClient initialization."""
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = mock_jwt_response

        with patch.object(AlationClient, "_load_jwt_from_cache", return_value=False):
            client = AlationClient(**client_config)

        assert client.base_url == "https://test.alation.com"
        assert client.client_id == "test_client_id"
        assert client.client_secret == "test_client_secret"
        assert client.timeout == 30
        assert client.jwt_token == "test_jwt_token"

    @patch("data_quality_sdk.client.alation_client.requests.post")
    def test_init_jwt_failure(self, mock_post, client_config):
        """Test AlationClient initialization with JWT failure."""
        mock_post.return_value.status_code = 401
        mock_post.return_value.text = "Unauthorized"

        with patch.object(AlationClient, "_load_jwt_from_cache", return_value=False):
            with pytest.raises(AlationAPIError, match="Failed to obtain JWT token"):
                AlationClient(**client_config)

    @patch("data_quality_sdk.client.alation_client.requests.post")
    def test_refresh_jwt_token_success(self, mock_post, mock_jwt_response, client_config):
        """Test successful JWT token refresh."""
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = mock_jwt_response

        with patch.object(AlationClient, "_load_jwt_from_cache", return_value=False), patch.object(
            AlationClient, "_save_jwt_to_cache"
        ) as mock_save:
            client = AlationClient(**client_config)

            assert client.jwt_token == "test_jwt_token"
            assert client.jwt_expires_at is not None
            mock_save.assert_called_once()

    @patch("data_quality_sdk.client.alation_client.requests.post")
    def test_refresh_jwt_token_network_error(self, mock_post, client_config):
        """Test JWT token refresh with network error."""
        mock_post.side_effect = requests.RequestException("Network error")

        with patch.object(AlationClient, "_load_jwt_from_cache", return_value=False):
            with pytest.raises(NetworkError, match="Failed to obtain JWT token"):
                AlationClient(**client_config)

    def test_ensure_valid_jwt_refresh_when_expired(self, client_config):
        """Test JWT refresh when token is expired."""
        with patch.object(AlationClient, "_load_jwt_from_cache", return_value=True), patch.object(
            AlationClient, "_refresh_jwt_token"
        ) as mock_refresh:
            client = AlationClient(**client_config)
            client.jwt_token = "old_token"
            client.jwt_expires_at = time.time() - 100  # Expired

            client._ensure_valid_jwt()
            mock_refresh.assert_called_once()

    def test_ensure_valid_jwt_no_refresh_when_valid(self, client_config):
        """Test no JWT refresh when token is still valid."""
        with patch.object(AlationClient, "_load_jwt_from_cache", return_value=True), patch.object(
            AlationClient, "_refresh_jwt_token"
        ) as mock_refresh:
            client = AlationClient(**client_config)
            client.jwt_token = "valid_token"
            client.jwt_expires_at = time.time() + 1800  # Valid for 30 minutes

            client._ensure_valid_jwt()
            mock_refresh.assert_not_called()

    def test_get_jwt_cache_path(self, client_config):
        """Test JWT cache path generation."""
        with patch.object(AlationClient, "_load_jwt_from_cache", return_value=True):
            client = AlationClient(**client_config)
            cache_path = client._get_jwt_cache_path()
            assert cache_path.endswith(".json")
            assert "alation" in cache_path or "jwt" in cache_path

    def test_load_jwt_from_cache_success(self, client_config):
        """Test successful JWT loading from cache."""
        cache_data = {
            "access_token": "cached_token",
            "expires_at": time.time() + 1800,
            "client_id": "test_client_id",
            "base_url": "https://test.alation.com",
        }

        with patch("builtins.open", mock_open(read_data=json.dumps(cache_data))), patch(
            "os.path.exists", return_value=True
        ), patch.object(AlationClient, "_refresh_jwt_token"):
            client = AlationClient(**client_config)
            assert client.jwt_token == "cached_token"

    def test_load_jwt_from_cache_expired(self, client_config):
        """Test JWT loading from cache with expired token."""
        cache_data = {
            "access_token": "expired_token",
            "expires_at": time.time() - 100,  # Expired
            "client_id": "test_client_id",
            "base_url": "https://test.alation.com",
        }

        with patch("builtins.open", mock_open(read_data=json.dumps(cache_data))), patch(
            "os.path.exists", return_value=True
        ), patch.object(AlationClient, "_refresh_jwt_token") as mock_refresh:
            AlationClient(**client_config)
            mock_refresh.assert_called()

    def test_save_jwt_to_cache(self, client_config):
        """Test JWT saving to cache."""
        with patch.object(AlationClient, "_load_jwt_from_cache", return_value=True), patch(
            "builtins.open", mock_open()
        ) as mock_file, patch("os.makedirs"), patch("os.chmod"):
            client = AlationClient(**client_config)
            client.jwt_token = "test_token"
            client.jwt_expires_at = time.time() + 1800

            client._save_jwt_to_cache()
            mock_file.assert_called()

    def test_get_all_metric_data_success(self, client_config):
        """Test successful metric data retrieval."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = [
            {"metric_id": "metric1", "check_definition": "row_count > 0"}
        ]

        with patch.object(AlationClient, "_load_jwt_from_cache", return_value=True), patch.object(
            AlationClient, "_refresh_jwt_token"
        ), patch.object(AlationClient, "_make_request", return_value=mock_response):
            client = AlationClient(**client_config)
            result = client.get_all_metric_data("123")

        assert "metric1" in result
        assert isinstance(result["metric1"], MetricMetadata)

    def test_get_all_checks_data_success(self, client_config):
        """Test successful checks data retrieval."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '[{"ds_id": 1, "dbtype": "postgres", "checks": {"row_count": "> 0"}}]'

        with patch.object(AlationClient, "_load_jwt_from_cache", return_value=True), patch.object(
            AlationClient, "_refresh_jwt_token"
        ), patch.object(AlationClient, "_make_request", return_value=mock_response):
            client = AlationClient(**client_config)
            result = client.get_all_checks_data("123")

        assert len(result) == 1
        assert isinstance(result[0], MonitorCheckResponse)
        assert result[0].ds_id == 1

    def test_health_check_success(self, client_config):
        """Test successful health check."""
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"django": "ok"}

        with patch.object(AlationClient, "_load_jwt_from_cache", return_value=True), patch.object(
            AlationClient, "_refresh_jwt_token"
        ):
            client = AlationClient(**client_config)

            # Mock the session.get method directly since health_check doesn't use _make_request
            with patch.object(client.session, "get", return_value=mock_response):
                result = client.health_check()

        assert result is True

    def test_health_check_failure(self, client_config):
        """Test health check failure."""
        mock_response = Mock()
        mock_response.status_code = 500

        with patch.object(AlationClient, "_load_jwt_from_cache", return_value=True), patch.object(
            AlationClient, "_refresh_jwt_token"
        ):
            client = AlationClient(**client_config)

            # Mock the session.get method directly
            with patch.object(client.session, "get", return_value=mock_response):
                result = client.health_check()

        assert result is False

    def test_make_request_with_retry_on_401(self, client_config):
        """Test request retry on 401 unauthorized error."""
        with patch.object(AlationClient, "_load_jwt_from_cache", return_value=True), patch.object(
            AlationClient, "_refresh_jwt_token"
        ):
            client = AlationClient(**client_config)

            # Mock first request raises 401 HTTPError, second returns 200
            mock_response_401 = Mock()
            mock_response_401.status_code = 401
            http_error = requests.HTTPError()
            http_error.response = mock_response_401
            mock_response_401.raise_for_status.side_effect = http_error

            mock_response_200 = Mock()
            mock_response_200.status_code = 200
            mock_response_200.raise_for_status.return_value = None

            with patch.object(
                client.session, "request", side_effect=[mock_response_401, mock_response_200]
            ):
                result = client._make_request("GET", "http://test.com")

                assert result.status_code == 200
