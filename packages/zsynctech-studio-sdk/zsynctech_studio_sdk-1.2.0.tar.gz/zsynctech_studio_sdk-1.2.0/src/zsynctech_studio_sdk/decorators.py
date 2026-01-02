import functools
import traceback
from typing import Callable, Optional
from uuid_extensions import uuid7

from zsynctech_studio_sdk.storage import storage
from zsynctech_studio_sdk.logger import sdk_logger
from zsynctech_studio_sdk.context import context, get_iso_timestamp, get_end_timestamp
from zsynctech_studio_sdk.enums import ExecutionStatus, TaskStatus, StepStatus
from zsynctech_studio_sdk.models import ExecutionModel, TaskModel, StepModel
from zsynctech_studio_sdk.server import ExecutionServer


def execution(
    func: Optional[Callable] = None,
    *,
    show_logs: bool = True,
    total_tasks: Optional[int] = None,
    exception_handlers: Optional[dict[type[Exception], ExecutionStatus]] = None
):
    """Decorator to mark a function as main execution.

    Can be used as @execution or @execution() or @execution(show_logs=True)

    Args:
        func (Optional[Callable]): Function being decorated
        show_logs (bool): If True, displays logs in real-time in console
        total_tasks (Optional[int]): Total tasks to process (for progress calculation)
        exception_handlers (Optional[dict[type[Exception], ExecutionStatus]]):
            Dictionary mapping exception types to execution status. When an exception
            is raised, the execution will be marked with the corresponding status
            instead of ERROR.

            Example:
                @execution(exception_handlers={
                    KeyboardInterrupt: ExecutionStatus.INTERRUPTED,
                    OutOfHoursError: ExecutionStatus.OUT_OF_OPERATING_HOURS
                })
                def my_execution():
                    pass
    """
    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            sdk_logger.get_logger(show_logs=show_logs)

            # Use execution ID from parameters if available, otherwise generate new one
            execution_id = str(uuid7())
            if context.execution_parameters and context.execution_parameters.executionId:
                execution_id = context.execution_parameters.executionId

            execution_model = ExecutionModel(
                id=execution_id,
                status=ExecutionStatus.RUNNING,
                totalTaskCount=total_tasks if total_tasks is not None else 0
            )

            context.execution_id = execution_model.id
            storage.save_execution(execution_model)
            sdk_logger.execution_started(execution_model.id)

            try:
                result = f(*args, **kwargs)

                storage.update_execution(
                    execution_model.id,
                    status=ExecutionStatus.FINISHED,
                    endDate=get_iso_timestamp()
                )

                execution = storage.get_execution(execution_model.id)
                sdk_logger.execution_finished(
                    execution_model.id,
                    execution.totalTaskCount,
                    execution.currentTaskCount
                )

                return result

            except Exception as e:
                error_msg = f"{str(e)}\n{traceback.format_exc()}"

                # Determine status based on exception_handlers
                status = ExecutionStatus.ERROR
                if exception_handlers:
                    for exception_type, custom_status in exception_handlers.items():
                        if isinstance(e, exception_type):
                            status = custom_status
                            break

                storage.update_execution(
                    execution_model.id,
                    status=status,
                    observation=error_msg,
                    endDate=get_iso_timestamp()
                )

                sdk_logger.execution_error(execution_model.id, e)
                raise

            finally:
                context.reset()

        def deploy(
            instance_id: str,
            secret_key: str,
            server: str,
            host: str = "0.0.0.0",
            port: int = 8000,
            encryption_key: Optional[str] = None,
            **kwargs
        ):
            """Deploy execution as FastAPI server.

            Creates a FastAPI server with /{instance_id}/health and /{instance_id}/start endpoints.

            Args:
                instance_id (str): Instance ID for robot identification
                secret_key (str): Secret key for platform authentication
                server (str): Platform server URL (e.g., "https://api.zsynctech.com")
                host (str): Host to bind the server to (default: 0.0.0.0)
                port (int): Port to bind the server to (default: 8000)
                encryption_key (Optional[str]): Hexadecimal encryption key for decrypting credentials
                **kwargs: Additional arguments to pass to uvicorn.run

            Example:
                @execution
                def my_execution():
                    # Your execution code
                    pass

                # Deploy as API server
                my_execution.deploy(
                    instance_id="robot-001",
                    secret_key="your-secret-key",
                    server="https://api.zsynctech.com",
                    port=8080,
                    encryption_key="your-hex-encryption-key"
                )
            """
            def get_execution_id():
                """Callback to get current execution_id from context."""
                return context.execution_id

            execution_server = ExecutionServer(
                wrapper,
                instance_id=instance_id,
                secret_key=secret_key,
                server=server,
                show_logs=show_logs,
                execution_id_callback=get_execution_id,
                encryption_key=encryption_key
            )
            execution_server.run(host=host, port=port, **kwargs)

        wrapper.deploy = deploy
        return wrapper

    if func is None:
        return decorator
    else:
        return decorator(func)


