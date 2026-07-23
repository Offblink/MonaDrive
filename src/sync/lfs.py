"""Git LFS 大文件检测。

在提交前扫描变更文件，检测超过阈值的大文件，提示用户启用 Git LFS。
"""

import os
from pathlib import Path

# 默认大文件阈值 (字节)
LFS_THRESHOLD = 50 * 1024 * 1024  # 50 MB

# Git LFS 常用追踪模式
LFS_TRACK_PATTERNS = [
    "*.psd", "*.zip", "*.tar.gz", "*.tgz", "*.7z", "*.rar",
    "*.mp4", "*.mov", "*.avi", "*.mkv", "*.wmv",
    "*.wav", "*.mp3", "*.flac", "*.aac",
    "*.iso", "*.dmg", "*.vmdk", "*.ova",
    "*.ai", "*.sketch", "*.fig",
    "*.model", "*.weights", "*.h5", "*.onnx", "*.pth", "*.ckpt",
    "*.bin", "*.dat", "*.pak",
    "*.dll", "*.so", "*.dylib", "*.exe",
]


def scan_large_files(path: str, threshold: int = LFS_THRESHOLD) -> list[dict]:
    """扫描目录下超过阈值的大文件。

    Args:
        path: 要扫描的目录路径
        threshold: 文件大小阈值 (字节)，默认 50MB

    Returns:
        [{"path": "relative/path", "size": 104857600, "size_str": "100.0 MB"}, ...]
    """
    root = Path(path)
    if not root.is_dir():
        return []

    large_files = []
    for entry in root.rglob("*"):
        if not entry.is_file():
            continue
        # 跳过 .git 目录
        if ".git" in entry.parts:
            continue
        try:
            size = entry.stat().st_size
            if size >= threshold:
                large_files.append({
                    "path": str(entry.relative_to(root)),
                    "size": size,
                    "size_str": _format_size(size),
                })
        except OSError:
            continue

    return sorted(large_files, key=lambda f: f["size"], reverse=True)


def get_lfs_suggestion(ext: str) -> str | None:
    """根据文件扩展名，返回建议的 LFS track 命令。"""
    ext = ext.lower()
    # 精确匹配
    for pattern in LFS_TRACK_PATTERNS:
        if pattern.startswith("*.") and f".{pattern[2:]}" == ext:
            return f'git lfs track "{pattern}"'
    # 按扩展名建议
    return f'git lfs track "*{ext}"'


def is_lfs_initialized(repo_path: str) -> bool:
    """检查仓库是否已初始化 Git LFS。"""
    gitattributes = Path(repo_path) / ".gitattributes"
    if not gitattributes.is_file():
        return False
    content = gitattributes.read_text(encoding="utf-8", errors="ignore")
    return "filter=lfs" in content


def init_lfs(repo_path: str) -> bool:
    """在仓库中初始化 Git LFS。

    需要系统中已安装 git-lfs。返回是否成功。
    """
    import subprocess
    try:
        subprocess.run(
            ["git", "lfs", "install"],
            cwd=repo_path,
            capture_output=True,
            timeout=30,
        )
        return True
    except Exception:
        return False


def track_lfs_patterns(repo_path: str, patterns: list[str]) -> None:
    """在仓库中配置 LFS 追踪规则。"""
    import subprocess
    for pattern in patterns:
        subprocess.run(
            ["git", "lfs", "track", pattern],
            cwd=repo_path,
            capture_output=True,
            timeout=10,
        )


def _format_size(size: int) -> str:
    """格式化文件大小为人可读的字符串。"""
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size < 1024:
            return f"{size:.1f} {unit}"
        size /= 1024
    return f"{size:.1f} PB"
