"""Token 安全存储 — 使用系统凭据管理器 (Windows Credential Manager)。"""

import keyring

SERVICE_NAME = "MonaDrive"
ACCOUNT_NAME = "github_token"


def store_token(token: str) -> None:
    """存储 GitHub access token 到系统凭据管理器。"""
    keyring.set_password(SERVICE_NAME, ACCOUNT_NAME, token)


def get_token() -> str | None:
    """从系统凭据管理器读取 GitHub access token。"""
    return keyring.get_password(SERVICE_NAME, ACCOUNT_NAME)


def delete_token() -> None:
    """删除存储的 GitHub access token。"""
    try:
        keyring.delete_password(SERVICE_NAME, ACCOUNT_NAME)
    except keyring.errors.PasswordDeleteError:
        pass  # 已经不存在
