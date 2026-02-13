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


def _get_release_info(
    repo: str,
    tag: str,
    asset_name: str,
    headers: dict[str, str],
) -> tuple[str, str]:
    """Query the GitHub Releases API. Returns (download_url, version_id)."""
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
    # Use the asset's updated_at timestamp as the version identifier -- it
    # changes on every new upload, unlike the release body which is free-form.
    version_id: str = asset.get("updated_at") or release.get("body", "").strip() or "unknown"

    return download_url, version_id


def _download_and_extract(
    download_url: str,
    cache_dir: Path,
    github_token: str | None,
) -> None:
    """Download tarball and extract into cache_dir."""
    dl_headers: dict[str, str] = {"Accept": "application/octet-stream"}
    if github_token:
        dl_headers["Authorization"] = f"token {github_token}"

    with tempfile.NamedTemporaryFile(suffix=".tar.gz", delete=False) as tmp:
        tmp_path = Path(tmp.name)
        with httpx.stream("GET", download_url, headers=dl_headers, follow_redirects=True, timeout=120) as stream:
            for chunk in stream.iter_bytes():
                tmp.write(chunk)

    if cache_dir.exists():
        shutil.rmtree(cache_dir)
    cache_dir.mkdir(parents=True, exist_ok=True)

    with tarfile.open(tmp_path) as tar:
        tar.extractall(path=cache_dir)

    tmp_path.unlink(missing_ok=True)


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

    Always checks for a newer version unless *force* is set (which re-downloads
    unconditionally).  Falls back to a stale cache on network failure.
    """
    marker = cache_dir / ".version"
    index = cache_dir / "index.html"

    headers: dict[str, str] = {"Accept": "application/vnd.github+json"}
    if github_token:
        headers["Authorization"] = f"token {github_token}"

    try:
        download_url, version_id = _get_release_info(repo, tag, asset_name, headers)

        # If cache is current and not forcing, skip the download.
        if not force and marker.exists() and marker.read_text().strip() == version_id:
            logger.info("Frontend is up to date (%s)", version_id)
            return cache_dir

        logger.info("Downloading frontend build (%s) ...", version_id)
        _download_and_extract(download_url, cache_dir, github_token)
        marker.write_text(version_id)

        logger.info("Frontend build cached in %s", cache_dir)
        return cache_dir

    except (httpx.HTTPError, Exception) as exc:
        logger.warning("Failed to check for frontend updates: %s", exc)

        if index.exists():
            logger.warning("Falling back to stale cached frontend in %s", cache_dir)
            return cache_dir

        raise SystemExit(
            "No cached frontend available and download failed. "
            "Check your network connection or build the frontend manually.\n"
            f"  Error: {exc}"
        ) from exc
