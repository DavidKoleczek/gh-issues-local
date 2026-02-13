"""Download and cache the frontend build from GitHub Releases."""

import logging
from pathlib import Path
import shutil
import tarfile
import tempfile

import httpx

logger = logging.getLogger(__name__)

# Defaults -- override via environment or CLI flags.
FRONTEND_REPO = "DavidKoleczek/gh-issues-local"
FRONTEND_RELEASE_TAG = "frontend-latest"
FRONTEND_ASSET_NAME = "frontend-dist.tar.gz"


def fetch_frontend(
    cache_dir: Path,
    *,
    repo: str = FRONTEND_REPO,
    tag: str = FRONTEND_RELEASE_TAG,
    asset_name: str = FRONTEND_ASSET_NAME,
    github_token: str | None = None,
    force: bool = False,
) -> Path:
    """Download the frontend tarball from GitHub Releases and cache it locally.

    Returns the path to the directory containing the extracted frontend files.
    Falls back to a stale cache on network failure.
    """
    marker = cache_dir / ".version"
    index = cache_dir / "index.html"

    if index.exists() and not force:
        logger.info("Using cached frontend build from %s", cache_dir)
        return cache_dir

    headers: dict[str, str] = {"Accept": "application/vnd.github+json"}
    if github_token:
        headers["Authorization"] = f"token {github_token}"

    try:
        # 1. Query the GitHub Releases API.
        api_url = f"https://api.github.com/repos/{repo}/releases/tags/{tag}"
        response = httpx.get(api_url, headers=headers, timeout=30)

        if response.status_code == 404:
            raise RuntimeError("Release not found. Has the GitHub Action run at least once?")
        if response.status_code in (401, 403):
            raise RuntimeError("Authentication required. Set GITHUB_TOKEN env var.")
        if response.status_code != 200:
            raise RuntimeError(f"GitHub API error {response.status_code}: {response.text}")

        release = response.json()

        asset = next(
            (a for a in release.get("assets", []) if a["name"] == asset_name),
            None,
        )
        if asset is None:
            available = [a["name"] for a in release.get("assets", [])]
            raise RuntimeError(f"Asset '{asset_name}' not found in release '{tag}'. Available: {available}")

        download_url: str = asset["browser_download_url"]
        commit_sha: str = release.get("body", "").strip() or "unknown"

        # 2. Download the tarball.
        dl_headers: dict[str, str] = {"Accept": "application/octet-stream"}
        if github_token:
            dl_headers["Authorization"] = f"token {github_token}"

        with tempfile.NamedTemporaryFile(suffix=".tar.gz", delete=False) as tmp:
            tmp_path = Path(tmp.name)
            with httpx.stream("GET", download_url, headers=dl_headers, follow_redirects=True, timeout=120) as stream:
                for chunk in stream.iter_bytes():
                    tmp.write(chunk)

        # 3. Clear old cache and extract.
        if cache_dir.exists():
            shutil.rmtree(cache_dir)
        cache_dir.mkdir(parents=True, exist_ok=True)

        with tarfile.open(tmp_path) as tar:
            tar.extractall(path=cache_dir)

        tmp_path.unlink(missing_ok=True)

        # 4. Write version marker.
        marker.write_text(commit_sha)

        logger.info("Frontend build downloaded and cached in %s (commit: %s)", cache_dir, commit_sha)
        return cache_dir

    except (httpx.HTTPError, Exception) as exc:
        logger.warning("Failed to download frontend build: %s", exc)

        if index.exists():
            logger.warning("Falling back to stale cached frontend in %s", cache_dir)
            return cache_dir

        raise SystemExit(
            "No cached frontend available and download failed. "
            "Check your network connection or build the frontend manually.\n"
            f"  Error: {exc}"
        ) from exc
