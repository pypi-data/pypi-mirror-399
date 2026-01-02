"""Configuration management for the Data Quality SDK."""

import os
from dataclasses import dataclass

from .utils.exceptions import DataQualitySDKError


@dataclass
class SDKConfig:
    """Configuration for the Data Quality SDK.

    Required Environment Variables:
        ALATION_HOST: The base URL of the Alation instance (e.g., https://my-alation.company.com)
        MONITOR_ID: The ID of the monitor to execute checks for
        ALATION_CLIENT_ID: OAuth client ID for JWT authentication
        ALATION_CLIENT_SECRET: OAuth client secret for JWT authentication
        TENANT_ID: Tenant ID for multi-tenant setups

    Optional Environment Variables:
        ALATION_TIMEOUT: Request timeout in seconds (default: 30)
        LOG_LEVEL: Logging level (default: INFO)
    """

    alation_host: str
    monitor_id: str
    tenant_id: str
    client_id: str
    client_secret: str
    timeout: int = 30
    log_level: str = "INFO"

    @classmethod
    def from_env(cls) -> "SDKConfig":
        """Create configuration from environment variables."""
        # Required variables
        alation_host = os.getenv("ALATION_HOST")
        monitor_id = os.getenv("MONITOR_ID")
        client_id = os.getenv("ALATION_CLIENT_ID")
        client_secret = os.getenv("ALATION_CLIENT_SECRET")
        tenant_id = os.getenv("TENANT_ID")

        if not alation_host:
            raise DataQualitySDKError(
                "ALATION_HOST environment variable is required. "
                "Set it to your Alation instance URL (e.g., https://my-alation.company.com)"
            )

        if not monitor_id:
            raise DataQualitySDKError(
                "MONITOR_ID environment variable is required. "
                "Set it to the ID of the monitor you want to execute."
            )

        if not client_id:
            raise DataQualitySDKError(
                "ALATION_CLIENT_ID environment variable is required. "
                "Set it to your OAuth client ID for JWT authentication."
            )

        if not client_secret:
            raise DataQualitySDKError(
                "ALATION_CLIENT_SECRET environment variable is required. "
                "Set it to your OAuth client secret for JWT authentication."
            )

        if not tenant_id:
            raise DataQualitySDKError(
                "TENANT_ID environment variable is required. "
                "Set it to your Alation's Tenant ID. You can find it in 'About this instance' under Help icon on top navigation bar."
            )

        # Optional variables
        timeout = int(os.getenv("ALATION_TIMEOUT", "30"))
        log_level = os.getenv("LOG_LEVEL", "INFO").upper()

        # Normalize alation_host (ensure no trailing slash)
        alation_host = alation_host.rstrip("/")

        return cls(
            alation_host=alation_host,
            monitor_id=monitor_id,
            client_id=client_id,
            client_secret=client_secret,
            tenant_id=tenant_id,
            timeout=timeout,
            log_level=log_level,
        )

    def get_checks_endpoint(self) -> str:
        """Get the checks endpoint URL."""
        return f"{self.alation_host}/api/checks?monitor_id={self.monitor_id}"

    def get_metadata_endpoint(self) -> str:
        """Get the metadata endpoint URL."""
        return f"{self.alation_host}/api/dq/query_service_metadata"

    def get_results_endpoint(self) -> str:
        """Get the results endpoint URL."""
        return f"{self.alation_host}/api/results/soda"

    def validate(self) -> None:
        """Validate the configuration."""
        if not self.alation_host.startswith(("http://", "https://")):
            raise DataQualitySDKError(
                f"ALATION_HOST must start with http:// or https://, got: {self.alation_host}"
            )

        if not self.monitor_id.isdigit():
            raise DataQualitySDKError(f"MONITOR_ID must be a numeric value, got: {self.monitor_id}")

        if self.timeout <= 0:
            raise DataQualitySDKError(f"ALATION_TIMEOUT must be positive, got: {self.timeout}")

        if self.log_level not in ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]:
            raise DataQualitySDKError(
                f"LOG_LEVEL must be one of DEBUG, INFO, WARNING, ERROR, CRITICAL, got: {self.log_level}"
            )
