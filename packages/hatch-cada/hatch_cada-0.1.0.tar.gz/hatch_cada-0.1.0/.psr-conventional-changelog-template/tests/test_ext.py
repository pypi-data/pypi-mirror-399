import httpx
import pytest
from jinja2 import Environment
from pytest import MonkeyPatch
from pytest_httpx import HTTPXMock

from psr_templates.ext import GitHubUsernameExtension


@pytest.fixture
def clean_env(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.delenv("GITHUB_REPOSITORY", raising=False)
    monkeypatch.delenv("GITHUB_REPOSITORY_OWNER", raising=False)
    monkeypatch.delenv("GITHUB_REPOSITORY_NAME", raising=False)
    monkeypatch.delenv("GITHUB_TOKEN", raising=False)


@pytest.fixture
def github_env(monkeypatch: MonkeyPatch) -> None:
    monkeypatch.setenv("GITHUB_REPOSITORY", "owner/repo")
    monkeypatch.setenv("GITHUB_TOKEN", "test-token")


class TestGitHubUsernameExtension:
    def test_init_with_repository(self, github_env: None) -> None:
        env = Environment(extensions=[GitHubUsernameExtension])
        assert "github_username" in env.filters

    def test_init_without_repository(self, clean_env: None) -> None:
        env = Environment(extensions=[GitHubUsernameExtension])
        assert "github_username" in env.filters

    def test_returns_none_without_repository(self, clean_env: None) -> None:
        env = Environment(extensions=[GitHubUsernameExtension])
        result = env.filters["github_username"]("abc123")
        assert result is None

    def test_resolves_username(self, github_env: None, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url="https://api.github.com/repos/owner/repo/commits/abc123",
            json={"author": {"login": "testuser"}},
        )
        env = Environment(extensions=[GitHubUsernameExtension])
        result = env.filters["github_username"]("abc123")
        assert result == "testuser"

    def test_returns_none_on_api_error(self, github_env: None, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_response(
            url="https://api.github.com/repos/owner/repo/commits/abc123",
            status_code=404,
        )
        env = Environment(extensions=[GitHubUsernameExtension])
        result = env.filters["github_username"]("abc123")
        assert result is None

    def test_parses_owner_repo_separately(
        self, clean_env: None, monkeypatch: MonkeyPatch, httpx_mock: HTTPXMock
    ) -> None:
        monkeypatch.setenv("GITHUB_REPOSITORY_OWNER", "myowner")
        monkeypatch.setenv("GITHUB_REPOSITORY_NAME", "myrepo")
        httpx_mock.add_response(
            url="https://api.github.com/repos/myowner/myrepo/commits/abc123",
            json={"author": {"login": "testuser"}},
        )
        env = Environment(extensions=[GitHubUsernameExtension])
        result = env.filters["github_username"]("abc123")
        assert result == "testuser"

    def test_returns_none_on_network_error(self, github_env: None, httpx_mock: HTTPXMock) -> None:
        httpx_mock.add_exception(httpx.ConnectError("Connection failed"))
        env = Environment(extensions=[GitHubUsernameExtension])
        result = env.filters["github_username"]("abc123")
        assert result is None
