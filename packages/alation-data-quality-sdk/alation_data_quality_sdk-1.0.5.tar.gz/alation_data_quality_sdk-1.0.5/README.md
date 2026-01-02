# Alation Data Quality SDK

A production-ready Python SDK for executing Alation data quality checks using Soda Core. Designed for seamless integration into data pipelines, CI/CD workflows, and Airflow DAGs with minimal configuration.

## Features

- **Simple Configuration**: OAuth-based authentication with environment variables
- **Production Ready**: Comprehensive error handling, logging, and retry logic
- **Pipeline Friendly**: Built for Airflow and CI/CD integration with proper exit codes
- **Automatic Setup**: Fetches datasource credentials and check definitions from Alation
- **Comprehensive Results**: Detailed scan results with actionable recommendations
- **Enterprise Grade**: JWT token management with automatic refresh

## Installation

```bash
pip install alation-data-quality-sdk
```

## Prerequisites

Before using the SDK, ensure you have:

1. **Alation Instance Access**: A running Alation instance with data quality monitoring enabled
2. **OAuth Credentials**: Client ID and Secret configured in Alation (Settings > Authentication > OAuth Client Applications). Make sure you add an appropriate admin role for data quality access.
3. **Data Quality Monitor**: At least one configured monitor in Alation with defined checks
4. **Supported Datasource**: Connection to Snowflake, Redshift, Databricks, or BigQuery

## Configuration

### Required Environment Variables

```bash
export ALATION_HOST="https://your-instance.alationcloud.com"
export MONITOR_ID="123"
export ALATION_CLIENT_ID="your-client-id"
export ALATION_CLIENT_SECRET="your-client-secret"
export TENANT_ID="your-tenant-id"
```

### How to Obtain Configuration Values

- **ALATION_HOST**: Your Alation instance URL (e.g., `https://company.alationcloud.com`)
- **MONITOR_ID**: Found in Alation Data Quality Monitor page, in the URL (e.g., `.../data_quality/monitor/123`, the ID is `123`)
- **ALATION_CLIENT_ID & ALATION_CLIENT_SECRET**: Generated in Alation Settings > Authentication > OAuth Client Applications
- **TENANT_ID**: Found in Alation under Help (`?` Icon on top right) > About this instance

### Optional Environment Variables

```bash
export ALATION_TIMEOUT="30"     # Request timeout in seconds (default: 30)
export LOG_LEVEL="INFO"         # Logging level: DEBUG, INFO, WARNING, ERROR (default: INFO)
```

## Quick Start

### Python API

```python
from data_quality_sdk import DataQualityRunner

# Initialize and run checks
runner = DataQualityRunner()
result = runner.run_checks()

# Check results
if result['exit_code'] == 0:
    print("✅ All quality checks passed!")
else:
    print(f"❌ Quality checks failed: {result['summary']}")
    for recommendation in result['recommendations']:
        print(f"  - {recommendation}")
```

### Command Line Interface

```bash
# Run quality checks
alation-dq

# Perform health check
alation-dq --health-check

# Return only exit code (for pipelines)
alation-dq --exit-code-only
```

## Supported Data Sources

The SDK currently supports the following data sources:

- **Snowflake**
- **Amazon Redshift**
- **Databricks**
- **Google BigQuery**

Additional datasource support may be available through custom configuration. Contact Alation support for details.

## Integration Examples

### Airflow Integration

```python
from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta

def run_data_quality_checks(**context):
    from data_quality_sdk import DataQualityRunner

    runner = DataQualityRunner()
    result = runner.run_checks()

    if result['exit_code'] != 0:
        raise Exception(f"Data quality checks failed: {result['summary']}")

    return result

default_args = {
    'owner': 'data-team',
    'depends_on_past': False,
    'start_date': datetime(2024, 1, 1),
    'email_on_failure': True,
    'email_on_retry': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

dag = DAG(
    'data_quality_pipeline',
    default_args=default_args,
    description='Data Quality Pipeline',
    schedule_interval='@daily',
    catchup=False,
)

# Your ETL tasks here
extract_task = BashOperator(
    task_id='extract_data',
    bash_command='your-extract-script.sh',
    dag=dag,
)

transform_task = BashOperator(
    task_id='transform_data',
    bash_command='your-transform-script.sh',
    dag=dag,
)

# Data quality checks
quality_check_task = PythonOperator(
    task_id='data_quality_checks',
    python_callable=run_data_quality_checks,
    env_vars={
        'ALATION_HOST': '{{ var.value.ALATION_HOST }}',
        'MONITOR_ID': '{{ var.value.MONITOR_ID }}',
        'ALATION_CLIENT_ID': '{{ var.value.ALATION_CLIENT_ID }}',
        'ALATION_CLIENT_SECRET': '{{ var.value.ALATION_CLIENT_SECRET }}',
        'TENANT_ID': '{{ var.value.TENANT_ID }}',
    },
    dag=dag,
)

# Load task (only runs if quality checks pass)
load_task = BashOperator(
    task_id='load_data',
    bash_command='your-load-script.sh',
    dag=dag,
)

# Set dependencies
extract_task >> transform_task >> quality_check_task >> load_task
```

