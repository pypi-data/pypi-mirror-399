"""Professional logging system for zsynctech-studio-sdk."""

from typing import Optional
import logging
import sys


class Colors:
    """ANSI color codes for terminal."""
    RESET = '\033[0m'
    BOLD = '\033[1m'

    # Cores para tipos
    EXECUTION = '\033[95m'  # Magenta
    TASK = '\033[94m'       # Azul
    STEP = '\033[96m'       # Ciano

    # Cores para status
    RUNNING = '\033[93m'    # Amarelo
    SUCCESS = '\033[92m'    # Verde
    FINISHED = '\033[92m'   # Verde
    FAIL = '\033[91m'       # Vermelho
    ERROR = '\033[91m'      # Vermelho

    # Cores para campos
    ID = '\033[90m'         # Cinza
    FIELD = '\033[37m'      # Branco


class SDKLogger:
    """Logger configured specifically for the SDK."""

    _instance: Optional['SDKLogger'] = None
    _initialized: bool = False

    def __new__(cls) -> 'SDKLogger':
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self) -> None:
        if self._initialized:
            return

        self._initialized = True
        self._logger_name: str = 'zsynctech_studio_sdk'
        self._logger: Optional[logging.Logger] = None
        self._console_handler: Optional[logging.StreamHandler] = None
        self._show_logs: bool = True

    def _setup_logger(self, show_logs: bool = True) -> None:
        """Configure the logger with console handler.

        Args:
            show_logs (bool): Whether to display logs in console
        """
        if self._logger is not None:
            self._show_logs = show_logs
            if self._console_handler:
                self._console_handler.setLevel(logging.INFO if show_logs else logging.CRITICAL)
            return

        self._logger = logging.getLogger(self._logger_name)
        self._logger.setLevel(logging.DEBUG)
        self._logger.propagate = False

        self._logger.handlers.clear()

        log_format = '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s'
        date_format = '%Y-%m-%d %H:%M:%S'
        formatter = logging.Formatter(log_format, datefmt=date_format)

        self._console_handler = logging.StreamHandler(sys.stdout)
        self._console_handler.setLevel(logging.INFO if show_logs else logging.CRITICAL)
        self._console_handler.setFormatter(formatter)

        if hasattr(sys.stdout, 'reconfigure'):
            try:
                sys.stdout.reconfigure(encoding='utf-8')
            except Exception:
                pass

        self._logger.addHandler(self._console_handler)

        self._show_logs = show_logs

    def get_logger(self, show_logs: bool = True) -> logging.Logger:
        """Return the configured logger.

        Args:
            show_logs (bool): Whether to display logs in console

        Returns:
            logging.Logger: Configured logger instance
        """
        self._setup_logger(show_logs)
        return self._logger

    def set_show_logs(self, show_logs: bool) -> None:
        """Update whether logs should be displayed in console.

        Args:
            show_logs (bool): Whether to display logs in console
        """
        self._show_logs = show_logs
        if self._console_handler:
            self._console_handler.setLevel(logging.INFO if show_logs else logging.CRITICAL)

    def execution_started(self, execution_id: str) -> None:
        """Log execution start.

        Args:
            execution_id (str): Unique execution ID
        """
        if self._logger:
            msg = (
                f"\n{Colors.EXECUTION}{Colors.BOLD}EXECUTION{Colors.RESET} "
                f"{Colors.ID}[{execution_id[-10:]}]{Colors.RESET} "
                f"{Colors.RUNNING}{Colors.BOLD}STARTED{Colors.RESET}"
            )
            self._logger.info(msg)

    def execution_finished(self, execution_id: str, total_tasks: int, current_tasks: int) -> None:
        """Log execution finish with success.

        Args:
            execution_id (str): Unique execution ID
            total_tasks (int): Total planned tasks
            current_tasks (int): Total executed tasks
        """
        if self._logger:
            msg = (
                f"{Colors.EXECUTION}{Colors.BOLD}EXECUTION{Colors.RESET} "
                f"{Colors.ID}[{execution_id[-10:]}]{Colors.RESET} "
                f"{Colors.FINISHED}{Colors.BOLD}FINISHED{Colors.RESET} → "
                f"{Colors.BOLD}{current_tasks}/{total_tasks} tasks{Colors.RESET}\n"
            )
            self._logger.info(msg)

    def execution_error(self, execution_id: str, error: Exception) -> None:
        """Log execution error.

        Args:
            execution_id (str): Unique execution ID
            error (Exception): Exception that caused the error
        """
        if self._logger:
            msg = (
                f"{Colors.EXECUTION}{Colors.BOLD}EXECUTION{Colors.RESET} "
                f"{Colors.ID}[{execution_id[-10:]}]{Colors.RESET} "
                f"{Colors.ERROR}{Colors.BOLD}FAILED{Colors.RESET} → "
                f"{Colors.ERROR}{str(error)}{Colors.RESET}\n"
            )
            self._logger.error(msg)

    def task_started(self, task_id: str, description: str, execution_id: str) -> None:
        """Log task start.

        Args:
            task_id (str): Unique task ID
            description (str): Task description
            execution_id (str): Parent execution ID
        """
        if self._logger:
            msg = (
                f"{Colors.TASK}{Colors.BOLD}TASK{Colors.RESET} "
                f"{Colors.ID}[{task_id[-10:]}]{Colors.RESET} "
                f"{Colors.RUNNING}{Colors.BOLD}RUNNING{Colors.RESET} → "
                f"{Colors.BOLD}{description}{Colors.RESET}"
            )
            self._logger.info(msg)

    def task_finished(self, task_id: str, description: str) -> None:
        """Log task finish with success.

        Args:
            task_id (str): Unique task ID
            description (str): Task description
        """
        if self._logger:
            msg = (
                f"{Colors.TASK}{Colors.BOLD}TASK{Colors.RESET} "
                f"{Colors.ID}[{task_id[-10:]}]{Colors.RESET} "
                f"{Colors.SUCCESS}{Colors.BOLD}SUCCESS{Colors.RESET} "
                f"{Colors.BOLD}{description}{Colors.RESET}"
            )
            self._logger.info(msg)

    def task_failed(self, task_id: str, description: str, error: Exception) -> None:
        """Log task failure.

        Args:
            task_id (str): Unique task ID
            description (str): Task description
            error (Exception): Exception that caused the failure
        """
        if self._logger:
            msg = (
                f"{Colors.TASK}{Colors.BOLD}TASK{Colors.RESET} "
                f"{Colors.ID}[{task_id[-10:]}]{Colors.RESET} "
                f"{Colors.FAIL}{Colors.BOLD}FAILED{Colors.RESET} "
                f"{Colors.BOLD}{description}{Colors.RESET} → "
                f"{Colors.ERROR}{str(error)}{Colors.RESET}"
            )
            self._logger.error(msg)

    def step_started(self, step_id: str, step_code: str, task_id: str) -> None:
        """Log step start.

        Args:
            step_id (str): Unique step ID
            step_code (str): Step identifier code
            task_id (str): Parent task ID
        """
        if self._logger:
            msg = (
                f"  {Colors.STEP}{Colors.BOLD}STEP{Colors.RESET} "
                f"{Colors.ID}[{step_id[-10:]}]{Colors.RESET} "
                f"{Colors.RUNNING}{Colors.BOLD}RUNNING{Colors.RESET} → "
                f"{Colors.BOLD}{step_code}{Colors.RESET}"
            )
            self._logger.info(msg)

    def step_finished(self, step_id: str, step_code: str) -> None:
        """Log step finish with success.

        Args:
            step_id (str): Unique step ID
            step_code (str): Step identifier code
        """
        if self._logger:
            msg = (
                f"  {Colors.STEP}{Colors.BOLD}STEP{Colors.RESET} "
                f"{Colors.ID}[{step_id[-10:]}]{Colors.RESET} "
                f"{Colors.SUCCESS}{Colors.BOLD}SUCCESS{Colors.RESET} "
                f"{Colors.BOLD}{step_code}{Colors.RESET}"
            )
            self._logger.info(msg)

    def step_failed(self, step_id: str, step_code: str, error: Exception) -> None:
        """Log step failure.

        Args:
            step_id (str): Unique step ID
            step_code (str): Step identifier code
            error (Exception): Exception that caused the failure
        """
        if self._logger:
            msg = (
                f"  {Colors.STEP}{Colors.BOLD}STEP{Colors.RESET} "
                f"{Colors.ID}[{step_id[-10:]}]{Colors.RESET} "
                f"{Colors.FAIL}{Colors.BOLD}FAILED{Colors.RESET} "
                f"{Colors.BOLD}{step_code}{Colors.RESET} → "
                f"{Colors.ERROR}{str(error)}{Colors.RESET}"
            )
            self._logger.error(msg)

    def info(self, message: str) -> None:
        """Log generic information.

        Args:
            message (str): Message to be logged
        """
        if self._logger:
            self._logger.info(message)

    def warning(self, message: str) -> None:
        """Log warning.

        Args:
            message (str): Warning message
        """
        if self._logger:
            self._logger.warning(message)

    def error(self, message: str) -> None:
        """Log error.

        Args:
            message (str): Error message
        """
        if self._logger:
            self._logger.error(message)

    def debug(self, message: str) -> None:
        """Log debug.

        Args:
            message (str): Debug message
        """
        if self._logger:
            self._logger.debug(message)


sdk_logger = SDKLogger()
