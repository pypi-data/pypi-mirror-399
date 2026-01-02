import threading
from typing import Optional, TYPE_CHECKING
from datetime import datetime, timezone

if TYPE_CHECKING:
    from zsynctech_studio_sdk.models.config import ExecutionParameters
    from zsynctech_studio_sdk.client import PlatformClient


class ExecutionContext:
    """Thread-safe global context to track current execution."""
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._initialized = True
        self._local = threading.local()

    def _get_state(self):
        if not hasattr(self._local, 'state'):
            self._local.state = {
                'execution_id': None,
                'current_task_id': None,
                'current_step_id': None,
                'automation_on_client_id': 'default-automation-client',
                'execution_parameters': None,
                'platform_client': None
            }
        return self._local.state

    @property
    def execution_id(self) -> Optional[str]:
        return self._get_state()['execution_id']

    @execution_id.setter
    def execution_id(self, value: str):
        self._get_state()['execution_id'] = value

    @property
    def current_task_id(self) -> Optional[str]:
        return self._get_state()['current_task_id']

    @current_task_id.setter
    def current_task_id(self, value: str):
        self._get_state()['current_task_id'] = value

    @property
    def current_step_id(self) -> Optional[str]:
        return self._get_state()['current_step_id']

    @current_step_id.setter
    def current_step_id(self, value: str):
        self._get_state()['current_step_id'] = value

    @property
    def automation_on_client_id(self) -> str:
        return self._get_state()['automation_on_client_id']

    @automation_on_client_id.setter
    def automation_on_client_id(self, value: str):
        self._get_state()['automation_on_client_id'] = value

    @property
    def execution_parameters(self) -> Optional['ExecutionParameters']:
        """Get the execution parameters for the current execution.

        Returns:
            ExecutionParameters object or None if not set
        """
        return self._get_state()['execution_parameters']

    @execution_parameters.setter
    def execution_parameters(self, value: Optional['ExecutionParameters']):
        """Set the execution parameters for the current execution.

        Args:
            value: ExecutionParameters object from the platform
        """
        self._get_state()['execution_parameters'] = value

    @property
    def platform_client(self) -> Optional['PlatformClient']:
        """Get the platform client for the current execution.

        Returns:
            PlatformClient object or None if not in deploy mode
        """
        return self._get_state()['platform_client']

    @platform_client.setter
    def platform_client(self, value: Optional['PlatformClient']):
        """Set the platform client for the current execution.

        Args:
            value: PlatformClient object or None
        """
        self._get_state()['platform_client'] = value

    def reset(self) -> None:
        """Clear current execution context.

        Removes all current execution, task and step IDs.
        """
        self._get_state().update({
            'execution_id': None,
            'current_task_id': None,
            'current_step_id': None,
            'automation_on_client_id': 'default-automation-client',
            'execution_parameters': None,
            'platform_client': None
        })


def get_iso_timestamp() -> str:
    """Return timestamp in ISO 8601 format with Z.

    Returns:
        str: UTC timestamp in YYYY-MM-DDTHH:MM:SS.sssZ format
    """
    return datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'


def get_end_timestamp() -> str:
    """Return timestamp +1 second in ISO 8601 format for endDate fields.

    This adds 1 second to help the platform display the data properly.

    Returns:
        str: UTC timestamp +1 second in YYYY-MM-DDTHH:MM:SS.sssZ format
    """
    from datetime import timedelta
    end_time = datetime.now(timezone.utc) + timedelta(seconds=1)
    return end_time.strftime('%Y-%m-%dT%H:%M:%S.%f')[:-3] + 'Z'


def get_execution_parameters() -> Optional['ExecutionParameters']:
    """Get the execution parameters for the current execution.

    This is a convenience function to access execution parameters from anywhere
    in your code during an execution.

    Returns:
        ExecutionParameters object with platform configuration, or None if not set

    Raises:
        RuntimeError: If called outside of an execution context

    Example:
        @execution
        def my_execution():
            params = get_execution_parameters()
            if params:
                print(f"Running for client: {params.clientId}")
                print(f"Input path: {params.inputPath}")
    """
    if not context.execution_id:
        raise RuntimeError("get_execution_parameters deve ser chamado dentro de um contexto de @execution")

    return context.execution_parameters


