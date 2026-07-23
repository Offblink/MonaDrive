"""GitHub API 封装 — 用户信息、仓库管理。"""

from github import Auth, Github, GithubException

from src.auth.token_store import get_token


class GitHubClient:
    """GitHub API 客户端，封装常用操作。"""

    def __init__(self):
        token = get_token()
        if not token:
            raise RuntimeError("未登录，请先完成 GitHub 授权")
        self._gh = Github(auth=Auth.Token(token))
        self._user = self._gh.get_user()

    @property
    def login(self) -> str:
        """GitHub 用户名。"""
        return self._user.login

    @property
    def avatar_url(self) -> str:
        """用户头像 URL。"""
        return self._user.avatar_url

    @property
    def name(self) -> str:
        """用户显示名 (可能为空)。"""
        return self._user.name or self._user.login

    def get_or_create_repo(self, repo_name: str, private: bool = True) -> dict:
        """获取或创建仓库。仓库必须为私有。

        Returns:
            {"full_name": "user/repo", "clone_url": "https://...", "html_url": "...", "private": True}
        """
        # 先尝试获取已有仓库
        try:
            repo = self._user.get_repo(repo_name)
            return {
                "full_name": repo.full_name,
                "clone_url": repo.clone_url,
                "html_url": repo.html_url,
                "private": repo.private,
            }
        except GithubException as e:
            if e.status != 404:
                raise

        # 不存在则创建
        repo = self._user.create_repo(
            name=repo_name,
            private=private,
            auto_init=True,  # 带 README.md 初始化
        )
        return {
            "full_name": repo.full_name,
            "clone_url": repo.clone_url,
            "html_url": repo.html_url,
            "private": repo.private,
        }

    def list_repos(self) -> list[dict]:
        """列出当前用户所有仓库。"""
        repos = []
        for repo in self._user.get_repos(sort="updated", direction="desc"):
            repos.append({
                "full_name": repo.full_name,
                "name": repo.name,
                "clone_url": repo.clone_url,
                "html_url": repo.html_url,
                "private": repo.private,
                "description": repo.description or "",
            })
        return repos

    def create_repo(self, repo_name: str, private: bool = True) -> dict:
        """创建新仓库。"""
        repo = self._user.create_repo(
            name=repo_name,
            private=private,
            auto_init=True,
        )
        return {
            "full_name": repo.full_name,
            "name": repo.name,
            "clone_url": repo.clone_url,
            "html_url": repo.html_url,
            "private": repo.private,
        }

    def rename_repo(self, old_name: str, new_name: str):
        """重命名仓库。"""
        repo = self._user.get_repo(old_name)
        repo.edit(name=new_name)

    def delete_repo(self, repo_name: str):
        """删除仓库。"""
        repo = self._user.get_repo(repo_name)
        repo.delete()
