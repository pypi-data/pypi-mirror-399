"""Stateless storage system for executions, tasks and steps.

This module provides a storage interface that sends data directly to the platform
without keeping any state in memory. This prevents memory issues when processing
large volumes of data (e.g., 20k+ tasks per day) and supports multiple concurrent robots.

Only the CURRENT active models (execution, task, step) are kept temporarily to allow
updates. Historical data is immediately discarded after being sent to the platform.
"""

import threading
from typing import Optional
from zsynctech_studio_sdk.models import ExecutionModel, TaskModel, StepModel
from zsynctech_studio_sdk.context import context


class StatelessStorage:
    """Stateless storage that sends data directly to platform without caching.

    This class maintains minimal state only for:
    1. Current execution metadata (counters)
    2. Current active models (execution, task, step) - to allow updates

    Historical data is NOT stored. Only the currently active execution/task/step
    are kept temporarily to enable proper updates with full model data.
    """

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

    def _get_execution_metadata(self):
        """Get minimal execution metadata for counter tracking only."""
        if not hasattr(self._local, 'execution_metadata'):
            self._local.execution_metadata = {
                'totalTaskCount': 0,
                'currentTaskCount': 0
            }
        return self._local.execution_metadata

    def _get_current_models(self):
        """Get current active models cache.

        Only stores the CURRENTLY ACTIVE execution, task, and step.
        When a task finishes, it's removed. When a step finishes, it's removed.
        This prevents memory buildup while allowing proper updates.
        """
        if not hasattr(self._local, 'current_models'):
            self._local.current_models = {
                'execution': None,
                'tasks': {},      # Dict[task_id, TaskModel] - only current task
                'steps': {}       # Dict[step_id, StepModel] - only current step
            }
        return self._local.current_models

    def save_execution(self, execution: ExecutionModel):
        """Save an execution by sending it to the platform.

        Args:
            execution (ExecutionModel): The execution model to save
        """
        # Store counters for tracking
        metadata = self._get_execution_metadata()
        metadata['totalTaskCount'] = execution.totalTaskCount
        metadata['currentTaskCount'] = execution.currentTaskCount

        # Store current execution model (only one at a time)
        models = self._get_current_models()
        models['execution'] = execution

        # Send to platform if in deploy mode
        if context.platform_client:
            context.platform_client.send_execution(execution)

    def get_execution(self, execution_id: str) -> Optional[ExecutionModel]:
        """Retrieve current execution model.

        Args:
            execution_id (str): The execution ID to retrieve

        Returns:
            Optional[ExecutionModel]: Current execution model if active
        """
        models = self._get_current_models()
        execution = models['execution']
        if execution and execution.id == execution_id:
            return execution
        return None

    def update_execution(self, execution_id: str, **updates):
        """Update execution by merging with current model and sending to platform.

        Args:
            execution_id (str): The execution ID to update
            **updates: Fields to be updated
        """
        # Get current execution model
        current_execution = self.get_execution(execution_id)

        if current_execution:
            # Merge updates with current model
            updated_execution = current_execution.model_copy(update=updates)

            # Update counters in metadata
            metadata = self._get_execution_metadata()
            metadata['totalTaskCount'] = updated_execution.totalTaskCount
            metadata['currentTaskCount'] = updated_execution.currentTaskCount

            # Store updated model
            models = self._get_current_models()
            models['execution'] = updated_execution

            # Send update to platform if in deploy mode
            if context.platform_client:
                context.platform_client.send_execution(updated_execution)

    def save_task(self, task: TaskModel):
        """Save a task by sending it to the platform.

        Args:
            task (TaskModel): The task model to save
        """
        # Store current task (only active one, replaced when new task starts)
        models = self._get_current_models()
        models['tasks'][task.id] = task

        # Send to platform if in deploy mode
        if context.platform_client:
            context.platform_client.send_task(task)

    def get_task(self, task_id: str) -> Optional[TaskModel]:
        """Retrieve current task model.

        Args:
            task_id (str): The task ID to retrieve

        Returns:
            Optional[TaskModel]: Current task model if active
        """
        models = self._get_current_models()
        return models['tasks'].get(task_id)

    def update_task(self, task_id: str, **updates):
        """Update task by merging with current model and sending to platform.

        Args:
            task_id (str): The task ID to update
            **updates: Fields to be updated
        """
        # Get current task model
        current_task = self.get_task(task_id)

        if current_task:
            # Merge updates with current model
            updated_task = current_task.model_copy(update=updates)

            # Update stored model
            models = self._get_current_models()
            models['tasks'][task_id] = updated_task

            # Send update to platform if in deploy mode
            if context.platform_client:
                context.platform_client.send_task(updated_task)

            # If task is finished, remove from active tasks to free memory
            if updates.get('status') in ['SUCCESS', 'FAIL']:
                models['tasks'].pop(task_id, None)

    def save_step(self, step: StepModel):
        """Save a step by sending it to the platform.

        Args:
            step (StepModel): The step model to save
        """
        # Store current step (only active one, replaced when new step starts)
        models = self._get_current_models()
        models['steps'][step.id] = step

        # Send to platform if in deploy mode
        if context.platform_client:
            context.platform_client.send_step(step)

    def get_step(self, step_id: str) -> Optional[StepModel]:
        """Retrieve current step model.

        Args:
            step_id (str): The step ID to retrieve

        Returns:
            Optional[StepModel]: Current step model if active
        """
        models = self._get_current_models()
        return models['steps'].get(step_id)

    def update_step(self, step_id: str, **updates):
        """Update step by merging with current model and sending to platform.

        Args:
            step_id (str): The step ID to update
            **updates: Fields to be updated
        """
        # Get current step model
        current_step = self.get_step(step_id)

        if current_step:
            # Merge updates with current model
            updated_step = current_step.model_copy(update=updates)

            # Update stored model
            models = self._get_current_models()
            models['steps'][step_id] = updated_step

            # Send update to platform if in deploy mode
            if context.platform_client:
                context.platform_client.send_step(updated_step)

            # If step is finished, remove from active steps to free memory
            if updates.get('status') in ['SUCCESS', 'FAIL']:
                models['steps'].pop(step_id, None)

    def clear(self):
        """Clear all execution data (metadata and current models)."""
        if hasattr(self._local, 'execution_metadata'):
            self._local.execution_metadata.clear()

        if hasattr(self._local, 'current_models'):
            self._local.current_models = {
                'execution': None,
                'tasks': {},
                'steps': {}
            }


storage = StatelessStorage()
