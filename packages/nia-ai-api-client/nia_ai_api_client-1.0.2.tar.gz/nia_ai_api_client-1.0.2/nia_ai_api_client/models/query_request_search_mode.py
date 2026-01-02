from enum import Enum


class QueryRequestSearchMode(str, Enum):
    REPOSITORIES = "repositories"
    SOURCES = "sources"

    def __str__(self) -> str:
        return str(self.value)
