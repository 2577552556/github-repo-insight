import re
from typing import NamedTuple

from app.core.exceptions import InvalidURLError


class RepoInfo(NamedTuple):
    owner: str
    repo: str


GITHUB_URL_PATTERN = re.compile(
    r"^https?://(?:www\.)?github\.com/([^/]+)/([^/]+)/?$"
)


def parse_github_url(url: str) -> RepoInfo:
    """Parse a GitHub URL and extract owner and repo names.

    Args:
        url: A GitHub repository URL

    Returns:
        RepoInfo tuple containing (owner, repo)

    Raises:
        InvalidURLError: If the URL is not a valid GitHub repository URL
    """
    match = GITHUB_URL_PATTERN.match(url.strip())
    if not match:
        raise InvalidURLError(
            "Invalid GitHub URL format. Expected: https://github.com/{owner}/{repo}"
        )
    return RepoInfo(owner=match.group(1), repo=match.group(2))