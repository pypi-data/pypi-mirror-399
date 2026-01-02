from enum import Enum


class ListResearchPapersStatus(str, Enum):
    COMPLETED = "completed"
    FAILED = "failed"
    PROCESSING = "processing"

    def __str__(self) -> str:
        return str(self.value)
