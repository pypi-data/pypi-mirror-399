"""Tests for the QueryClientWrapper class."""

import base64
from unittest.mock import Mock, patch

import pytest

from data_quality_sdk.client.query_client import QueryClientWrapper
from data_quality_sdk.utils.exceptions import ProtobufConfigError


class TestQueryClientWrapper:
    """Test cases for QueryClientWrapper class."""

    @pytest.fixture
    def query_wrapper(self):
        """Create a QueryClientWrapper instance for testing."""
        return QueryClientWrapper()

    @pytest.fixture
    def mock_protobuf_config(self):
        """Mock protobuf configuration object."""
        config = Mock()
        config.host = "test-host.com"
        config.port = 5432
        config.database = "test_db"
        config.username = "test_user"
        config.password = "test_pass"
        config.type = "postgresql"
        return config

    @pytest.fixture
    def sample_b64_config(self):
        """Sample base64 encoded configuration string."""
        return base64.b64encode(b"sample config data").decode()

    def test_init(self, query_wrapper):
        """Test QueryClientWrapper initialization."""
        assert query_wrapper.logger is not None

    @patch("queryservice_client.queryclient.QueryClient")
    def test_parse_protobuf_config_success(
        self, mock_query_client_class, query_wrapper, mock_protobuf_config, sample_b64_config
    ):
        """Test successful protobuf configuration parsing."""
        mock_query_client_class.configuration_from_b64_string.return_value = mock_protobuf_config

        with patch.object(query_wrapper, "_protobuf_to_dict") as mock_to_dict:
            mock_to_dict.return_value = {"host": "test-host.com", "port": 5432}

            result = query_wrapper.parse_protobuf_config(sample_b64_config)

            assert result == {"host": "test-host.com", "port": 5432}
            mock_query_client_class.configuration_from_b64_string.assert_called_once_with(
                sample_b64_config
            )
            mock_to_dict.assert_called_once_with(mock_protobuf_config)

    def test_parse_protobuf_config_import_error(self, query_wrapper, sample_b64_config):
        """Test protobuf parsing when QueryService client is not available."""
        # Simulate ImportError when importing QueryClient
        with patch(
            "builtins.__import__", side_effect=ImportError("No module named 'queryservice_client'")
        ):
            with pytest.raises(ProtobufConfigError, match="QueryService client not available"):
                query_wrapper.parse_protobuf_config(sample_b64_config)

    @patch("queryservice_client.queryclient.QueryClient")
    def test_parse_protobuf_config_parsing_error(
        self, mock_query_client_class, query_wrapper, sample_b64_config
    ):
        """Test protobuf parsing with general parsing error."""
        mock_query_client_class.configuration_from_b64_string.side_effect = Exception("Parse error")

        with pytest.raises(ProtobufConfigError, match="Failed to parse protobuf configuration"):
            query_wrapper.parse_protobuf_config(sample_b64_config)

    def test_protobuf_to_dict_with_google_protobuf(self, query_wrapper, mock_protobuf_config):
        """Test protobuf to dict conversion using Google protobuf."""
        expected_dict = {"host": "test-host.com", "port": 5432}

        with patch("google.protobuf.json_format.MessageToDict") as mock_message_to_dict:
            mock_message_to_dict.return_value = expected_dict

            result = query_wrapper._protobuf_to_dict(mock_protobuf_config)

            assert result == expected_dict
            mock_message_to_dict.assert_called_once_with(mock_protobuf_config)

    def test_protobuf_to_dict_fallback(self, query_wrapper, mock_protobuf_config):
        """Test protobuf to dict conversion with fallback method."""
        expected_dict = {"host": "test-host.com", "port": 5432}

        with patch("google.protobuf.json_format.MessageToDict", side_effect=ImportError):
            with patch.object(query_wrapper, "_extract_common_config_fields") as mock_extract:
                mock_extract.return_value = expected_dict

                result = query_wrapper._protobuf_to_dict(mock_protobuf_config)

                assert result == expected_dict
                mock_extract.assert_called_once_with(mock_protobuf_config)

    def test_extract_common_config_fields(self, query_wrapper, mock_protobuf_config):
        """Test extraction of common configuration fields."""
        result = query_wrapper._extract_common_config_fields(mock_protobuf_config)

        assert result["host"] == "test-host.com"
        assert result["port"] == 5432
        assert result["database"] == "test_db"
        assert result["username"] == "test_user"
        assert result["password"] == "test_pass"
        assert result["type"] == "postgresql"

    def test_extract_common_config_fields_with_nested_connection(self, query_wrapper):
        """Test extraction with nested connection object."""

        # Create a simple object that mimics a protobuf config with nested connection
        class SimpleConfig:
            def __init__(self):
                # No top-level attributes, only nested connection
                self.connection = SimpleConnection()

        class SimpleConnection:
            def __init__(self):
                self.host = "nested-host.com"
                self.port = 3306
                self.database = "nested_db"

        config = SimpleConfig()
        result = query_wrapper._extract_common_config_fields(config)

        assert result["host"] == "nested-host.com"
        assert result["port"] == 3306
        assert result["database"] == "nested_db"

    def test_extract_common_config_fields_empty_values_ignored(self, query_wrapper):
        """Test that empty values are ignored during extraction."""

        # Create a simple object with empty/falsy values
        class ConfigWithEmptyValues:
            def __init__(self):
                self.host = ""  # Empty string should be ignored
                self.port = 0  # Zero should be ignored
                self.database = None  # None should be ignored
                self.username = "valid_user"  # Valid value should be included

        config = ConfigWithEmptyValues()
        result = query_wrapper._extract_common_config_fields(config)

        # Empty/falsy values should be ignored due to the "if value" check in the code
        assert "host" not in result
        assert "port" not in result
        assert "database" not in result
        assert result["username"] == "valid_user"

    def test_get_connection_info_success(self, query_wrapper, sample_b64_config):
        """Test successful connection info extraction."""
        mock_config_dict = {
            "parameters": {
                "host": {"text": {"value": "test-host.com"}},
                "port": {"integer": {"value": 5432}},
                "database": {"text": {"value": "test_db"}},
                "username": {"text": {"value": "test_user"}},
                "password": {"encryptedText": {"value": "encrypted_pass"}},
                "type": {"select": {"value": "postgresql"}},
            }
        }

        with patch.object(query_wrapper, "parse_protobuf_config") as mock_parse:
            mock_parse.return_value = mock_config_dict

            result = query_wrapper.get_connection_info(sample_b64_config)

            assert result["host"] == "test-host.com"
            assert result["port"] == 5432
            assert result["database"] == "test_db"
            assert result["username"] == "test_user"
            assert result["password"] == "encrypted_pass"
            assert result["type"] == "postgresql"

    def test_get_connection_info_with_jdbc_uri(self, query_wrapper, sample_b64_config):
        """Test connection info extraction with JDBC URI."""
        mock_config_dict = {
            "parameters": {
                "jdbc_uri": {"text": {"value": "postgresql://test-host:5432/test_db"}},
                "username": {"text": {"value": "test_user"}},
            }
        }

        with patch.object(query_wrapper, "parse_protobuf_config") as mock_parse:
            mock_parse.return_value = mock_config_dict

            result = query_wrapper.get_connection_info(sample_b64_config)

            assert result["host"] == "test-host"
            assert result["port"] == 5432
            assert result["database"] == "test_db"
            assert result["type"] == "postgresql"
            assert result["username"] == "test_user"

    def test_get_connection_info_no_host_error(self, query_wrapper, sample_b64_config):
        """Test connection info extraction error when no host is found."""
        mock_config_dict = {
            "parameters": {
                "database": {"text": {"value": "test_db"}},
                "username": {"text": {"value": "test_user"}},
            }
        }

        with patch.object(query_wrapper, "parse_protobuf_config") as mock_parse:
            mock_parse.return_value = mock_config_dict

            with pytest.raises(ProtobufConfigError, match="No host or JDBC URI found"):
                query_wrapper.get_connection_info(sample_b64_config)

    def test_get_connection_info_type_inference_from_port(self, query_wrapper, sample_b64_config):
        """Test database type inference from port number."""
        mock_config_dict = {
            "parameters": {
                "host": {"text": {"value": "test-host.com"}},
                "port": {"integer": {"value": 3306}},  # MySQL default port
            }
        }

        with patch.object(query_wrapper, "parse_protobuf_config") as mock_parse:
            mock_parse.return_value = mock_config_dict

            result = query_wrapper.get_connection_info(sample_b64_config)

            assert result["type"] == "mysql"

    def test_parse_jdbc_uri_snowflake(self, query_wrapper):
        """Test JDBC URI parsing for Snowflake."""
        jdbc_uri = (
            "snowflake://myaccount.snowflakecomputing.com:443/?warehouse=COMPUTE_WH&db=TEST_DB"
        )

        result = query_wrapper._parse_jdbc_uri(jdbc_uri)

        assert result["host"] == "myaccount.snowflakecomputing.com"
        assert result["port"] == 443
        assert result["type"] == "snowflake"
        assert result["database"] == "TEST_DB"
        assert result["warehouse"] == "COMPUTE_WH"

    def test_parse_jdbc_uri_postgresql(self, query_wrapper):
        """Test JDBC URI parsing for PostgreSQL."""
        jdbc_uri = "postgresql://localhost:5432/testdb"

        result = query_wrapper._parse_jdbc_uri(jdbc_uri)

        assert result["host"] == "localhost"
        assert result["port"] == 5432
        assert result["database"] == "testdb"
        assert result["type"] == "postgresql"

    def test_parse_jdbc_uri_postgres_alternative(self, query_wrapper):
        """Test JDBC URI parsing for PostgreSQL with postgres:// scheme."""
        jdbc_uri = "postgres://localhost:5432/testdb"

        result = query_wrapper._parse_jdbc_uri(jdbc_uri)

        assert result["host"] == "localhost"
        assert result["port"] == 5432
        assert result["database"] == "testdb"
        assert result["type"] == "postgresql"

    def test_parse_jdbc_uri_mysql(self, query_wrapper):
        """Test JDBC URI parsing for MySQL."""
        jdbc_uri = "mysql://localhost:3306/testdb"

        result = query_wrapper._parse_jdbc_uri(jdbc_uri)

        assert result["host"] == "localhost"
        assert result["port"] == 3306
        assert result["database"] == "testdb"
        assert result["type"] == "mysql"

    def test_parse_jdbc_uri_invalid(self, query_wrapper):
        """Test JDBC URI parsing with invalid URI."""
        invalid_uri = "invalid://malformed-uri"

        result = query_wrapper._parse_jdbc_uri(invalid_uri)

        # Should return empty dict for unhandled/invalid URIs
        assert result == {}

    def test_parse_jdbc_uri_exception_handling(self, query_wrapper):
        """Test JDBC URI parsing with exception during parsing."""
        # This should trigger an exception in urlparse or processing
        malformed_uri = "://invalid-format"

        result = query_wrapper._parse_jdbc_uri(malformed_uri)

        # Should return empty dict when parsing fails
        assert result == {}

    def test_extract_param_value_various_types(self, query_wrapper, sample_b64_config):
        """Test parameter extraction for different value types."""
        mock_config_dict = {
            "parameters": {
                "host": {"text": {"value": "localhost"}},  # Add host to avoid error
                "text_param": {"text": {"value": "text_value"}},
                "encrypted_param": {"encryptedText": {"value": "encrypted_value"}},
                "bool_param": {"boolean": {"value": True}},
                "int_param": {"integer": {"value": 42}},
                "select_param": {"select": {"value": "selected_value"}},
                "textarea_param": {"textArea": {"value": "textarea_value"}},
            }
        }

        with patch.object(query_wrapper, "parse_protobuf_config") as mock_parse:
            mock_parse.return_value = mock_config_dict

            result = query_wrapper.get_connection_info(sample_b64_config)

            # The method should extract values from different parameter types
            assert result["host"] == "localhost"

    def test_alternative_parameter_names(self, query_wrapper, sample_b64_config):
        """Test extraction using alternative parameter names."""
        mock_config_dict = {
            "parameters": {
                "hostname": {"text": {"value": "alt-host.com"}},  # Alternative to "host"
                "dbname": {"text": {"value": "alt_db"}},  # Alternative to "database"
                "user": {"text": {"value": "alt_user"}},  # Alternative to "username"
                "pwd": {"encryptedText": {"value": "alt_pass"}},  # Alternative to "password"
                "default_schema": {"text": {"value": "alt_schema"}},  # Alternative to "schema"
            }
        }

        with patch.object(query_wrapper, "parse_protobuf_config") as mock_parse:
            mock_parse.return_value = mock_config_dict

            result = query_wrapper.get_connection_info(sample_b64_config)

            assert result["host"] == "alt-host.com"
            assert result["database"] == "alt_db"
            assert result["username"] == "alt_user"
            assert result["password"] == "alt_pass"
            assert result["schema"] == "alt_schema"
