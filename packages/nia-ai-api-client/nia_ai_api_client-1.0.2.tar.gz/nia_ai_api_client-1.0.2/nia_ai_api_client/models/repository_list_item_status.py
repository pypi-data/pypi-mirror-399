from enum import Enum


class RepositoryListItemStatus(str, Enum):
    COMPLETED = "completed"
    ERROR = "error"
    INDEXED = "indexed"
    INDEXING = "indexing"

    def __str__(self) -> str:
        return str(self.value)
