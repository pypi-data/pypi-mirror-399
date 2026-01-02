"""HTTP client for platform communication.

This module provides HTTP client to send execution, task, and step data to the platform.
"""
import httpx
from typing import Optional
from zsynctech_studio_sdk.models import ExecutionModel, TaskModel, StepModel
from zsynctech_studio_sdk.logger import sdk_logger


class PlatformClient:
    """HTTP client for communicating with the ZSyncTech platform."""

    def __init__(self, server: str, secret_key: str, instance_id: str, timeout: float = 30.0):
        """Initialize the platform client.

        Args:
            server: Platform server URL
            secret_key: Secret key for authentication
            instance_id: Instance ID for robot identification
            timeout: Request timeout in seconds (default: 30.0)
        """
        # Remove trailing slash from server URL
        self.server = server.rstrip('/')
        self.secret_key = secret_key
        self.instance_id = instance_id
        self.timeout = timeout

        # Build base URL
        self.base_url = f"{self.server}/automation-gateway/"

        # Build headers (format: Bearer key::instanceId)
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.secret_key}::{self.instance_id}"
        }

        # Create HTTP client
        self.client = httpx.Client(
            base_url=self.base_url,
            headers=self.headers,
            timeout=self.timeout
        )

    def _safe_request(self, method: str, endpoint: str, data: dict) -> Optional[dict]:
        """Make a safe HTTP request with error handling.

        Args:
            method: HTTP method (POST, PUT, etc.)
            endpoint: API endpoint
            data: JSON data to send

        Returns:
            Response JSON or None if request fails
        """
        try:
            response = self.client.request(method, endpoint, json=data)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPError as e:
            sdk_logger.get_logger().error(f"Platform request failed [{method} {endpoint}]: {e}")
            return None
        except Exception as e:
            sdk_logger.get_logger().error(f"Unexpected error in platform request: {e}")
            return None

    def send_execution(self, execution: ExecutionModel) -> Optional[dict]:
        """Send execution data to the platform.

        Args:
            execution: ExecutionModel instance

        Returns:
            Response JSON or None if request fails
        """
        data = execution.model_dump(mode='json', by_alias=True)
        return self._safe_request("POST", "executions", data)

    def send_task(self, task: TaskModel) -> Optional[dict]:
        """Send task data to the platform.

        Args:
            task: TaskModel instance

        Returns:
            Response JSON or None if request fails
        """
        data = task.model_dump(mode='json', by_alias=True)
        return self._safe_request("POST", "tasks", data)

    def send_step(self, step: StepModel) -> Optional[dict]:
        """Send step data to the platform.

        Args:
            step: StepModel instance

        Returns:
            Response JSON or None if request fails
        """
        data = step.model_dump(mode='json', by_alias=True)
        return self._safe_request("POST", "taskSteps", data)

    def close(self):
        """Close the HTTP client connection."""
        self.client.close()

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