def get_execution():
    """Get the current execution model.

    This function allows you to access and modify fields of the current execution.
    After modifying fields, call update_execution() to save changes to the platform.

    Returns:
        ExecutionModel: Current execution model

    Raises:
        RuntimeError: If called outside of an execution context or if execution not found

    Example:
        @execution
        def my_execution():
            execution = get_execution()
            execution.observation = "Processing customer data"
            update_execution(execution)  # Save changes to platform
    """
    from zsynctech_studio_sdk.storage import storage

    if not context.execution_id:
        raise RuntimeError("get_execution deve ser chamado dentro de um contexto de @execution")

    execution = storage.get_execution(context.execution_id)
    if not execution:
        raise RuntimeError(f"Execution {context.execution_id} não encontrada")

    return execution


def update_execution(execution):
    """Update the current execution with modified fields.

    This function sends the modified execution model to the platform.

    Args:
        execution: ExecutionModel with updated fields

    Raises:
        RuntimeError: If called outside of an execution context

    Example:
        @execution
        def my_execution():
            execution = get_execution()
            execution.observation = "Processing customer data"
            update_execution(execution)
    """
    from zsynctech_studio_sdk.storage import storage

    if not context.execution_id:
        raise RuntimeError("update_execution deve ser chamado dentro de um contexto de @execution")

    if execution.id != context.execution_id:
        raise ValueError(f"Execution ID mismatch: expected {context.execution_id}, got {execution.id}")

    storage.save_execution(execution)


def get_task():
    """Get the current task model.

    This function allows you to access and modify fields of the current task,
    such as description or observation. After modifying fields, call update_task()
    to save changes to the platform.

    Returns:
        TaskModel: Current task model

    Raises:
        RuntimeError: If called outside of a task context or if task not found

    Example:
        @task
        def my_task():
            task = get_task()
            task.description = "Processing invoices"
            task.observation = "Found 50 items to process"
            update_task(task)  # Save changes to platform
    """
    from zsynctech_studio_sdk.storage import storage

    if not context.current_task_id:
        raise RuntimeError("get_task deve ser chamado dentro de um contexto de @task")

    task = storage.get_task(context.current_task_id)
    if not task:
        raise RuntimeError(f"Task {context.current_task_id} não encontrada")

    return task


def update_task(task):
    """Update the current task with modified fields.

    This function sends the modified task model to the platform.

    Args:
        task: TaskModel with updated fields

    Raises:
        RuntimeError: If called outside of a task context

    Example:
        @task
        def my_task():
            task = get_task()
            task.description = "Processing invoices"
            task.observation = "Found 50 items to process"
            update_task(task)
    """
    from zsynctech_studio_sdk.storage import storage

    if not context.current_task_id:
        raise RuntimeError("update_task deve ser chamado dentro de um contexto de @task")

    if task.id != context.current_task_id:
        raise ValueError(f"Task ID mismatch: expected {context.current_task_id}, got {task.id}")

    storage.save_task(task)


def get_step():
    """Get the current step model.

    This function allows you to access and modify fields of the current step,
    such as observation. After modifying fields, call update_step() to save
    changes to the platform.

    Returns:
        StepModel: Current step model

    Raises:
        RuntimeError: If called outside of a step context or if step not found

    Example:
        @step(code="0001")
        def my_step():
            step = get_step()
            step.observation = "Connecting to database"
            update_step(step)  # Save changes to platform
    """
    from zsynctech_studio_sdk.storage import storage

    if not context.current_step_id:
        raise RuntimeError("get_step deve ser chamado dentro de um contexto de @step")

    step = storage.get_step(context.current_step_id)
    if not step:
        raise RuntimeError(f"Step {context.current_step_id} não encontrado")

    return step


def update_step(step):
    """Update the current step with modified fields.

    This function sends the modified step model to the platform.

    Args:
        step: StepModel with updated fields

    Raises:
        RuntimeError: If called outside of a step context

    Example:
        @step(code="0001")
        def my_step():
            step = get_step()
            step.observation = "Connecting to database"
            update_step(step)
    """
    from zsynctech_studio_sdk.storage import storage

    if not context.current_step_id:
        raise RuntimeError("update_step deve ser chamado dentro de um contexto de @step")

    if step.id != context.current_step_id:
        raise ValueError(f"Step ID mismatch: expected {context.current_step_id}, got {step.id}")

    storage.save_step(step)


# Singleton instance
context = ExecutionContext()
