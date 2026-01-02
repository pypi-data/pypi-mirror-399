from enum import Enum


class EditedFileOperation(str, Enum):
    CREATED = "created"
    DELETED = "deleted"
    MODIFIED = "modified"

    def __str__(self) -> str:
        return str(self.value)
