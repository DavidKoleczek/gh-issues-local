---
name: update-dependencies
description: Update all dependencies in pyproject.toml and pre-commit hooks to their latest versions. Bumps minor/patch versions, flags major version upgrades for user review, and runs checks to verify nothing breaks.
---

# Update Dependencies

## pyproject.toml

1. Read `pyproject.toml`. Note the versioning convention: dependencies pin below the next major version (e.g. `"openai[aiohttp]>=2.9,<3.0"` will never auto-upgrade to v3.x). You will only be updating minor/patch versions. Dev dependencies (under `[dependency-groups]`) do not need the major-version ceiling. Do not touch `uv_build`, `build-system`, or anything outside `[project] dependencies` and `[dependency-groups]`.
2. For each dependency, go to its PyPI release history page. For example, for the `openai` package that is: `https://pypi.org/project/openai/#history`. Get the latest release version (ignore pre-releases, alphas, betas, and release candidates).
3. Bump the dependency in `pyproject.toml`. For example, if the current spec is `>=1.5,<2.0` and the latest PyPI version is 1.11, change it to `>=1.11,<2.0`. For dev dependencies without a ceiling, bump the floor the same way (e.g. `>=9.0` to `>=9.3`).
4. If a dependency has a major version upgrade available (e.g. latest is v3.x but the spec caps at `<3.0`), do NOT make the change. Instead, collect all such cases and report them to the user at the end.
5. Run checks from the project root to make sure nothing broke:
   ```
   uv run ruff format && uv run ruff check --fix && uv run ty check
   ```
6. Run `uv sync --all-extras --all-groups` to update the lock file.

## Pre-commit Hooks

1. Read `.pre-commit-config.yaml`.
2. For each hook repo that has a `rev:` field pointing to a remote repository (skip `repo: local` entries):
   - Go to the repo's releases/tags page on GitHub. For example, for `https://github.com/astral-sh/ruff-pre-commit`, check `https://github.com/astral-sh/ruff-pre-commit/releases`.
   - Find the latest release tag.
   - Bump the `rev:` value in `.pre-commit-config.yaml` to that tag.
3. After bumping, run `prek run --all-files` to verify the updated hooks work.
