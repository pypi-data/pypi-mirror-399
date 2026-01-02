"""Alation API client for data quality operations."""

import json
from typing import Any, Dict, List, Optional, Tuple
from urllib.parse import urljoin

import requests
import yaml

from ..utils.exceptions import AlationAPIError, NetworkError
from ..utils.logging import get_logger, log_api_request


class MonitorCheckResponse:
    """Data structure for monitor check response."""

    def __init__(self, ds_id: int, dbtype: str, checks: str):
        self.ds_id = ds_id
        self.dbtype = dbtype
        self.checks = checks

    def to_dict(self) -> Dict[str, Any]:
        return {"ds_id": self.ds_id, "dbtype": self.dbtype, "checks": self.checks}


class MetricMetadata:
    """Data structure for metric metadata."""

    def __init__(self, data: Dict[str, Any]):
        self.metric_id = data.get("metric_id")
        self.check_definition = data.get("check_definition")
        self.check_description = data.get("check_description")
        self.ds_id = data.get("ds_id")
        self.dbtype = data.get("dbtype")
        self.schema_id = data.get("schema_id")
        self.schema_name = data.get("schema_name")
        self.table_id = data.get("table_id")
        self.table_name = data.get("table_name")
        self.column_id = data.get("column_id")
        self.column_name = data.get("column_name")
        self.category = data.get("category")
        self.asset_otype = data.get("asset_otype")
        self.asset_id = data.get("asset_id")
        self.sample_failed_query = data.get("sample_failed_query", "")
        self.monitor_id = data.get("monitor_id")
        self.monitor_title = data.get("monitor_title")
        self.is_absolute_value = data.get("is_absolute_value")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "metric_id": self.metric_id,
            "check_definition": self.check_definition,
            "check_description": self.check_description,
            "ds_id": self.ds_id,
            "dbtype": self.dbtype,
            "schema_id": self.schema_id,
            "schema_name": self.schema_name,
            "table_id": self.table_id,
            "table_name": self.table_name,
            "column_id": self.column_id,
            "column_name": self.column_name,
            "category": self.category,
            "asset_otype": self.asset_otype,
            "asset_id": self.asset_id,
            "sample_failed_query": self.sample_failed_query,
            "monitor_id": self.monitor_id,
            "monitor_title": self.monitor_title,
            "is_absolute_value": self.is_absolute_value,
        }


class SampleFailedRowQuery:
    """Data structure for sample failed row query."""

    def __init__(self, metric_unique_identifier: str, ds_id: int, query: str):
        self.metric_unique_identifier = metric_unique_identifier
        self.ds_id = ds_id
        self.query = query

    def to_dict(self) -> Dict[str, Any]:
        return {
            "metric_unique_identifier": self.metric_unique_identifier,
            "ds_id": self.ds_id,
            "query": self.query,
        }


