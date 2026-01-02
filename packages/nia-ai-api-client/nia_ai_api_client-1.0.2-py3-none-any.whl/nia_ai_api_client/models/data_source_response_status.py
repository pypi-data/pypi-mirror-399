from enum import Enum


class DataSourceResponseStatus(str, Enum):
    COMPLETED = "completed"
    ERROR = "error"
    FAILED = "failed"
    PENDING = "pending"
    PROCESSING = "processing"

    def __str__(self) -> str:
        return str(self.value)
