#!/usr/bin/env python3
"""
Basic usage example for the Alation Data Quality SDK.

This example demonstrates how to use the SDK to run data quality checks
and perform health checks in various scenarios.

Run this file directly to see all examples:
    python examples/basic_usage.py
"""

import os

from data_quality_sdk import DataQualityRunner, SDKConfig


def basic_example():
    """Run data quality checks with basic configuration."""
    print("=== Basic Data Quality SDK Usage ===\n")

    print("Method 1: Using environment variables (recommended for production)")

    # Check if environment variables are set
    required_vars = [
        "ALATION_HOST",
        "MONITOR_ID",
        "ALATION_CLIENT_ID",
        "ALATION_CLIENT_SECRET",
        "TENANT_ID",
    ]
    if all(os.getenv(var) for var in required_vars):
        try:
            runner = DataQualityRunner()
            result = runner.run_checks()

            print(f"✅ Checks completed with exit code: {result['exit_code']}")
            print(f"Summary: {result['summary']}")

            if result["recommendations"]:
                print("\nRecommendations:")
                for rec in result["recommendations"]:
                    print(f"  - {rec}")

        except Exception as e:
            print(f"❌ Error: {e}")
    else:
        print(
            "Required environment variables not set, demonstrating with configuration object instead...\n"
        )

        print("Method 2: Using configuration object")

        # Example configuration (replace with your values)
        config = SDKConfig(
            alation_host="https://your-alation.company.com",
            monitor_id="123",
            client_id="your-oauth-client-id",
            client_secret="your-oauth-client-secret",
            tenant_id="your-tenant-id",
            timeout=30,
            log_level="INFO",
        )

        try:
            runner = DataQualityRunner(config)
            result = runner.run_checks()

            print(f"✅ Configuration-based run completed with exit code: {result['exit_code']}")
            print(f"Summary: {result['summary']}")

            if result["recommendations"]:
                print("\nRecommendations:")
                for rec in result["recommendations"]:
                    print(f"  - {rec}")

        except Exception as e:
            print(f"❌ Error: {e}")


def health_check_example():
    """Demonstrate health check functionality."""
    print("\n=== Health Check Example ===\n")

    try:
        # You can run health check without creating runner instances
        # to test basic SDK setup
        health = DataQualityRunner.health_check()

        print(f"Health Status: {health['status']}")
        print("Component Checks:")
        for component, status in health["checks"].items():
            print(f"  {component}: {status}")

        if health["recommendations"]:
            print("\nRecommendations:")
            for rec in health["recommendations"]:
                print(f"  - {rec}")

    except Exception as e:
        print(f"❌ Health check failed: {e}")


def error_handling_example():
    """Demonstrate error handling with invalid configuration."""
    print("\n=== Error Handling Example ===\n")

    # Example with invalid configuration to show error handling
    config = SDKConfig(
        alation_host="https://invalid-host.example.com",
        monitor_id="999999",
        client_id="invalid-client-id",
        client_secret="invalid-client-secret",
        tenant_id="invalid-tenant-id",
        timeout=5,  # Short timeout for quick failure
    )

    try:
        runner = DataQualityRunner(config)
        result = runner.run_checks()

        # Even if it "succeeds" in dry run, show the structure
        print("Result structure:")
        print(f"  Exit code: {result['exit_code']}")
        print(f"  Errors: {result.get('errors', [])}")
        print(f"  Monitor ID: {result.get('monitor_id')}")
        print(f"  Execution metadata: {result.get('execution_metadata', {})}")

    except Exception as e:
        print(f"❌ Expected error with invalid config: {e}")
        print("This demonstrates the SDK's error handling capabilities.")


def detailed_results_example():
    """Show how to access detailed results."""
    print("\n=== Detailed Results Example ===\n")

    # This example shows what kind of detailed information is available
    # (using a mock result since we don't have real credentials)

    mock_result = {
        "exit_code": 1,
        "monitor_id": "123",
        "alation_host": "https://your-alation.company.com",
        "summary": {
            "total_checks": 5,
            "passed": 3,
            "failed": 2,
            "warnings": 0,
            "errors": 0,
            "datasources_processed": 2,
        },
        "failed_checks": [
            {
                "name": "row_count > 1000",
                "table": "user_events",
                "status": "FAILED",
                "actual_value": 850,
                "expected_value": "> 1000",
                "message": "Row count check failed",
                "ds_id": 1,
                "dbtype": "postgresql",
            },
            {
                "name": "freshness < 1 day",
                "table": "daily_reports",
                "status": "FAILED",
                "message": "Data is 2 days old",
                "ds_id": 2,
                "dbtype": "snowflake",
            },
        ],
        "passed_checks": [
            {
                "name": "no duplicates",
                "table": "users",
                "status": "PASSED",
                "ds_id": 1,
                "dbtype": "postgresql",
            }
        ],
        "recommendations": [
            "📊 Row count issue in user_events: Check data ingestion process",
            "🕒 Data freshness issue in daily_reports: Check ETL pipeline schedules",
            "🛑 PIPELINE ACTION: Consider failing pipeline due to data quality issues",
        ],
        "execution_metadata": {
            "sdk_version": "1.0.0",
            "datasources_count": 2,
            "metrics_count": 8,
            "total_duration_seconds": 15.3,
            "dry_run": False,
        },
    }

    print("Example of detailed results structure:")
    print("Result:", mock_result)


if __name__ == "__main__":
    print("Alation Data Quality SDK - Basic Usage Examples")
    print("=" * 50)
    print("Note: This will use placeholder configuration values for demonstration.")
    print("Set the required environment variables to test with real data.\n")

    # Run all examples
    basic_example()
    health_check_example()
    error_handling_example()
    detailed_results_example()

    print("\n" + "=" * 50)
    print("Example completed!")
    print("To run with real data:")
    print("1. Set ALATION_HOST to your Alation instance URL")
    print("2. Set MONITOR_ID to a valid monitor ID")
    print("3. Set ALATION_CLIENT_ID to your OAuth client ID")
    print("4. Set ALATION_CLIENT_SECRET to your OAuth client secret")
    print("5. Set TENANT_ID to your tenant ID")