class AlationClient:
    """Client for interacting with Alation APIs following the soda_check.py pattern."""

    def __init__(
        self,
        base_url: str,
        client_id: str,
        client_secret: str,
        timeout: int = 30,
    ):
        """Initialize the Alation client.

        Args:
            base_url: Base URL of the Alation instance (e.g., https://my-alation.company.com)
            client_id: OAuth client ID for JWT authentication
            client_secret: OAuth client secret for JWT authentication
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.client_id = client_id
        self.client_secret = client_secret
        self.timeout = timeout
        self.session = requests.Session()
        self.logger = get_logger(__name__)

        # JWT token management
        self.jwt_token: Optional[str] = None
        self.jwt_expires_at: Optional[float] = None

        # Set default headers
        self.session.headers.update(
            {"Content-Type": "application/json", "User-Agent": "Alation-DataQuality-SDK/1.0.0"}
        )

        # Load JWT token from cache or generate new one
        self._load_or_refresh_jwt_token()

    def _refresh_jwt_token(self) -> None:
        """Generate a new JWT token using client credentials."""
        import base64
        import time

        try:
            # Prepare Basic Auth header
            credentials = base64.b64encode(
                f"{self.client_id}:{self.client_secret}".encode()
            ).decode()
            headers = {
                "Authorization": f"Basic {credentials}",
                "Content-Type": "application/x-www-form-urlencoded",
                "User-Agent": "Alation-DataQuality-SDK/1.0.0",
            }

            # Prepare request body
            data = {"grant_type": "client_credentials"}

            # Make JWT token request
            endpoint = f"{self.base_url}/oauth/v2/token/"
            response = requests.post(endpoint, headers=headers, data=data, timeout=self.timeout)

            if response.status_code != 200:
                raise AlationAPIError(
                    f"Failed to obtain JWT token: {response.status_code} - {response.text}"
                )

            token_data = response.json()

            # Extract token information
            self.jwt_token = token_data.get("access_token")
            expires_in = token_data.get("expires_in", 3600)  # Default to 1 hour if not provided
            self.jwt_expires_at = time.time() + expires_in - 60  # Refresh 60 seconds before expiry

            if not self.jwt_token:
                raise AlationAPIError("JWT response missing access_token")

            # Update session headers with new JWT token
            self.session.headers.update({"Authorization": f"Bearer {self.jwt_token}"})

            self.logger.info("Successfully obtained JWT token")

            # Cache the new token
            self._save_jwt_to_cache()

        except requests.RequestException as e:
            raise NetworkError(f"Failed to obtain JWT token: {str(e)}", e)
        except Exception as e:
            raise AlationAPIError(f"Error generating JWT token: {str(e)}")

    def _ensure_valid_jwt(self) -> None:
        """Ensure JWT token is valid, refresh if necessary."""
        import time

        if not self.jwt_token or not self.jwt_expires_at:
            self.logger.info("No JWT token or expiry time, refreshing...")
            self._refresh_jwt_token()
            return

        if time.time() >= self.jwt_expires_at:
            self.logger.info("JWT token expired, refreshing...")
            self._refresh_jwt_token()
            return

    def _get_jwt_cache_path(self) -> str:
        """Get the path to the JWT cache file."""
        import os
        import tempfile

        # Try to use user's home directory first, fall back to temp directory
        try:
            cache_dir = os.path.expanduser("~/.alation")
            os.makedirs(cache_dir, exist_ok=True)
            return os.path.join(cache_dir, "jwt_cache.json")
        except (OSError, PermissionError):
            # Fall back to system temp directory with user-specific naming
            try:
                user_id = os.getuid()  # Unix/Linux
            except AttributeError:
                user_id = os.getenv("USERNAME", "user")  # Windows fallback
            return os.path.join(tempfile.gettempdir(), f"alation_jwt_cache_{user_id}.json")

    def _load_jwt_from_cache(self) -> bool:
        """Load JWT token from cache file if valid. Returns True if loaded successfully."""
        import json
        import os
        import time

        try:
            cache_path = self._get_jwt_cache_path()

            if not os.path.exists(cache_path):
                return False

            with open(cache_path, "r") as f:
                cache_data = json.load(f)

            # Validate cache data structure
            required_fields = ["access_token", "expires_at", "client_id", "base_url"]
            if not all(field in cache_data for field in required_fields):
                self.logger.debug("JWT cache missing required fields")
                return False

            # Check if cache is for the same client and host
            if cache_data["client_id"] != self.client_id or cache_data["base_url"] != self.base_url:
                self.logger.debug("JWT cache is for different client or host")
                return False

            # Check if token is still valid (with 60 second buffer)
            if time.time() >= (cache_data["expires_at"] - 60):
                self.logger.debug("JWT cache token is expired or expiring soon")
                return False

            # Load the cached token
            self.jwt_token = cache_data["access_token"]
            self.jwt_expires_at = cache_data["expires_at"]

            # Update session headers
            self.session.headers.update({"Authorization": f"Bearer {self.jwt_token}"})

            self.logger.info("Successfully loaded JWT token from cache")
            return True

        except (json.JSONDecodeError, KeyError, OSError, IOError) as e:
            self.logger.debug(f"Failed to load JWT from cache: {e}")
            return False

    def _save_jwt_to_cache(self) -> None:
        """Save current JWT token to cache file."""
        import json
        import os

        if not self.jwt_token or not self.jwt_expires_at:
            return

        try:
            cache_path = self._get_jwt_cache_path()

            cache_data = {
                "access_token": self.jwt_token,
                "expires_at": self.jwt_expires_at,
                "client_id": self.client_id,
                "base_url": self.base_url,
            }

            # Ensure directory exists
            os.makedirs(os.path.dirname(cache_path), exist_ok=True)

            # Write cache file with secure permissions
            with open(cache_path, "w") as f:
                json.dump(cache_data, f)

            # Set secure file permissions (user read/write only)
            try:
                os.chmod(cache_path, 0o600)
            except OSError:
                pass  # Ignore permission errors on systems that don't support chmod

            self.logger.debug(f"JWT token cached to {cache_path}")

        except (OSError, IOError) as e:
            self.logger.debug(f"Failed to save JWT to cache: {e}")
            # Don't raise exception - caching is optional

    def _load_or_refresh_jwt_token(self) -> None:
        """Load JWT from cache or generate a new one."""
        # Try to load from cache first
        if self._load_jwt_from_cache():
            return

        # Cache miss or invalid - generate new token
        self.logger.debug("No valid cached JWT found, generating new token")
        self._refresh_jwt_token()

    def get_all_metric_data(self, monitor_id: str) -> Dict[str, MetricMetadata]:
        """Get all metric metadata for a monitor.

        Args:
            monitor_id: The monitor ID to get metrics for

        Returns:
            Dictionary mapping metric_id to MetricMetadata objects

        Raises:
            AlationAPIError: If API call fails
        """
        endpoint = f"{self.base_url}/dqms/api/monitors/{monitor_id}/metrics"

        try:
            response = self._make_request("GET", endpoint)
            log_api_request(self.logger, "GET", endpoint, response.status_code)

            data = response.json()

            if not isinstance(data, list):
                raise AlationAPIError("Expected a list of metric objects from the metrics API")

            # Convert to dictionary keyed by metric_id
            metric_dict = {}
            for metric_data in data:
                metric = MetricMetadata(metric_data)
                if metric.metric_id:
                    metric_dict[str(metric.metric_id)] = metric

            self.logger.info(f"Retrieved {len(metric_dict)} metrics for monitor {monitor_id}")
            return metric_dict

        except requests.RequestException as e:
            raise NetworkError(f"Failed to retrieve metrics from Alation: {str(e)}", e)
        except json.JSONDecodeError as e:
            raise AlationAPIError(f"Invalid JSON response from metrics endpoint: {str(e)}")

    def get_all_checks_data(self, monitor_id: str) -> List[MonitorCheckResponse]:
        """Get all checks data for a monitor.

        Args:
            monitor_id: The monitor ID to get checks for

        Returns:
            List of MonitorCheckResponse objects

        Raises:
            AlationAPIError: If API call fails
        """
        # Use the standard checks endpoint
        endpoint = f"{self.base_url}/dqms/api/monitors/{monitor_id}/checks"

        try:
            response = self._make_request("GET", endpoint)
            log_api_request(self.logger, "GET", endpoint, response.status_code)

            # The API returns YAML content as a JSON-encoded string, so we need to decode it first
            try:
                # First try to parse as JSON to get the actual YAML content
                json_data = json.loads(response.text)
                if isinstance(json_data, str):
                    # The JSON contains a YAML string, parse it
                    yaml_data = yaml.safe_load(json_data)
                else:
                    # The JSON is already structured data
                    yaml_data = json_data
            except json.JSONDecodeError:
                # Fallback: try to parse directly as YAML
                yaml_data = yaml.safe_load(response.text)

            if not isinstance(yaml_data, list):
                raise AlationAPIError("Expected a list of check objects from the checks API")

            # Convert to MonitorCheckResponse objects
            check_responses = []
            for item in yaml_data:
                ds_id = item.get("ds_id")
                dbtype = item.get("dbtype")
                checks_data = item.get("checks")

                if not ds_id or not dbtype or not checks_data:
                    self.logger.warning(f"Skipping incomplete check data: {item}")
                    continue

                # Convert checks data back to YAML string
                checks_yaml = yaml.dump(checks_data, sort_keys=False)

                check_response = MonitorCheckResponse(
                    ds_id=ds_id, dbtype=dbtype, checks=checks_yaml
                )
                check_responses.append(check_response)

            self.logger.info(
                f"Retrieved {len(check_responses)} check configurations for monitor {monitor_id}"
            )
            return check_responses

        except requests.RequestException as e:
            raise NetworkError(f"Failed to retrieve checks from Alation: {str(e)}", e)
        except yaml.YAMLError as e:
            raise AlationAPIError(f"Invalid YAML response from checks endpoint: {str(e)}")
        except Exception as e:
            raise AlationAPIError(f"Failed to parse checks response: {str(e)}")

    def get_ocf_configuration(self, datasource_id: int) -> Dict[str, Any]:
        """Get OCF configuration for a datasource.

        Args:
            datasource_id: The datasource ID to get configuration for

        Returns:
            Dictionary containing OCF configuration data

        Raises:
            AlationAPIError: If API call fails
        """
        endpoint = f"{self.base_url}/api/v2/dq/query_service_metadata/"
        data = {"datasource_id": datasource_id}

        try:
            response = self._make_request("POST", endpoint, data=json.dumps(data))
            log_api_request(self.logger, "POST", endpoint, response.status_code)

            response_data = response.json()

            if "error" in response_data:
                raise AlationAPIError(
                    f"Error getting OCF configuration for datasource {datasource_id}: {response_data['error']}",
                    response.status_code,
                    response.text,
                )

            if "protobuf_config" not in response_data:
                raise AlationAPIError("No protobuf_config found in OCF configuration response")

            self.logger.info(f"Retrieved OCF configuration for datasource {datasource_id}")

            return response_data

        except requests.RequestException as e:
            raise NetworkError(f"Failed to retrieve OCF configuration: {str(e)}", e)
        except json.JSONDecodeError as e:
            raise AlationAPIError(
                f"Invalid JSON response from OCF configuration endpoint: {str(e)}"
            )

    def create_job(self, monitor_id: str) -> str:
        """Create a new job for the monitor and return the job_id.

        Args:
            monitor_id: Monitor identifier

        Returns:
            The created job_id

        Raises:
            AlationAPIError: If API call fails
        """
        endpoint = f"{self.base_url}/api/dq/monitors/{monitor_id}/job/new"

        payload = {"job_type": 94, "is_sdk_job": True}

        try:
            response = self._make_request("POST", endpoint, json=payload)
            log_api_request(self.logger, "POST", endpoint, response.status_code)

            response_data = response.json()
            job_id = response_data.get("job_id")

            if not job_id:
                raise AlationAPIError(f"No job_id returned from job creation API: {response_data}")

            self.logger.info(f"Successfully created job with ID: {job_id}")
            return str(job_id)

        except requests.RequestException as e:
            raise NetworkError(f"Failed to create job: {str(e)}", e)
        except json.JSONDecodeError as e:
            raise AlationAPIError(f"Invalid JSON response from job creation endpoint: {str(e)}")

    def send_result_for_scan(
        self,
        tenant_id: str,
        job_id: str,
        request_id: str,
        monitor_id: str,
        result: Dict[str, Any],
        ds_id: int,
        last_result: bool = False,
        job_type: str = "94",
    ) -> None:
        """Send scan results to the ingestion service.

        Args:
            tenant_id: Tenant identifier
            job_id: Job identifier
            request_id: Request identifier
            monitor_id: Monitor identifier
            result: Scan result data
            ds_id: Datasource identifier
            last_result: Whether this is the last result in a batch
            job_type: Type of job being executed

        Raises:
            AlationAPIError: If API call fails
        """
        import time

        # Modify request_id to include timestamp
        timestamped_request_id = f"{request_id}{int(time.time())}"

        # Construct the ingestion endpoint
        endpoint = (
            f"{self.base_url}/dqings/api/dq/tenants/{tenant_id}/jobs/{job_id}/"
            f"requests/{timestamped_request_id}/monitors/{monitor_id}/events/ingest/"
        )

        params = {
            "isLastResult": "true" if last_result else "false",
            "ds_id": str(ds_id),
            "job_type": job_type,
        }

        try:
            response = self._make_request("POST", endpoint, params=params, json=result)
            log_api_request(self.logger, "POST", endpoint, response.status_code)

            # Try to parse response even if it might be empty
            try:
                response_data = response.json()
                self.logger.info(f"Successfully sent scan results for datasource {ds_id}")
            except json.JSONDecodeError:
                # Some APIs don't return JSON, just check status code
                self.logger.info(
                    f"Successfully sent scan results for datasource {ds_id} (no response body)"
                )

        except requests.RequestException as e:
            raise NetworkError(f"Failed to send scan results: {str(e)}", e)

    def save_sample_failed_check_queries(
        self, monitor_id: str, job_id: str, samples: List[SampleFailedRowQuery]
    ) -> Any:
        """Save sample failed check queries.

        Args:
            monitor_id: Monitor identifier
            job_id: Job identifier
            samples: List of sample failed row queries

        Returns:
            Server response (if any)

        Raises:
            AlationAPIError: If API call fails
        """
        endpoint = f"{self.base_url}/dqms/api/monitors/{monitor_id}/jobs/{job_id}/sample-failed-check-queries"

        # Convert to dictionaries for JSON serialization
        samples_data = [sample.to_dict() for sample in samples]

        try:
            response = self._make_request("POST", endpoint, json=samples_data)
            log_api_request(self.logger, "POST", endpoint, response.status_code)

            self.logger.info(f"Successfully saved {len(samples)} sample failed check queries")

            # Return JSON if provided; else None
            try:
                return response.json()
            except json.JSONDecodeError:
                return None

        except requests.RequestException as e:
            raise NetworkError(f"Failed to save sample failed check queries: {str(e)}", e)

    def _make_request(self, method: str, url: str, **kwargs) -> requests.Response:
        """Make an HTTP request with error handling and JWT refresh.

        Args:
            method: HTTP method (GET, POST, etc.)
            url: URL to make request to
            **kwargs: Additional arguments to pass to requests

        Returns:
            Response object

        Raises:
            requests.RequestException: If request fails
        """
        # Ensure JWT token is valid before making the request
        self._ensure_valid_jwt()

        try:
            response = self.session.request(method=method, url=url, timeout=self.timeout, **kwargs)
            response.raise_for_status()
            return response

        except requests.exceptions.HTTPError as e:
            # Handle 401 Unauthorized - refresh JWT and retry once
            if e.response.status_code == 401:
                self.logger.info("Received 401 Unauthorized, refreshing JWT token and retrying...")
                self._refresh_jwt_token()

                # Retry the request with new token
                try:
                    response = self.session.request(
                        method=method, url=url, timeout=self.timeout, **kwargs
                    )
                    response.raise_for_status()
                    return response
                except requests.exceptions.RequestException as retry_e:
                    raise requests.RequestException(
                        f"Request failed after JWT refresh: {str(retry_e)}"
                    ) from retry_e
            else:
                # Re-raise non-401 HTTP errors
                raise e

        except requests.exceptions.Timeout as e:
            raise requests.RequestException(f"Request timeout after {self.timeout} seconds") from e
        except requests.exceptions.ConnectionError as e:
            raise requests.RequestException(f"Connection error: {str(e)}") from e
        except requests.exceptions.RequestException as e:
            # Re-raise with more context
            raise e

    def _extract_checks_from_response(self, data: Any) -> List[str]:
        """Extract SodaCL check blocks from API response.

        Args:
            data: Response data from checks API

        Returns:
            List of SodaCL check blocks as strings

        Raises:
            AlationAPIError: If no checks found or invalid format
        """
        checks_blocks = []

        if isinstance(data, list):
            # Response is a list of items, each with checks
            for item in data:
                if isinstance(item, dict) and "checks" in item:
                    checks_content = item["checks"]
                    if isinstance(checks_content, str) and checks_content.strip():
                        checks_blocks.append(checks_content.strip())
                    elif isinstance(checks_content, dict):
                        # Convert dict to YAML string
                        import yaml

                        checks_blocks.append(yaml.dump(checks_content, sort_keys=False))

        elif isinstance(data, dict):
            # Try different possible keys for checks content
            for key in ("dq_checks", "checks", "content"):
                val = data.get(key)
                if isinstance(val, str) and val.strip():
                    checks_blocks.append(val.strip())
                    break
                elif isinstance(val, list):
                    # Join list into one block
                    joined = "\n---\n".join([str(x) for x in val if str(x).strip()])
                    if joined.strip():
                        checks_blocks.append(joined.strip())
                    break

        if not checks_blocks:
            raise AlationAPIError("No SodaCL checks found in API response")

        return checks_blocks

    def health_check(self) -> bool:
        """Perform a health check on the Alation connection.

        Returns:
            True if connection is healthy, False otherwise
        """
        try:
            # Use the correct health check endpoint
            endpoint = f"{self.base_url}/monitor/i_am_alive"
            response = self.session.get(endpoint, timeout=5)

            if response.status_code != 200:
                return False

            # Check for expected response format
            try:
                data = response.json()
                return data.get("django") == "ok"
            except (ValueError, KeyError):
                # If response is not JSON or doesn't have expected format, consider unhealthy
                return False

        except Exception:
            return False
