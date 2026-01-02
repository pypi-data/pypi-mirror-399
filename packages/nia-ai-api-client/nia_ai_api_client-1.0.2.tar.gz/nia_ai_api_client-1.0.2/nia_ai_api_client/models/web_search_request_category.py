from enum import Enum


class WebSearchRequestCategory(str, Enum):
    BLOG = "blog"
    COMPANY = "company"
    GITHUB = "github"
    NEWS = "news"
    PDF = "pdf"
    RESEARCH = "research"
    TWEET = "tweet"

    def __str__(self) -> str:
        return str(self.value)
