from enum import Enum


class CreateOracleJobResponse200Status(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"

    def __str__(self) -> str:
        return str(self.value)
