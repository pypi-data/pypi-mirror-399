from zsynctech_studio_sdk.enums.execution import ExecutionStatus
from zsynctech_studio_sdk.models.base import BaseEntity
from pydantic import model_validator


class ExecutionModel(BaseEntity):
    totalTaskCount: int = 0
    currentTaskCount: int = 0
    status: ExecutionStatus = ExecutionStatus.WAITING

    @model_validator(mode='after')
    def validate_business_rules(self):
        """Validate business rules of the model.

        Checks if currentTaskCount does not exceed totalTaskCount,
        but only when totalTaskCount > 0.
        """
        current = self.currentTaskCount or 0
        total = self.totalTaskCount or 0
        if total > 0 and current > total:
            raise ValueError('currentTaskCount não pode ser maior que totalTaskCount')

        return self