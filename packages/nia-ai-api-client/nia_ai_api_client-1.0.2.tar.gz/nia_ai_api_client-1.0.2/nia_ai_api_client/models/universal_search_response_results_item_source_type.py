from enum import Enum


class UniversalSearchResponseResultsItemSourceType(str, Enum):
    DOCUMENTATION = "documentation"
    REPOSITORY = "repository"

    def __str__(self) -> str:
        return str(self.value)
