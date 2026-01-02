from enum import Enum


class OracleResearchRequestModel(str, Enum):
    CLAUDE_OPUS_4_5_20251101 = "claude-opus-4-5-20251101"
    CLAUDE_SONNET_4_5_1M = "claude-sonnet-4-5-1m"
    CLAUDE_SONNET_4_5_20250929 = "claude-sonnet-4-5-20250929"

    def __str__(self) -> str:
        return str(self.value)
