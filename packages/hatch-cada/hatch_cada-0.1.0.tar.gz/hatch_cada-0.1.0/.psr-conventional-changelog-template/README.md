# Python Semantic Release Conventional Changelog Templates

Changelog templates for [Python Semantic Release](https://python-semantic-release.readthedocs.io/).

## Example

Given the following commits using the [Conventional Commits](https://www.conventionalcommits.org/) format:

```
feat(api)!: remove deprecated `sync` method (#45)

BREAKING CHANGE: Use `async_sync` instead.
```

````
feat(auth): add OAuth2 support (#42)

This adds full OAuth2 flow support:

```python
client.auth.oauth2(provider="github")
```

Closes #12

Co-authored-by: Charlie <charlie@example.com>
````

```
fix(parser): handle empty input gracefully
```

The template generates this changelog:

````markdown
# v2.0.0 (2024-12-15)

### :warning: Breaking Changes :warning:

- **api:** Remove deprecated `sync` method by [@alice](https://github.com/alice) ([a1b2c3d](https://github.com/org/repo/commit/a1b2c3d)) in [#45](https://github.com/org/repo/pull/45)

    **Migration:** Use `async_sync` instead.

### Features

- **auth:** Add OAuth2 support by [@bob](https://github.com/bob), Charlie ([f4e5d6c](https://github.com/org/repo/commit/f4e5d6c)) in [#42](https://github.com/org/repo/pull/42), closes [#12](https://github.com/org/repo/issues/12)

    This adds full OAuth2 flow support:

    ```python
    client.auth.oauth2(provider="github")
    ```

### Bug Fixes

- **parser:** Handle empty input gracefully by [@alice](https://github.com/alice) ([b2c3d4e](https://github.com/org/repo/commit/b2c3d4e))
````

The commit format is `type(scope): description` where:

- `type` determines the changelog section (`feat` → Features, `fix` → Bug Fixes, etc.)
- `scope` is optional and appears in bold
- `description` is automatically sentence cased (`add OAuth2` → `Add OAuth2`)
- `!` after the scope or `BREAKING CHANGE:` in the body triggers a major version bump
- `#N` in the subject links to a PR, `Closes #N` in the body links to issues
- `Co-authored-by:` trailers are included in author attribution

## Installation

The official PSR GitHub action runs in a Docker container, which doesn't support custom Jinja extensions. Instead, run PSR directly with the CLI.

### 1. Configure `pyproject.toml`

```toml
[tool.semantic_release]
commit_author = "github-actions[bot] <41898282+github-actions[bot]@users.noreply.github.com>"

[tool.semantic_release.remote]
type = "github"
ignore_token_for_push = true

[tool.semantic_release.changelog]
template_dir = ".psr-templates/src/psr_templates/templates"

[tool.semantic_release.changelog.environment]
extensions = ["psr_templates.ext:GitHubUsernameExtension"]
```

### 2. Set up deploy key (for branch protection)

If your repository has branch protection rules, you need a deploy key to bypass them:

```bash
# Generate deploy key
ssh-keygen -t ed25519 -C "psr-deploy" -N "" -f deploy-key
```

Then in your GitHub repository:
1. **Settings → Deploy keys** → Add `deploy-key.pub` with write access
2. **Settings → Secrets** → Add `DEPLOY_KEY` with the private key content
3. **Settings → Rules → Rulesets** → Add "Deploy keys" to bypass list

### 3. Create release workflow

```yaml
name: Release

on:
  workflow_dispatch:

jobs:
  release:
    runs-on: ubuntu-latest
    permissions:
      contents: write

    steps:
      - uses: actions/checkout@v6
        with:
          fetch-depth: 0
          ssh-key: ${{ secrets.DEPLOY_KEY }}

      - uses: actions/checkout@v6
        with:
          repository: bilelomrani1/psr-templates
          path: .psr-templates

      - uses: astral-sh/setup-uv@v7
        with:
          enable-cache: true

      - name: Install dependencies
        run: |
          uv venv
          uv pip install python-semantic-release
          uv pip install .psr-templates

      - name: Run semantic-release
        env:
          GH_TOKEN: ${{ secrets.GITHUB_TOKEN }}
          GIT_COMMIT_AUTHOR: github-actions[bot] <41898282+github-actions[bot]@users.noreply.github.com>
        run: uv run semantic-release version
```

## Environment Variables

The `github_username` filter requires these environment variables (automatically available in GitHub Actions):

- `GITHUB_REPOSITORY` - Repository in `owner/repo` format
- `GH_TOKEN` - GitHub token for API access (optional but recommended to avoid rate limits)

## Commit Types

The template supports these conventional commit types:

- `feat` - Features
- `fix` - Bug Fixes
- `perf` - Performance Improvements
- `docs` - Documentation
- `refactor` - Refactoring
- `test` - Testing
- `build` - Build System
- `ci` - Continuous Integration
- `chore` - Chores
- `style` - Code Style

## Development

```bash
# Setup
uv run poe setup

# Run tests
uv run poe test

# Run linter and type checker
uv run poe check

# Format code
uv run poe format
```
