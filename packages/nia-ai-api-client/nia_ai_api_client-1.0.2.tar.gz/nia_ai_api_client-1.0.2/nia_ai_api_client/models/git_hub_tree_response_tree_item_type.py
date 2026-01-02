from enum import Enum


class GitHubTreeResponseTreeItemType(str, Enum):
    FILE = "file"
    TREE = "tree"

    def __str__(self) -> str:
        return str(self.value)
