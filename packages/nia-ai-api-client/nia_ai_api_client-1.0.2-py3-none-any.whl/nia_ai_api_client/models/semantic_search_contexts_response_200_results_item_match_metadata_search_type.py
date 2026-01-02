from enum import Enum


class SemanticSearchContextsResponse200ResultsItemMatchMetadataSearchType(str, Enum):
    HYBRID = "hybrid"

    def __str__(self) -> str:
        return str(self.value)
