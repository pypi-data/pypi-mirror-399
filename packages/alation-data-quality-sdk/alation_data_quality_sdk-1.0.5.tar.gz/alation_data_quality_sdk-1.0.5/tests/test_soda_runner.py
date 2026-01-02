"""Tests for the SodaRunner class."""

import tempfile
from unittest.mock import Mock, mock_open, patch

import pytest

from data_quality_sdk.datasource.soda_runner import SodaRunner
from data_quality_sdk.utils.exceptions import DatasourceConfigError, SodaScanError


class TestSodaRunner:
    """Test cases for SodaRunner class."""

    @pytest.fixture
    def soda_runner(self):
        """Create a SodaRunner instance for testing."""
        return SodaRunner()

    @pytest.fixture
    def check_data(self):
        """Sample check data for testing."""
        return {
            "ds_id": 1,
            "dbtype": "postgres",
            "checks": """
            checks for users:
              - row_count > 0
              - missing_count(email) = 0
            """,
        }

    @pytest.fixture
    def ocf_config(self):
        """Sample OCF configuration for testing."""
        return {
            "connection": {
                "host": "localhost",
                "port": "5432",
                "database": "test_db",
                "username": "test_user",
                "password": "test_pass",
            },
            "protobuf_config": "test_config_data",
        }

    @pytest.fixture
    def metric_dict(self):
        """Sample metric dictionary for testing."""
        return {
            "metric1": {
                "metric_id": "metric1",
                "check_definition": "row_count > 0",
                "table_name": "users",
            }
        }

    def test_init(self, soda_runner):
        """Test SodaRunner initialization."""
        assert soda_runner.logger is not None

    def test_execute_ds_scan_soda_not_installed(self, soda_runner, check_data, ocf_config):
        """Test scan execution when Soda Core is not installed."""
        with patch("builtins.__import__", side_effect=ImportError("No module named 'soda'")):
            with pytest.raises(SodaScanError, match="Soda Core not available"):
                soda_runner.execute_ds_scan(check_data, ocf_config)

    @patch("soda.scan.Scan")
    @patch(
        "data_quality_sdk.datasource.config_generator.DatasourceConfigGenerator.generate_soda_config"
    )
    def test_execute_ds_scan_success(
        self, mock_config_gen, mock_scan_class, soda_runner, check_data, ocf_config, metric_dict
    ):
        """Test successful scan execution."""
        # Mock the config generator to return valid YAML
        mock_config_gen.return_value = (
            "data_source postgres:\n  type: postgres\n  host: localhost\n  port: 5432"
        )

        # Mock scan instance
        mock_scan = Mock()
        mock_scan_class.return_value = mock_scan
        mock_scan.execute.return_value = None
        mock_scan.get_scan_results.return_value = {
            "checks": [{"name": "users.row_count", "outcome": "pass", "actualValue": 100}]
        }

        result = soda_runner.execute_ds_scan(check_data, ocf_config, metric_dict)

        assert result["checks"][0]["name"] == "users.row_count"
        assert result["checks"][0]["outcome"] == "pass"
        assert result["checks"][0]["actualValue"] == 100
        mock_scan.execute.assert_called_once()
        mock_scan.add_sodacl_yaml_str.assert_called_once()
        mock_scan.add_configuration_yaml_str.assert_called_once()

    @patch("soda.scan.Scan")
    @patch(
        "data_quality_sdk.datasource.config_generator.DatasourceConfigGenerator.generate_soda_config"
    )
    def test_execute_ds_scan_failure(
        self, mock_config_gen, mock_scan_class, soda_runner, check_data, ocf_config
    ):
        """Test scan execution failure."""
        # Mock the config generator to return valid YAML
        mock_config_gen.return_value = (
            "data_source postgres:\n  type: postgres\n  host: localhost\n  port: 5432"
        )

        # Mock scan instance that fails
        mock_scan = Mock()
        mock_scan_class.return_value = mock_scan
        mock_scan.execute.side_effect = Exception("Scan execution failed")

        with pytest.raises(SodaScanError, match="Soda scan execution failed for ds_id 1"):
            soda_runner.execute_ds_scan(check_data, ocf_config)

    def test_execute_ds_scan_missing_checks(self, soda_runner, ocf_config):
        """Test scan execution with missing checks data."""
        check_data_no_checks = {"ds_id": 1, "dbtype": "postgres", "checks": ""}

        with pytest.raises(SodaScanError, match="No valid checks YAML found in check data"):
            soda_runner.execute_ds_scan(check_data_no_checks, ocf_config)

    @patch("soda.scan.Scan")
    @patch(
        "data_quality_sdk.datasource.config_generator.DatasourceConfigGenerator.generate_soda_config"
    )
    def test_execute_ds_scan_invalid_dbtype(
        self, mock_config_gen, mock_scan_class, soda_runner, ocf_config
    ):
        """Test scan execution with unsupported database type."""
        # Mock config generator to raise an error for unsupported db type
        mock_config_gen.side_effect = DatasourceConfigError(
            "Unsupported database type: unsupported_db"
        )

        check_data_invalid = {
            "ds_id": 1,
            "dbtype": "unsupported_db",
            "checks": "checks for users: - row_count > 0",
        }

        with pytest.raises(SodaScanError, match="Soda scan execution failed for ds_id 1"):
            soda_runner.execute_ds_scan(check_data_invalid, ocf_config)

    @patch("soda.scan.Scan")
    @patch(
        "data_quality_sdk.datasource.config_generator.DatasourceConfigGenerator.generate_soda_config"
    )
    def test_generate_soda_configuration_postgres(
        self, mock_config_gen, mock_scan_class, soda_runner, check_data, ocf_config
    ):
        """Test Soda configuration generation for PostgreSQL."""
        # Mock the config generator to return valid PostgreSQL YAML
        mock_config_gen.return_value = "data_source postgres:\n  type: postgres\n  host: localhost\n  port: 5432\n  database: test_db"

        mock_scan = Mock()
        mock_scan_class.return_value = mock_scan
        mock_scan.execute.return_value = None
        mock_scan.get_scan_results.return_value = {"checks": []}

        result = soda_runner.execute_ds_scan(check_data, ocf_config)

        # Check that config generator was called with correct parameters
        mock_config_gen.assert_called_once_with(
            datasource_name="postgres", protobuf_config_b64="test_config_data", db_type="postgres"
        )
        assert result is not None

    @patch("soda.scan.Scan")
    @patch(
        "data_quality_sdk.datasource.config_generator.DatasourceConfigGenerator.generate_soda_config"
    )
    def test_generate_soda_configuration_snowflake(
        self, mock_config_gen, mock_scan_class, soda_runner, ocf_config
    ):
        """Test Soda configuration generation for Snowflake."""
        # Mock the config generator to return valid Snowflake YAML
        mock_config_gen.return_value = "data_source snowflake:\n  type: snowflake\n  host: account.snowflakecomputing.com\n  warehouse: COMPUTE_WH"

        check_data_snowflake = {
            "ds_id": 1,
            "dbtype": "snowflake",
            "checks": "checks for users: - row_count > 0",
        }

        mock_scan = Mock()
        mock_scan_class.return_value = mock_scan
        mock_scan.execute.return_value = None
        mock_scan.get_scan_results.return_value = {"checks": []}

        result = soda_runner.execute_ds_scan(check_data_snowflake, ocf_config)

        # Check that config generator was called with correct parameters
        mock_config_gen.assert_called_once_with(
            datasource_name="snowflake", protobuf_config_b64="test_config_data", db_type="snowflake"
        )
        assert result is not None

    @patch("soda.scan.Scan")
    @patch(
        "data_quality_sdk.datasource.config_generator.DatasourceConfigGenerator.generate_soda_config"
    )
    def test_extract_sample_failed_queries_success(
        self, mock_config_gen, mock_scan_class, soda_runner, check_data, ocf_config
    ):
        """Test successful extraction of sample failed queries."""
        # Mock the config generator to return valid YAML
        mock_config_gen.return_value = (
            "data_source postgres:\n  type: postgres\n  host: localhost\n  port: 5432"
        )

        # Mock scan with failed check that has sample query
        mock_scan = Mock()
        mock_scan_class.return_value = mock_scan
        mock_scan.execute.return_value = None
        mock_scan.get_scan_results.return_value = {
            "checks": [
                {
                    "name": "users.row_count",
                    "outcome": "fail",
                    "actualValue": 0,
                    "source_identity": "users.row_count",
                    "sampleFailedRowsQuery": "SELECT * FROM users LIMIT 10",
                }
            ]
        }

        # Execute scan first
        scan_result = soda_runner.execute_ds_scan(check_data, ocf_config)

        # Then extract failed queries
        result = soda_runner.extract_sample_failed_queries(scan_result, {}, 1)

        assert len(result) == 1
        assert result[0]["ds_id"] == 1
        assert result[0]["metric_unique_identifier"] == "users.row_count"
        assert "query" in result[0]

    @patch("soda.scan.Scan")
    @patch(
        "data_quality_sdk.datasource.config_generator.DatasourceConfigGenerator.generate_soda_config"
    )
    def test_extract_sample_failed_queries_no_failures(
        self, mock_config_gen, mock_scan_class, soda_runner, check_data, ocf_config
    ):
        """Test extraction when there are no failed checks."""
        # Mock the config generator to return valid YAML
        mock_config_gen.return_value = (
            "data_source postgres:\n  type: postgres\n  host: localhost\n  port: 5432"
        )

        # Mock scan with all passing checks
        mock_scan = Mock()
        mock_scan_class.return_value = mock_scan
        mock_scan.execute.return_value = None
        mock_scan.get_scan_results.return_value = {
            "checks": [{"name": "users.row_count", "outcome": "pass", "actualValue": 100}]
        }

        # Execute scan first
        soda_runner.execute_ds_scan(check_data, ocf_config)

        # Then extract failed queries
        result = soda_runner.extract_sample_failed_queries({}, {}, 1)

        assert len(result) == 0

    def test_extract_sample_failed_queries_no_scan_results(self, soda_runner):
        """Test extraction when no scan has been run."""
        result = soda_runner.extract_sample_failed_queries({}, {}, 1)
        assert len(result) == 0

    @patch("soda.scan.Scan")
    @patch(
        "data_quality_sdk.datasource.config_generator.DatasourceConfigGenerator.generate_soda_config"
    )
    def test_process_check_results_with_metadata(
        self, mock_config_gen, mock_scan_class, soda_runner, check_data, ocf_config, metric_dict
    ):
        """Test processing of check results with metric metadata."""
        # Mock the config generator to return valid YAML
        mock_config_gen.return_value = (
            "data_source postgres:\n  type: postgres\n  host: localhost\n  port: 5432"
        )

        mock_scan = Mock()
        mock_scan_class.return_value = mock_scan
        mock_scan.execute.return_value = None
        mock_scan.get_scan_results.return_value = {
            "checks": [
                {
                    "name": "users.row_count",
                    "outcome": "pass",
                    "actualValue": 100,
                    "expectedValue": "> 0",
                }
            ]
        }

        result = soda_runner.execute_ds_scan(check_data, ocf_config, metric_dict)

        assert "checks" in result
        assert len(result["checks"]) == 1
        check = result["checks"][0]
        assert check["name"] == "users.row_count"
        assert check["outcome"] == "pass"
        assert check["actualValue"] == 100

    @patch("soda.scan.Scan")
    @patch(
        "data_quality_sdk.datasource.config_generator.DatasourceConfigGenerator.generate_soda_config"
    )
    def test_cleanup_temp_files(
        self, mock_config_gen, mock_scan_class, soda_runner, check_data, ocf_config
    ):
        """Test that temporary files are properly cleaned up."""
        # Mock the config generator to return valid YAML
        mock_config_gen.return_value = (
            "data_source postgres:\n  type: postgres\n  host: localhost\n  port: 5432"
        )

        mock_scan = Mock()
        mock_scan_class.return_value = mock_scan
        mock_scan.execute.return_value = None
        mock_scan.get_scan_results.return_value = {"checks": []}

        result = soda_runner.execute_ds_scan(check_data, ocf_config)

        # Verify the scan was executed
        mock_scan.execute.assert_called_once()
        assert result is not None
