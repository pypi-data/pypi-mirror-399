from enum import Enum


class DataSourceResponseSourceType(str, Enum):
    DOCUMENTATION = "documentation"
    RESEARCH_PAPER = "research_paper"
    TEXT = "text"
    WEB = "web"

    def __str__(self) -> str:
        return str(self.value)
