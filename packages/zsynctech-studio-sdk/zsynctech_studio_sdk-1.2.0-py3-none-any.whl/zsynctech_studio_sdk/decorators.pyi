"""Type stubs for decorators module."""
from typing import Callable, Optional, TypeVar, Protocol, Any, overload
from typing_extensions import ParamSpec

P = ParamSpec("P")
R = TypeVar("R")


class ExecutionCallable(Protocol[P, R]):
    """Protocol for execution-decorated functions with deploy method."""

    def __call__(self, *args: P.args, **kwargs: P.kwargs) -> R: ...

    def deploy(
        self,
        instance_id: str,
        secret_key: str,
        server: str,
        host: str = "0.0.0.0",
        port: int = 8000,
        encryption_key: Optional[str] = None,
        **kwargs: Any
    ) -> None:
        """Deploy execution as FastAPI server.

        Creates a FastAPI server with /{instance_id}/health and /{instance_id}/start endpoints.

        Args:
            instance_id: Instance ID for robot identification
            secret_key: Secret key for platform authentication
            server: Platform server URL (e.g., "https://api.zsynctech.com")
            host: Host to bind the server to (default: 0.0.0.0)
            port: Port to bind the server to (default: 8000)
            encryption_key: Optional hexadecimal encryption key for decrypting credentials
            **kwargs: Additional arguments to pass to uvicorn.run
        """
        ...


@overload
def execution(
    func: Callable[P, R]
) -> ExecutionCallable[P, R]: ...

@overload
def execution(
    func: None = None,
    *,
    show_logs: bool = True,
    total_tasks: Optional[int] = None
) -> Callable[[Callable[P, R]], ExecutionCallable[P, R]]: ...

def execution(
    func: Optional[Callable[P, R]] = None,
    *,
    show_logs: bool = True,
    total_tasks: Optional[int] = None
) -> ExecutionCallable[P, R] | Callable[[Callable[P, R]], ExecutionCallable[P, R]]:
    """Decorator to mark a function as main execution.

    Can be used as @execution or @execution() or @execution(show_logs=True)

    Args:
        func: Function being decorated
        show_logs: If True, displays logs in real-time in console
        total_tasks: Total tasks to process (for progress calculation)

    Returns:
        Decorated function with deploy method
    """
    ...


class TaskCallable(Protocol[P, R]):
    """Protocol for task-decorated functions that accept task_code parameter."""

    def __call__(self, *args: P.args, task_code: Optional[str] = None, **kwargs: P.kwargs) -> R:
        """Call the task function.

        Args:
            *args: Positional arguments for the original function
            task_code: Optional task identifier code (can be passed dynamically at runtime)
            **kwargs: Keyword arguments for the original function

        Returns:
            Return value of the original function
        """
        ...


def task(func: Callable[P, R]) -> TaskCallable[P, R]:
    """Decorator to mark a function as task.

    Creates a task record and manages its lifecycle.

    The decorated function accepts an optional 'task_code' keyword argument
    to set a custom code for the task dynamically at runtime.

    Args:
        func: Function being decorated

    Returns:
        Decorated function that accepts task_code parameter

    Example:
        @task
        def processar():
            pass

        # Call with dynamic code
        processar(task_code="123")
    """
    ...


@overload
def step(
    func: Callable[P, R]
) -> Callable[P, R]: ...

@overload
def step(
    func: None = None,
    *,
    code: Optional[str] = None
) -> Callable[[Callable[P, R]], Callable[P, R]]: ...

def step(
    func: Optional[Callable[P, R]] = None,
    *,
    code: Optional[str] = None
) -> Callable[P, R] | Callable[[Callable[P, R]], Callable[P, R]]:
    """Decorator to mark a function as step.

    Can be used as @step, @step() or @step(code="CODE-001")

    Args:
        func: Function being decorated
        code: Step identifier code

    Returns:
        Decorated function
    """
    ...


def set_total_tasks(total: int) -> None:
    """Set the total tasks for current execution.

    Args:
        total: Total tasks to process

    Raises:
        RuntimeError: If called outside of an @execution context
    """
    ...
