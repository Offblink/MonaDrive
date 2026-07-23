"""Git detection and auto-download of Portable Git (MinGit).

Checks for git on PATH, falls back to a bundled MinGit in %LOCALAPPDATA%/MonaDrive/git.
Downloads on first launch if neither exists.
"""

import shutil
import subprocess
import sys
import zipfile
from pathlib import Path

import requests

GIT_DIR = Path.home() / "AppData" / "Local" / "MonaDrive" / "git"
GIT_EXE = GIT_DIR / "cmd" / "git.exe"

# MinGit 64-bit — minimal portable Git, no admin needed
MINGIT_URL = (
    "https://github.com/git-for-windows/git/releases/download/"
    "v2.47.1.windows.2/MinGit-2.47.1-64-bit.zip"
)


def find_git() -> str | None:
    """Return git executable on PATH, or None."""
    git = shutil.which("git")
    if git:
        try:
            subprocess.run([git, "--version"], capture_output=True, timeout=5)
            return git
        except Exception:
            pass
    return None


def bundled_git() -> str | None:
    """Return bundled git path if it exists."""
    return str(GIT_EXE) if GIT_EXE.is_file() else None


def get_git() -> str | None:
    """Return available git path (PATH first, then bundled)."""
    return find_git() or bundled_git()


def _download_with_progress(url: str, dest: Path, callback) -> None:
    """Download file with progress callback(bytes_downloaded, total_bytes)."""
    resp = requests.get(url, stream=True, timeout=120)
    resp.raise_for_status()
    total = int(resp.headers.get("content-length", 0))
    downloaded = 0
    with open(dest, "wb") as f:
        for chunk in resp.iter_content(chunk_size=65536):
            f.write(chunk)
            downloaded += len(chunk)
            if callback:
                callback(downloaded, total)


def download_git(progress_callback=None) -> str:
    """Download + extract MinGit. Returns git.exe path. Raises on failure."""
    GIT_DIR.mkdir(parents=True, exist_ok=True)
    zip_path = GIT_DIR / "mingit.zip"

    try:
        _download_with_progress(MINGIT_URL, zip_path, progress_callback)
    except Exception as e:
        raise RuntimeError(f"Git 下载失败: {e}") from e

    try:
        with zipfile.ZipFile(zip_path) as zf:
            zf.extractall(GIT_DIR)
    except Exception as e:
        raise RuntimeError(f"Git 解压失败: {e}") from e
    finally:
        if zip_path.is_file():
            zip_path.unlink(missing_ok=True)

    if not GIT_EXE.is_file():
        raise RuntimeError("Git 安装异常：未找到 git.exe")

    return str(GIT_EXE)


def ensure_git(progress_callback=None) -> str:
    """Return a working git path — existing or freshly downloaded.

    Raises RuntimeError if download fails.
    """
    git = get_git()
    if git:
        return git
    return download_git(progress_callback)
