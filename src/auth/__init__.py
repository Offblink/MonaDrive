"""GitHub OAuth 配置 — 从配置文件动态加载。"""

import json
from pathlib import Path

# OAuth 流程参数
REDIRECT_HOST = "127.0.0.1"
REDIRECT_PORT = 0  # 0 = 系统自动分配端口

# GitHub API 端点
AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
TOKEN_URL = "https://github.com/login/oauth/access_token"

# 配置文件路径
CONFIG_DIR = "~/.monadrive"
CONFIG_FILE = "config.json"


def _config_path() -> Path:
    config_dir = Path(CONFIG_DIR).expanduser()
    config_dir.mkdir(parents=True, exist_ok=True)
    return config_dir / CONFIG_FILE


def load_config() -> dict:
    """加载完整配置文件。"""
    path = _config_path()
    if path.is_file():
        return json.loads(path.read_text(encoding="utf-8"))
    return {}


def save_config(data: dict) -> None:
    """保存完整配置文件。"""
    _config_path().write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def get_github_config() -> dict:
    """获取 GitHub OAuth 配置。"""
    cfg = load_config()
    return cfg.get("github", {})


def set_github_config(client_id: str, client_secret: str) -> None:
    """保存 GitHub OAuth 配置。"""
    cfg = load_config()
    cfg["github"] = {
        "client_id": client_id,
        "client_secret": client_secret,
    }
    save_config(cfg)
