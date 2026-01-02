from enum import Enum


class SourceContentRequestSourceType(str, Enum):
    DOCUMENTATION = "documentation"
    REPOSITORY = "repository"

    def __str__(self) -> str:
        return str(self.value)
