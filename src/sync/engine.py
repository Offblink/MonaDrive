"""Git 同步引擎 — clone, commit, push, pull。

使用 GitPython 进行所有 Git 操作，通过 token 认证访问私有仓库。
"""


import concurrent.futures
import os
from pathlib import Path

from git import GitCommandError, InvalidGitRepositoryError, Repo

from src.auth.token_store import get_token

os.environ.setdefault("GIT_LFS_SKIP_SMUDGE", "1")

_TIMEOUT_SECONDS = 15


def _git_timeout(fn, timeout=_TIMEOUT_SECONDS):
    executor = concurrent.futures.ThreadPoolExecutor(max_workers=1)
    future = executor.submit(fn)
    try:
        return future.result(timeout=timeout)
    except concurrent.futures.TimeoutError:
        executor.shutdown(wait=False, cancel_futures=True)
        raise SyncError(f"操作超时 ({timeout}s)，请检查网络连接")
    finally:
        executor.shutdown(wait=False)


class SyncError(Exception):
    """同步操作异常。"""
    pass


class SyncEngine:
    """Git 同步引擎。"""

    def __init__(self, local_path: str, repo_full_name: str):
        self.local_path = Path(local_path)
        self.repo_full_name = repo_full_name
        self._repo: Repo | None = None

    @property
    def repo(self) -> Repo:
        if self._repo is None:
            raise SyncError("仓库未初始化，请先执行 clone")
        return self._repo

    @property
    def is_cloned(self) -> bool:
        """检查本地是否已有克隆的仓库。"""
        git_dir = self.local_path / ".git"
        return git_dir.is_dir()

    def clone(self) -> None:
        """初始化本地仓库并关联远端。不自动拉取，由用户选择推或拉。"""
        token = get_token()
        if not token:
            raise SyncError("未登录，请先完成 GitHub 授权")

        clone_url = f"https://oauth2:{token}@github.com/{self.repo_full_name}.git"
        self.local_path.parent.mkdir(parents=True, exist_ok=True)

        if self.local_path.exists():
            if self.is_cloned:
                # 已有仓库 → 打开 + 更新 remote URL
                self._repo = Repo(self.local_path)
                origin = self._repo.remote("origin")
                origin.set_url(clone_url)
                self._disable_hooks()
                return
            # 目录存在但不是 git 仓库 → init + 关联远端（不拉取）
            self._repo = Repo.init(self.local_path)
            self._repo.create_remote("origin", clone_url)
            try:
                self._repo.git.branch("-M", "main")
            except Exception:
                pass
            # 仅 fetch 远端引用（不合并），用于显示 ahead/behind
            try:
                _git_timeout(lambda: self._repo.remote("origin").fetch(), timeout=15)
            except Exception:
                pass
            self._disable_hooks()
            return
        # 目录不存在 → 完整 clone
        self._repo = Repo.clone_from(clone_url, self.local_path)
        self._disable_hooks()

    def _verify_remote(self) -> bool:
        """验证远端仓库是否仍存在且可访问（ls-remote，轻量）。"""
        if self._repo is None:
            return False
        try:
            _git_timeout(lambda: self._repo.git.ls_remote("--heads", "origin"), timeout=10)
            return True
        except SyncError:
            return False
        except Exception:
            return False

    def _disable_hooks(self):
        """Disable git hooks to avoid 'hook not found' or LFS errors."""
        hooks_dir = self.local_path / ".git" / "hooks"
        if not hooks_dir.is_dir():
            return
        for f in list(hooks_dir.iterdir()):
            if f.is_file() and not f.name.endswith(".sample"):
                try:
                    f.unlink()
                except Exception:
                    try:
                        f.write_text("#!/bin/sh\nexit 0\n")
                    except Exception:
                        pass

    def _cleanup_locks(self):
        """Remove stale git lock files, rebase state, and LFS hooks."""
        for lock_name in ("index.lock", "HEAD.lock", "ORIG_HEAD.lock"):
            (self.local_path / ".git" / lock_name).unlink(missing_ok=True)
        (self.local_path / ".git" / "shallow.lock").unlink(missing_ok=True)
        rebase_dir = self.local_path / ".git" / "rebase-merge"
        if rebase_dir.is_dir():
            import shutil
            shutil.rmtree(rebase_dir, ignore_errors=True)
        if self._repo is not None:
            try:
                self._repo.git.rebase("--abort")
            except Exception:
                pass
    def commit_and_push(self, message: str = "auto sync", exclude: list[str] | None = None) -> str:
        """提交并推送本地变更到远端（本地优先）。"""
        if self._repo is None:
            raise SyncError("仓库未初始化，请先执行 clone")
        self._cleanup_locks()
        self._disable_hooks()

        has_new = self._has_changes()
        # 检查是否有未推送的提交
        ahead = 0
        origin = self._repo.remote("origin")
        try:
            _git_timeout(lambda: origin.fetch(), timeout=15)
            try:
                branch = self._repo.active_branch.name
            except Exception:
                branch = "main"
            remote_ref = f"origin/{branch}"
            if remote_ref in [r.name for r in origin.refs]:
                ahead = len(list(self._repo.iter_commits(f"{remote_ref}..{branch}")))
        except Exception:
            pass

        if not has_new and ahead == 0:
            return ""

        # stage + commit
        if has_new:
            if exclude:
                exclist = [e.replace("\\", "/") for e in exclude]
                for p in self.local_path.rglob("*"):
                    if ".git" in p.parts: continue
                    rel = str(p.relative_to(self.local_path)).replace("\\", "/")
                    if rel in exclist or any(rel.startswith(e + "/") for e in exclist):
                        continue
                    if p.is_file():
                        self._repo.git.add(str(p))
            else:
                self._repo.git.add(A=True)
            self._repo.index.commit(message)

        # push — 本地优先，用 force 覆盖远端
        try:
            try:
                branch = self._repo.active_branch.name
            except Exception:
                branch = "main"
            result = _git_timeout(lambda: origin.push(f"{branch}:main", force=True), timeout=60)
            if result:
                for info in result:
                    flags = int(info.flags)
                    if flags & (1024 | 2048 | 4096 | 8192 | 16384 | 32768):
                        raise SyncError(f"Push rejected: {info.summary.strip() or 'unknown error'}")
        except GitCommandError as e:
            msg = str(e)
            if "larger than" in msg or "exceed" in msg.lower() or "too large" in msg.lower():
                raise SyncError(
                    "Push rejected: file exceeds GitHub's 100 MB limit.\n"
                    "Consider using Git LFS: https://git-lfs.com"
                ) from e
            raise SyncError(f"Push failed: {msg}") from e

        return "pushed"

    def _ensure_up_to_date(self):
        """Fetch 远端并在落后时 pull --rebase。"""
        try:
            origin = self._repo.remote("origin")
            _git_timeout(lambda: origin.fetch())
            try:
                branch = self._repo.active_branch.name if not self._repo.head.is_detached else "main"
            except Exception:
                branch = "main"
            ref_names = [r.name for r in origin.refs]
            remote_branch = f"origin/{branch}"
            if remote_branch not in ref_names:
                # fallback: 本地是 master 但远端是 main（或反过来）
                for cand in ("origin/main", "origin/master"):
                    if cand in ref_names:
                        remote_branch = cand
                        break
                else:
                    return
            behind = list(self._repo.iter_commits(f"{branch}..{remote_branch}"))
            if behind:
                _git_timeout(lambda: self._repo.git.pull(
                    "--rebase", "origin", remote_branch.split("/", 1)[1],
                    allow_unrelated_histories=True))
        except GitCommandError as e:
            raise SyncError(f"同步远端变更失败: {e}") from e
    def _rollback_commit(self):
        """回滚最近一次 commit，变更回到暂存区以便用户重试。"""
        try:
            self._repo.git.reset("--soft", "HEAD~1")
        except Exception:
            pass

    def pull(self) -> str:
        """从远程拉取变更（远端优先，覆盖本地）。"""
        if self._repo is None:
            raise SyncError("仓库未初始化，请先执行 clone")
        self._cleanup_locks()
        self._disable_hooks()

        origin = self._repo.remote("origin")
        _git_timeout(lambda: origin.fetch(), timeout=30)

        # 检测远端分支
        ref_names = [r.name for r in origin.refs]
        branch = "main"
        if "origin/main" not in ref_names and "origin/master" in ref_names:
            branch = "master"

        # 强制 reset 到远端（远端优先）
        remote_ref = f"origin/{branch}"
        if remote_ref in ref_names:
            _git_timeout(lambda: self._repo.git.reset("--hard", remote_ref), timeout=30)
            return f"Reset to {remote_ref}"
        raise SyncError(f"远端分支 {remote_ref} 不存在")

    def get_status(self) -> dict:
        """获取当前仓库状态。

        Returns:
            {"changed": [...], "untracked": [...], "branch": "main", "behind": N, "ahead": N}
        """
        if self._repo is None or not self.is_cloned:
            return {
                "changed": [],
                "untracked": [],
                "branch": "",
                "behind": 0,
                "ahead": 0,
                "not_ready": True,
            }

        try:
            repo = self._repo
        except Exception:
            return {"not_ready": True}

        changed = [item.a_path for item in repo.index.diff(None)]
        untracked = repo.untracked_files
        try:
            branch = repo.active_branch.name if not repo.head.is_detached else "main"
        except Exception:
            branch = "main"

        # 获取 ahead/behind 计数
        behind, ahead, remote_error = 0, 0, False
        try:
            origin = repo.remote("origin")
            _git_timeout(lambda: origin.fetch(), timeout=15)
            ref_names = [r.name for r in origin.refs]
            remote_branch = f"origin/{branch}"
            if remote_branch not in ref_names:
                for cand in ("origin/main", "origin/master"):
                    if cand in ref_names:
                        remote_branch = cand
                        break
            if remote_branch in ref_names:
                behind = len(list(repo.iter_commits(f"{branch}..{remote_branch}")))
                ahead = len(list(repo.iter_commits(f"{remote_branch}..{branch}")))
        except Exception:
            remote_error = True

        return {
            "changed": changed,
            "untracked": untracked,
            "branch": branch,
            "behind": behind,
            "ahead": ahead,
            "not_ready": False,
            "remote_error": remote_error,
        }

    def _has_changes(self) -> bool:
        """检查是否有待提交的变更。"""
        if self._repo is None:
            return False
        return bool(
            self._repo.index.diff(None)  # 已修改
            or self._repo.untracked_files  # 新文件
            or self._repo.index.diff("HEAD")  # 已暂存
        )