### CI/CD Integration

```yaml
# .github/workflows/data-quality.yml
name: Data Quality Checks

on:
  schedule:
    - cron: "0 6 * * *" # Daily at 6 AM
  workflow_dispatch:

jobs:
  quality-checks:
    runs-on: ubuntu-latest

    steps:
      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: "3.9"

      - name: Install SDK
        run: |
          pip install alation-data-quality-sdk

      - name: Run data quality checks
        env:
          ALATION_HOST: ${{ secrets.ALATION_HOST }}
          MONITOR_ID: ${{ secrets.MONITOR_ID }}
          ALATION_CLIENT_ID: ${{ secrets.ALATION_CLIENT_ID }}
          ALATION_CLIENT_SECRET: ${{ secrets.ALATION_CLIENT_SECRET }}
          TENANT_ID: ${{ secrets.TENANT_ID }}
        run: |
          alation-dq --exit-code-only
```

## How It Works

1. **Authenticate**: Uses OAuth client credentials to obtain JWT tokens from Alation
2. **Fetch Checks**: Retrieves check definitions and datasource information using the Monitor ID
3. **Get Credentials**: Obtains datasource connection credentials via Alation's metadata API
4. **Generate Config**: Converts protobuf configuration to Soda Core YAML format
5. **Execute Scan**: Runs Soda Core scan with generated configuration and check definitions
6. **Report Results**: Sends scan results back to Alation and provides detailed local results

## Advanced Usage

### Programmatic Configuration

```python
from data_quality_sdk import SDKConfig, DataQualityRunner

config = SDKConfig(
    alation_host="https://my-instance.alationcloud.com",
    monitor_id="123",
    client_id="your-client-id",
    client_secret="your-client-secret",
    tenant_id="your-tenant-id",
    timeout=60,
    log_level="DEBUG"
)

runner = DataQualityRunner(config)
result = runner.run_checks()
```

### Health Check

Before running in production, verify your setup:

```python
health = DataQualityRunner.health_check()

print(f"Status: {health['status']}")
for check, result in health['checks'].items():
    print(f"  {check}: {result}")
```

## Understanding Results

The SDK returns detailed results with the following structure:

```python
{
    'exit_code': 0,                    # 0 = success, >0 = issues
    'monitor_id': '123',
    'summary': {
        'total_checks': 10,
        'passed': 8,
        'failed': 2,
        'warnings': 0,
        'errors': 0
    },
    'failed_checks': [...],            # Details of failed checks
    'recommendations': [...],          # Actionable recommendations
    'execution_metadata': {...}       # Runtime information
}
```

## Exit Codes

- `0`: Success - all checks passed
- `1`: Quality checks failed (data quality issues)
- `2`: Configuration or setup error
- `3`: Results upload failed
- `4`: Network connectivity error
- `5`: Unexpected error

## Error Handling

The SDK provides comprehensive error handling with specific exception types:

- `AlationAPIError`: Issues with Alation API calls
- `DatasourceConfigError`: Problems with datasource configuration
- `SodaScanError`: Soda Core execution failures
- `UnsupportedDatasourceError`: Unsupported datasource types
- `NetworkError`: Network connectivity issues

## Logging

The SDK provides structured logging with configurable levels:

```python
# Set log level via environment variable
export LOG_LEVEL="DEBUG"

# Or programmatically
from data_quality_sdk.utils.logging import setup_logging
logger = setup_logging("DEBUG")
```

## Troubleshooting

### Common Issues

1. **"Invalid OAuth credentials"**
   - Verify ALATION_CLIENT_ID and ALATION_CLIENT_SECRET are correct
   - Ensure OAuth application is active in Alation Settings

2. **"Tenant ID not found"**
   - Verify TENANT_ID matches the value in Alation > Help > About this instance
   - Check that your OAuth application has the correct tenant scope

3. **"Monitor not found"**
   - Verify MONITOR_ID exists in Alation Data Quality Monitors
   - Ensure your user has access to the specified monitor

4. **"Unsupported datasource type"**
   - Check that your datasource is one of: Snowflake, Redshift, Databricks, BigQuery
   - Contact Alation support for additional datasource support

5. **Connection errors**
   - Verify ALATION_HOST is correct and accessible
   - Check network connectivity to your Alation instance
   - Ensure your OAuth credentials have not expired

### Debug Mode

Enable debug logging to get detailed information:

```bash
export LOG_LEVEL="DEBUG"
alation-dq
```

## Support

For issues and questions:

1. Check the troubleshooting section above
2. Enable debug logging with `LOG_LEVEL="DEBUG"`
3. Contact your Alation Customer Success team
4. Visit Alation Community forums at https://help.alation.com

For bug reports, please contact Alation Support with:
- SDK version (`pip show alation-data-quality-sdk`)
- Python version
- Error messages and logs
- Steps to reproduce

## License

Apache License 2.0
