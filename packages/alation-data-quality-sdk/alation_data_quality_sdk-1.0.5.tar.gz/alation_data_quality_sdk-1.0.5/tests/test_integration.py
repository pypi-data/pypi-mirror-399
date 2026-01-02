"""Integration tests for the Data Quality SDK."""

from unittest.mock import MagicMock, Mock, patch

import pytest

from data_quality_sdk.config import SDKConfig
from data_quality_sdk.main import DataQualityRunner


@pytest.mark.integration
class TestDataQualityRunnerIntegration:
    """Integration tests for the complete DataQualityRunner workflow."""

    @pytest.fixture
    def integration_config(self):
        """Create configuration for integration testing."""
        return SDKConfig(
            alation_host="https://test.alation.com",
            monitor_id="123",
            client_id="test_client_id",
            client_secret="test_client_secret",
            tenant_id="test_tenant_id",
        )

    @patch("data_quality_sdk.main.AlationClient")
    @patch("data_quality_sdk.main.SodaRunner")
    @patch("data_quality_sdk.main.setup_logging")
    def test_complete_successful_workflow(
        self,
        mock_logging,
        mock_soda_runner_class,
        mock_client_class,
        integration_config,
        mock_check_data,
        mock_soda_scan_result,
        mock_ocf_config,
        mock_metric_dict,
    ):
        """Test complete successful workflow from start to finish."""
        # Setup mocks
        mock_logger = Mock()
        mock_logging.return_value = mock_logger

        # Mock Alation client
        mock_client = Mock()
        mock_client.get_all_metric_data.return_value = mock_metric_dict
        mock_client.get_all_checks_data.return_value = [mock_check_data]
        mock_client.get_ocf_configuration.return_value = mock_ocf_config
        mock_client.send_result_for_scan.return_value = None
        mock_client.save_sample_failed_check_queries.return_value = None
        mock_client_class.return_value = mock_client

        # Mock Soda runner
        mock_soda = Mock()
        mock_soda.execute_ds_scan.return_value = mock_soda_scan_result
        mock_soda.extract_sample_failed_queries.return_value = []
        mock_soda_runner_class.return_value = mock_soda

        # Create and run DataQualityRunner
        runner = DataQualityRunner(config=integration_config)
        result = runner.run_checks()

        # Verify the complete workflow
        assert result["exit_code"] == 1  # Exit code 1 because we have a failed check
        assert result["summary"]["total_checks"] == 2
        assert result["summary"]["passed"] == 1
        assert result["summary"]["failed"] == 1
        assert result["summary"]["datasources_processed"] == 1

        # Verify API calls were made
        mock_client.get_all_metric_data.assert_called_once_with("123")
        mock_client.get_all_checks_data.assert_called_once()
        mock_client.get_ocf_configuration.assert_called_once_with(1)
        mock_client.send_result_for_scan.assert_called_once()

        # Verify Soda scan was executed
        mock_soda.execute_ds_scan.assert_called_once()

        # Verify recommendations were generated
        assert len(result["recommendations"]) > 0

    @patch("data_quality_sdk.main.AlationClient")
    @patch("data_quality_sdk.main.SodaRunner")
    @patch("data_quality_sdk.main.setup_logging")
    def test_workflow_with_api_failure(
        self, mock_logging, mock_soda_runner_class, mock_client_class, integration_config
    ):
        """Test workflow when API calls fail."""
        mock_logger = Mock()
        mock_logging.return_value = mock_logger

        # Mock Alation client with API failure
        mock_client = Mock()
        mock_client.get_all_metric_data.side_effect = Exception("API Error")
        mock_client.get_all_checks_data.return_value = []
        mock_client_class.return_value = mock_client

        # Create and run DataQualityRunner
        runner = DataQualityRunner(config=integration_config)
        result = runner.run_checks()

        # Verify error handling
        assert result["exit_code"] == 2  # No checks found
        assert "No checks found for monitor" in result["errors"]

    @patch("data_quality_sdk.main.AlationClient")
    @patch("data_quality_sdk.main.SodaRunner")
    @patch("data_quality_sdk.main.setup_logging")
    def test_workflow_with_soda_scan_failure(
        self,
        mock_logging,
        mock_soda_runner_class,
        mock_client_class,
        integration_config,
        mock_check_data,
        mock_ocf_config,
        mock_metric_dict,
    ):
        """Test workflow when Soda scan fails."""
        mock_logger = Mock()
        mock_logging.return_value = mock_logger

        # Mock Alation client
        mock_client = Mock()
        mock_client.get_all_metric_data.return_value = mock_metric_dict
        mock_client.get_all_checks_data.return_value = [mock_check_data]
        mock_client.get_ocf_configuration.return_value = mock_ocf_config
        mock_client_class.return_value = mock_client

        # Mock Soda runner with failure
        mock_soda = Mock()
        mock_soda.execute_ds_scan.side_effect = Exception("Soda scan failed")
        mock_soda_runner_class.return_value = mock_soda

        # Create and run DataQualityRunner
        runner = DataQualityRunner(config=integration_config)
        result = runner.run_checks()

        # Verify error handling
        assert result["exit_code"] == 1  # Scan execution failed
        assert any("Scan failed for datasource 1" in error for error in result["errors"])

    @patch("data_quality_sdk.main.AlationClient")
    @patch("data_quality_sdk.main.SodaRunner")
    @patch("data_quality_sdk.main.setup_logging")
    def test_basic_workflow(
        self,
        mock_logging,
        mock_soda_runner_class,
        mock_client_class,
        mock_check_data,
        mock_metric_dict,
    ):
        """Test basic workflow with job creation."""
        mock_logger = Mock()
        mock_logging.return_value = mock_logger

        # Create test config
        test_config = SDKConfig(
            alation_host="https://test.alation.com",
            monitor_id="123",
            client_id="test_client_id",
            client_secret="test_client_secret",
            tenant_id="test_tenant_id",
        )

        # Mock Alation client
        mock_client = Mock()
        mock_client.get_all_metric_data.return_value = mock_metric_dict
        mock_client.get_all_checks_data.return_value = [mock_check_data]
        mock_client.create_job.return_value = 123
        mock_client.get_ocf_configuration.return_value = {
            "protobuf_config": "test_config",
            "connection": {"host": "localhost"},
        }
        mock_client.send_result_for_scan.return_value = None
        mock_client.save_sample_failed_check_queries.return_value = None
        mock_client.update_job_status.return_value = None  # Add missing method
        mock_client_class.return_value = mock_client

        # Mock Soda runner
        mock_soda = Mock()
        mock_soda.execute_ds_scan.return_value = {
            "ds_id": 1,
            "dbtype": "postgres",
            "checks": [
                {
                    "name": "row_count_metric",
                    "table": "users",
                    "outcome": "pass",
                    "actualValue": 100,
                    "expectedValue": ">= 0",
                },
                {
                    "name": "null_count_metric",
                    "table": "users",
                    "column": "email",
                    "outcome": "pass",
                    "actualValue": 0,
                    "expectedValue": "= 0",
                },
            ],
        }
        mock_soda.extract_sample_failed_queries.return_value = []
        mock_soda_runner_class.return_value = mock_soda

        # Create and run DataQualityRunner
        runner = DataQualityRunner(config=test_config)
        result = runner.run_checks()

        # Debug output to see what's causing the failure
        if result["exit_code"] != 0:
            print(f"DEBUG: exit_code = {result['exit_code']}")
            print(f"DEBUG: errors = {result.get('errors', [])}")
            print(f"DEBUG: summary = {result.get('summary', {})}")

        # Verify basic behavior
        assert result["exit_code"] == 0
        assert result["summary"]["total_checks"] == 2
        assert result["summary"]["passed"] == 2
        assert result["summary"]["failed"] == 0
        assert result["summary"]["errors"] == 0
        assert len(result["all_scan_results"]) == 1

        # Verify job was created
        mock_client.create_job.assert_called_once()

    @patch("data_quality_sdk.main.AlationClient")
    @patch("data_quality_sdk.main.SodaRunner")
    @patch("data_quality_sdk.main.setup_logging")
    def test_health_check_integration(
        self, mock_logging, mock_soda_runner_class, mock_client_class, integration_config
    ):
        """Test health check integration."""
        mock_logger = Mock()
        mock_logging.return_value = mock_logger

        # Mock Alation client
        mock_client = Mock()
        mock_client.health_check.return_value = True
        mock_client_class.return_value = mock_client

        # Test health check with classmethod
        health = DataQualityRunner.health_check(config=integration_config)

        # Verify health check
        assert health["status"] == "healthy"
        assert health["checks"]["alation_connectivity"] == "ok"
        assert health["checks"]["soda_core"] == "ok"
        assert health["checks"]["configuration"] == "ok"

    @patch("data_quality_sdk.main.AlationClient")
    @patch("data_quality_sdk.main.SodaRunner")
    @patch("data_quality_sdk.main.setup_logging")
    def test_multiple_datasources_workflow(
        self,
        mock_logging,
        mock_soda_runner_class,
        mock_client_class,
        integration_config,
        mock_ocf_config,
        mock_metric_dict,
    ):
        """Test workflow with multiple datasources."""
        mock_logger = Mock()
        mock_logging.return_value = mock_logger

        # Create multiple check data objects
        check_data_1 = Mock()
        check_data_1.ds_id = 1
        check_data_1.dbtype = "postgres"
        check_data_1.checks = [{"name": "check_1"}]

        check_data_2 = Mock()
        check_data_2.ds_id = 2
        check_data_2.dbtype = "mysql"
        check_data_2.checks = [{"name": "check_2"}]

        # Mock Alation client
        mock_client = Mock()
        mock_client.get_all_metric_data.return_value = mock_metric_dict
        mock_client.get_all_checks_data.return_value = [check_data_1, check_data_2]
        mock_client.get_ocf_configuration.return_value = mock_ocf_config
        mock_client.send_result_for_scan.return_value = None
        mock_client_class.return_value = mock_client

        # Mock Soda runner
        mock_soda = Mock()
        mock_soda.execute_ds_scan.return_value = {
            "ds_id": 1,
            "checks": [{"name": "test", "outcome": "pass"}],
        }
        mock_soda.extract_sample_failed_queries.return_value = []
        mock_soda_runner_class.return_value = mock_soda

        # Create and run DataQualityRunner
        runner = DataQualityRunner(config=integration_config)
        result = runner.run_checks()

        # Verify multiple datasources were processed
        assert result["summary"]["datasources_processed"] == 2
        assert len(result["all_scan_results"]) == 2

        # Verify API calls for both datasources
        assert mock_client.get_ocf_configuration.call_count == 2
        assert mock_client.send_result_for_scan.call_count == 2
        assert mock_soda.execute_ds_scan.call_count == 2
