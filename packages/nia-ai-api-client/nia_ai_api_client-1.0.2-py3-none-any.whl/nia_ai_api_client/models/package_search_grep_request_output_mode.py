from enum import Enum


class PackageSearchGrepRequestOutputMode(str, Enum):
    CONTENT = "content"
    COUNT = "count"
    FILES_WITH_MATCHES = "files_with_matches"

    def __str__(self) -> str:
        return str(self.value)
