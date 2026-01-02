from enum import Enum


class CancelOracleJobResponse200Status(str, Enum):
    CANCELLED = "cancelled"

    def __str__(self) -> str:
        return str(self.value)
