from enum import Enum


class DataSourceRequestLlmsTxtStrategy(str, Enum):
    IGNORE = "ignore"
    ONLY = "only"
    PREFER = "prefer"

    def __str__(self) -> str:
        return str(self.value)