def task(func: Callable) -> Callable:
    """Decorator to mark a function as task.

    Creates a task record and manages its lifecycle.

    The decorated function can receive a 'task_code' keyword argument to set
    a custom code for the task dynamically at runtime.

    Example:
        @task
        def processar():
            pass

        # Call with dynamic code
        processar(task_code="123")
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Extract task_code from kwargs if provided
        task_code = kwargs.pop('task_code', None)

        # If task_code is in the function signature, extract it from kwargs or args
        import inspect
        sig = inspect.signature(func)
        if 'task_code' in sig.parameters and task_code is None:
            # Check if it was passed as positional argument
            param_names = list(sig.parameters.keys())
            if 'task_code' in param_names:
                task_code_index = param_names.index('task_code')
                if task_code_index < len(args):
                    # Extract from args and rebuild args without task_code
                    args_list = list(args)
                    task_code = args_list.pop(task_code_index)
                    args = tuple(args_list)

        if not context.execution_id:
            raise RuntimeError("Task deve ser executada dentro de um contexto de @execution")

        if task_code is not None:
            task_code = str(task_code)
        else:
            task_code = str(uuid7())

        task_model = TaskModel(
            id=str(uuid7()),
            executionId=context.execution_id,
            status=TaskStatus.RUNNING,
            description="Não informado",
            code=task_code,
            startDate=get_iso_timestamp()
        )

        context.current_task_id = task_model.id
        storage.save_task(task_model)

        execution = storage.get_execution(context.execution_id)
        if execution:
            new_current = execution.currentTaskCount + 1

            if execution.totalTaskCount < new_current:
                storage.update_execution(
                    context.execution_id,
                    currentTaskCount=new_current,
                    totalTaskCount=new_current
                )
            else:
                storage.update_execution(
                    context.execution_id,
                    currentTaskCount=new_current
                )

        sdk_logger.task_started(task_model.id, task_model.description, context.execution_id)

        try:
            result = func(*args, **kwargs)

            storage.update_task(
                task_model.id,
                status=TaskStatus.SUCCESS,
                observation="Task finalizada com sucesso",
                endDate=get_end_timestamp()
            )

            sdk_logger.task_finished(task_model.id, task_model.description)

            return result

        except Exception as e:
            error_msg = f"{str(e)}\n{traceback.format_exc()}"
            storage.update_task(
                task_model.id,
                status=TaskStatus.FAIL,
                observation=error_msg,
                endDate=get_end_timestamp()
            )
            sdk_logger.task_failed(task_model.id, task_model.description, e)
            raise

        finally:
            context.current_task_id = None

    return wrapper


def step(func: Optional[Callable] = None, *, code: Optional[str] = None):
    """Decorator to mark a function as step.

    Can be used as @step, @step() or @step(code="CODE-001")

    Args:
        func (Optional[Callable]): Function being decorated
        code (Optional[str]): Step identifier code
    """
    def decorator(f: Callable) -> Callable:
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            if not context.current_task_id:
                raise RuntimeError("Step deve ser executado dentro de um contexto de @task")

            step_model = StepModel(
                id=str(uuid7()),
                taskId=context.current_task_id,
                stepCode=code or str(f.__name__).upper(),
                automationOnClientId=context.automation_on_client_id,
                status=StepStatus.RUNNING,
                startDate=get_iso_timestamp()
            )

            context.current_step_id = step_model.id
            storage.save_step(step_model)

            sdk_logger.step_started(step_model.id, step_model.stepCode, context.current_task_id)

            try:
                result = f(*args, **kwargs)

                storage.update_step(
                    step_model.id,
                    status=StepStatus.SUCCESS,
                    endDate=get_end_timestamp()
                )

                sdk_logger.step_finished(step_model.id, step_model.stepCode)

                return result

            except Exception as e:
                error_msg = f"{str(e)}\n{traceback.format_exc()}"
                storage.update_step(
                    step_model.id,
                    status=StepStatus.FAIL,
                    observation=error_msg,
                    endDate=get_end_timestamp()
                )
                sdk_logger.step_failed(step_model.id, step_model.stepCode, e)
                raise

            finally:
                context.current_step_id = None

        return wrapper

    if func is None:
        return decorator
    else:
        return decorator(func)


def set_total_tasks(total: int) -> None:
    """Set the total tasks for current execution.

    Useful to dynamically define the total based on runtime data.

    Args:
        total (int): Total tasks to process

    Raises:
        RuntimeError: If called outside of an @execution context

    Example:
        @execution()
        def process_file():
            lines = read_file('data.csv')
            set_total_tasks(len(lines))
            for line in lines:
                process_line(line)
    """
    if not context.execution_id:
        raise RuntimeError("set_total_tasks deve ser chamado dentro de um contexto de @execution")

    storage.update_execution(context.execution_id, totalTaskCount=total)
