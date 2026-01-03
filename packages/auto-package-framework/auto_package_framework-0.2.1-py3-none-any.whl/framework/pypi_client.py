"""PyPI发布客户端模块"""

import subprocess
import sys
from pathlib import Path
from typing import Optional
import os


class PyPIClient:
    """PyPI发布客户端"""

    def __init__(
        self,
        username: Optional[str] = None,
        password: Optional[str] = None,
        token: Optional[str] = None,
    ):
        """
        初始化PyPI客户端

        Args:
            username: PyPI用户名（如果使用密码认证）
            password: PyPI密码（如果使用密码认证）
            token: PyPI API Token（推荐方式）
        """
        self.username = username
        self.password = password
        self.token = token

        if not token and not (username and password):
            raise ValueError("必须提供token或username+password")

    def build_package(self, project_path: Path) -> Path:
        """
        构建Python包

        Args:
            project_path: 项目路径

        Returns:
            构建产物目录路径
        """
        dist_path = project_path / "dist"

        # 清理旧的构建产物
        if dist_path.exists():
            import shutil

            shutil.rmtree(dist_path)

        # 运行构建命令
        result = subprocess.run(
            [sys.executable, "-m", "build"],
            cwd=project_path,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            raise RuntimeError(f"构建失败: {result.stderr}")

        return dist_path

    def publish(
        self,
        project_path: Path,
        repository: str = "pypi",
        skip_build: bool = False,
    ) -> None:
        """
        发布包到PyPI

        Args:
            project_path: 项目路径
            repository: 仓库名称（pypi或testpypi）
            skip_build: 是否跳过构建（如果已经构建过）
        """
        # 构建包
        if not skip_build:
            self.build_package(project_path)

        # 准备环境变量
        env = os.environ.copy()

        if self.token:
            # 使用Token认证
            env["TWINE_USERNAME"] = "__token__"
            env["TWINE_PASSWORD"] = self.token
        else:
            # 使用用户名密码认证
            env["TWINE_USERNAME"] = self.username
            env["TWINE_PASSWORD"] = self.password

        # 运行上传命令
        dist_path = project_path / "dist"
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "twine",
                "upload",
                f"--repository={repository}",
                str(dist_path / "*"),
            ],
            cwd=project_path,
            env=env,
            capture_output=True,
            text=True,
        )

        if result.returncode != 0:
            raise RuntimeError(f"发布失败: {result.stderr}")

    def publish_to_testpypi(
        self, project_path: Path, skip_build: bool = False
    ) -> None:
        """
        发布到TestPyPI（用于测试）

        Args:
            project_path: 项目路径
            skip_build: 是否跳过构建
        """
        self.publish(project_path, repository="testpypi", skip_build=skip_build)

