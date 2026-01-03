"""GitHub API客户端模块"""

from pathlib import Path
from typing import Optional, Dict, Any
from github import Github, Repository, ContentFile
from git import Repo, Actor
import base64


class GitHubClient:
    """GitHub API客户端"""

    def __init__(self, token: str, username: Optional[str] = None):
        """
        初始化GitHub客户端

        Args:
            token: GitHub Personal Access Token
            username: GitHub用户名（可选，用于Git提交）
        """
        self.github = Github(token)
        self.username = username or self.github.get_user().login

    def create_repository(
        self,
        name: str,
        description: str = "",
        private: bool = False,
        auto_init: bool = False,
    ) -> Repository:
        """
        创建GitHub仓库

        Args:
            name: 仓库名称
            description: 仓库描述
            private: 是否私有
            auto_init: 是否自动初始化README

        Returns:
            创建的仓库对象
        """
        user = self.github.get_user()
        repo = user.create_repo(
            name=name,
            description=description,
            private=private,
            auto_init=auto_init,
        )
        return repo

    def repository_exists(self, name: str) -> bool:
        """
        检查仓库是否存在

        Args:
            name: 仓库名称

        Returns:
            是否存在
        """
        try:
            user = self.github.get_user()
            user.get_repo(name)
            return True
        except Exception:
            return False

    def push_local_repo(
        self, local_path: Path, repo_name: str, branch: str = "main"
    ) -> None:
        """
        推送本地仓库到GitHub

        Args:
            local_path: 本地仓库路径
            repo_name: GitHub仓库名称
            branch: 分支名称
        """
        repo = Repo(local_path)

        # 确保在正确的分支
        if branch not in [head.name for head in repo.heads]:
            repo.git.checkout("-b", branch)

        # 配置远程仓库
        remote_url = f"https://{self.github._Github__requester._Requester__authorizationHeader.split()[1]}@github.com/{self.username}/{repo_name}.git"
        if "origin" in repo.remotes:
            repo.remote("origin").set_url(remote_url)
        else:
            repo.create_remote("origin", remote_url)

        # 添加所有文件
        repo.git.add(A=True)

        # 提交
        if repo.is_dirty(untracked_files=True) or len(list(repo.index.iter_blobs())) > 0:
            actor = Actor(self.username, f"{self.username}@users.noreply.github.com")
            repo.index.commit(
                "chore: initial commit from auto-package-framework",
                author=actor,
                committer=actor,
            )

        # 推送
        repo.git.push("origin", branch, force=False)

    def create_file_in_repo(
        self,
        repo: Repository,
        path: str,
        content: str,
        message: str,
        branch: str = "main",
    ) -> None:
        """
        在仓库中创建文件

        Args:
            repo: 仓库对象
            path: 文件路径
            content: 文件内容
            message: 提交消息
            branch: 分支名称
        """
        try:
            # 尝试获取现有文件
            existing_file = repo.get_contents(path, ref=branch)
            # 如果存在，更新
            repo.update_file(
                path=path,
                message=message,
                content=content,
                sha=existing_file.sha,
                branch=branch,
            )
        except Exception:
            # 如果不存在，创建
            repo.create_file(
                path=path,
                message=message,
                content=content,
                branch=branch,
            )

    def create_release(
        self,
        repo: Repository,
        tag: str,
        name: str,
        body: str,
        draft: bool = False,
        prerelease: bool = False,
    ) -> Any:
        """
        创建GitHub Release

        Args:
            repo: 仓库对象
            tag: 标签名称
            name: Release名称
            body: Release描述
            draft: 是否为草稿
            prerelease: 是否为预发布

        Returns:
            Release对象
        """
        return repo.create_git_release(
            tag=tag,
            name=name,
            message=body,
            draft=draft,
            prerelease=prerelease,
        )

