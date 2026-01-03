"""Jinja2 extension that resolves GitHub usernames from commit SHAs.

Adds a `github_username` filter for use in changelog templates. Requires
`GITHUB_REPOSITORY` and optionally `GITHUB_TOKEN` environment variables.
"""

import logging
import os

import httpx
from jinja2 import Environment
from jinja2.ext import Extension

__all__ = ["GitHubUsernameExtension"]

logger = logging.getLogger(__name__)


class GitHubUsernameExtension(Extension):
    """Adds a `github_username` filter to resolve commit authors via GitHub API."""

    def __init__(self, environment: Environment) -> None:
        super().__init__(environment)
        self._owner, self._repo = self._parse_repository()
        self._token = os.environ.get("GITHUB_TOKEN", "")
        environment.filters["github_username"] = self.get_github_username

        if self._owner and self._repo:
            logger.info("Initialized GitHub username extension for %s/%s", self._owner, self._repo)
        else:
            logger.warning("GITHUB_REPOSITORY not set, username resolution disabled")

    def _parse_repository(self) -> tuple[str, str]:
        owner = os.environ.get("GITHUB_REPOSITORY_OWNER", "")
        repo = os.environ.get("GITHUB_REPOSITORY_NAME", "")
        if owner and repo:
            return owner, repo

        full_repo = os.environ.get("GITHUB_REPOSITORY", "")
        if "/" in full_repo:
            return full_repo.split("/", 1)  # type: ignore[return-value]

        return "", ""

    def get_github_username(self, commit_sha: str) -> str | None:
        if not self._owner or not self._repo:
            return None

        url = f"https://api.github.com/repos/{self._owner}/{self._repo}/commits/{commit_sha}"
        headers = {"Accept": "application/vnd.github.v3+json"}
        if self._token:
            headers["Authorization"] = f"token {self._token}"

        try:
            with httpx.Client() as client:
                response = client.get(url, headers=headers, timeout=10.0)
                if response.status_code == 200:
                    username = response.json().get("author", {}).get("login")
                    logger.debug("Resolved %s to @%s", commit_sha[:7], username)
                    return username
                logger.warning("GitHub API returned %d for %s", response.status_code, commit_sha[:7])
        except httpx.HTTPError as e:
            logger.warning("GitHub API error for %s: %s", commit_sha[:7], e)
            return None
