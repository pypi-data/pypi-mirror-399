"""FastAPI server for remote execution.

This module provides a FastAPI server to run executions remotely.
"""
import asyncio
from typing import Callable, Optional
from fastapi import FastAPI, HTTPException, BackgroundTasks, Body
from pydantic import BaseModel
import threading
import uvicorn


from zsynctech_studio_sdk.logger import sdk_logger
from zsynctech_studio_sdk.context import context
from zsynctech_studio_sdk.models.config import ExecutionParameters
from zsynctech_studio_sdk.client import PlatformClient


class StartResponse(BaseModel):
    """Response model for start endpoint."""
    message: str
    execution_id: Optional[str] = None


class HealthResponse(BaseModel):
    """Response model for health endpoint."""
    status: str
    message: str
    execution_id: Optional[str] = None


class ExecutionServer:
    """Server to expose execution function via FastAPI."""

    def __init__(
        self,
        execution_func: Callable,
        instance_id: str,
        secret_key: str,
        server: str,
        show_logs: bool = True,
        execution_id_callback: Optional[Callable] = None,
        encryption_key: Optional[str] = None
    ):
        """Initialize the execution server.

        Args:
            execution_func: The decorated execution function to run
            instance_id: Instance ID for robot identification
            secret_key: Secret key for platform authentication
            server: Platform server URL
            show_logs: If True, displays logs in real-time
            execution_id_callback: Optional callback to get execution_id during execution
            encryption_key: Optional hexadecimal encryption key for decrypting credentials
        """
        self.execution_func = execution_func
        self.instance_id = instance_id
        self.secret_key = secret_key
        self.server = server
        self.show_logs = show_logs
        self.execution_id_callback = execution_id_callback
        self.encryption_key = encryption_key
        self.app = FastAPI(title="ZSyncTech Studio SDK API")
        self.is_running = False
        self.current_execution_id: Optional[str] = None
        self.current_execution_parameters: Optional[ExecutionParameters] = None

        self._setup_routes()

    def _setup_routes(self):
        """Setup FastAPI routes."""

        @self.app.get("/{instance_id}/health", response_model=HealthResponse)
        async def health(instance_id: str):
            """Health check endpoint.

            Args:
                instance_id: Instance ID from the URL path

            Returns:
                HealthResponse with server status and execution_id if running

            Raises:
                HTTPException: If instance_id doesn't match
            """
            # Validate instance_id
            if instance_id != self.instance_id:
                raise HTTPException(
                    status_code=403,
                    detail={
                        "error": "Invalid instance ID",
                        "message": f"Instance ID '{instance_id}' does not match configured instance."
                    }
                )

            if self.is_running:
                return HealthResponse(
                    status="running",
                    message=f"Robot is processing execution",
                    execution_id=self.current_execution_id
                )
            else:
                return HealthResponse(
                    status="healthy",
                    message="Robot is up and ready",
                    execution_id=None
                )

        @self.app.post("/{instance_id}/start", response_model=StartResponse)
        async def start(
            instance_id: str,
            background_tasks: BackgroundTasks,
            parameters: Optional[ExecutionParameters] = Body(None, description="Execution parameters from platform")
        ):
            """Start execution endpoint.

            Args:
                instance_id: Instance ID from the URL path
                background_tasks: FastAPI background tasks manager
                parameters: Optional execution parameters from the platform

            Returns:
                StartResponse with execution status

            Raises:
                HTTPException: If execution is already running or instance_id doesn't match
            """
            # Validate instance_id
            if instance_id != self.instance_id:
                raise HTTPException(
                    status_code=403,
                    detail={
                        "error": "Invalid instance ID",
                        "message": f"Instance ID '{instance_id}' does not match configured instance."
                    }
                )

            if self.is_running:
                raise HTTPException(
                    status_code=409,
                    detail={
                        "error": "Execution already in progress",
                        "message": f"Cannot start new execution. Please wait for the current execution to finish.",
                        "current_execution_id": self.current_execution_id
                    }
                )

            # Store parameters for the execution
            self.current_execution_parameters = parameters

            background_tasks.add_task(self._run_execution)

            return StartResponse(
                message="Execution started successfully in background",
                execution_id=None  # Will be set after execution starts
            )

    async def _run_execution(self):
        """Run the execution function in background."""
        self.is_running = True
        try:
            # Run the execution function (it's synchronous)
            # The execution_id is set inside the decorated function
            result = await asyncio.to_thread(self._execute_and_capture_id)
            self.is_running = False
            self.current_execution_id = None
            self.current_execution_parameters = None
            return result
        except Exception as e:
            self.is_running = False
            self.current_execution_id = None
            self.current_execution_parameters = None
            sdk_logger.get_logger(show_logs=self.show_logs).error(f"Execution failed: {e}")
            raise

    def _execute_and_capture_id(self):
        """Execute the function and capture the execution ID from context."""
        import time

        # Set automation_on_client_id to instance_id
        context.automation_on_client_id = self.instance_id

        # Set execution parameters in context before execution starts
        if self.current_execution_parameters:
            # Inject encryption_key if provided
            if self.encryption_key:
                self.current_execution_parameters.encryption_key = self.encryption_key
            context.execution_parameters = self.current_execution_parameters

        # Initialize platform client for deploy mode
        platform_client = PlatformClient(
            server=self.server,
            secret_key=self.secret_key,
            instance_id=self.instance_id
        )
        context.platform_client = platform_client

        # Start execution in a separate tracking mechanism
        # We need to capture the execution_id after it's set in the decorator
        def run_with_id_capture():
            # Give a small delay for the execution_id to be set
            time.sleep(0.1)
            if self.execution_id_callback:
                self.current_execution_id = self.execution_id_callback()

        # Start ID capture in background
        capture_thread = threading.Thread(target=run_with_id_capture)
        capture_thread.start()

        try:
            # Call the execution function
            result = self.execution_func()
            return result
        finally:
            # Close platform client connection
            platform_client.close()

    def run(self, host: str = "0.0.0.0", port: int = 8000, **kwargs):
        """Start the FastAPI server.

        Args:
            host: Host to bind the server to (default: 0.0.0.0)
            port: Port to bind the server to (default: 8000)
            **kwargs: Additional arguments to pass to uvicorn.run
        """
        uvicorn.run(self.app, host=host, port=port, **kwargs)
