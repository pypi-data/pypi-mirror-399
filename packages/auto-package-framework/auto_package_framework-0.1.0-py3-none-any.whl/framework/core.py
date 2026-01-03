"""核心工作流引擎"""

from pathlib import Path
from typing import Optional, Dict, Any
import shutil

from .config import Config
from .project_generator import ProjectGenerator
from .github_client import GitHubClient
from .pypi_client import PyPIClient
from .ai_developer import AIDeveloper


class AutoPackageFramework:
    """自动化包创建和发布框架核心类"""

    def __init__(self, config_path: Optional[str] = None):
        """
        初始化框架

        Args:
            config_path: 配置文件路径
        """
        self.config = Config(config_path)

        # 初始化各个组件
        self.project_generator = ProjectGenerator(self.config.template_path)
        self.github_client = None
        self.pypi_client = None
        self.ai_developer = None

        # 初始化GitHub客户端（如果配置了）
        if self.config.github_token:
            self.github_client = GitHubClient(
                token=self.config.github_token,
                username=self.config.github_username,
            )

        # 初始化PyPI客户端（如果配置了）
        if self.config.pypi_token or (
            self.config.pypi_username and self.config.pypi_password
        ):
            self.pypi_client = PyPIClient(
                username=self.config.pypi_username,
                password=self.config.pypi_password,
                token=self.config.pypi_token,
            )

        # 初始化AI开发者（如果配置了）
        if self.config.ai_api_key:
            self.ai_developer = AIDeveloper(
                provider=self.config.ai_provider,
                api_key=self.config.ai_api_key,
                model=self.config.ai_model,
            )

    def create_package(
        self,
        project_name: str,
        project_idea: str,
        output_path: Optional[Path] = None,
        github_repo: Optional[str] = None,
        auto_publish: bool = False,
        replacements: Optional[Dict[str, str]] = None,
    ) -> Dict[str, Any]:
        """
        创建并发布一个完整的Python包

        Args:
            project_name: 项目名称
            project_idea: 项目想法描述
            output_path: 输出路径（默认：当前目录下的项目名）
            github_repo: GitHub仓库名称（如果为None，使用project_name）
            auto_publish: 是否自动发布到PyPI
            replacements: 额外的替换映射

        Returns:
            操作结果字典
        """
        result = {
            "project_name": project_name,
            "success": False,
            "steps": [],
            "errors": [],
        }

        try:
            # 步骤1: 生成项目结构
            result["steps"].append("生成项目结构")
            if output_path is None:
                output_path = Path.cwd() / project_name

            replacements = replacements or {}
            if not replacements.get("USERNAME"):
                replacements["USERNAME"] = self.config.github_username or "USERNAME"

            project_path = self.project_generator.generate(
                project_name=project_name,
                output_path=output_path,
                replacements=replacements,
                project_idea=project_idea,
            )
            result["project_path"] = str(project_path)

            # 步骤2: AI生成代码
            if self.ai_developer:
                result["steps"].append("AI生成代码")
                self._generate_code_with_ai(project_path, project_name, project_idea)
            else:
                result["steps"].append("跳过AI代码生成（未配置AI）")

            # 步骤3: 创建GitHub仓库
            if self.github_client and github_repo:
                result["steps"].append("创建GitHub仓库")
                self._setup_github_repo(project_path, github_repo, project_idea)
                result["github_repo"] = f"https://github.com/{self.config.github_username}/{github_repo}"
            else:
                result["steps"].append("跳过GitHub创建（未配置或未指定仓库名）")

            # 步骤4: 发布到PyPI
            if auto_publish and self.pypi_client:
                result["steps"].append("发布到PyPI")
                self._publish_to_pypi(project_path)
                result["pypi_published"] = True
            else:
                result["steps"].append("跳过PyPI发布")

            result["success"] = True

        except Exception as e:
            result["errors"].append(str(e))
            result["success"] = False

        return result

    def _generate_code_with_ai(
        self, project_path: Path, project_name: str, project_idea: str
    ) -> None:
        """
        使用AI生成代码

        Args:
            project_path: 项目路径
            project_name: 项目名称
            project_idea: 项目想法
        """
        if not self.ai_developer:
            return

        # 读取PROJECT_IDEA.md作为上下文
        idea_file = project_path / "PROJECT_IDEA.md"
        existing_files = {}
        if idea_file.exists():
            existing_files["PROJECT_IDEA.md"] = idea_file.read_text(encoding="utf-8")

        # 读取pyproject.toml获取包名
        pyproject_file = project_path / "pyproject.toml"
        package_name = project_name.lower().replace("-", "_")
        if pyproject_file.exists():
            content = pyproject_file.read_text(encoding="utf-8")
            # 简单提取包名
            import re

            match = re.search(r'name = "([^"]+)"', content)
            if match:
                package_name = match.group(1)

        # 生成代码
        project_structure = {
            "name": project_name,
            "package_name": package_name,
            "python_version": "3.8+",
        }

        generated_files = self.ai_developer.generate_code(
            project_idea=project_idea,
            project_structure=project_structure,
            existing_files=existing_files,
        )

        # 写入生成的文件
        for file_path, code_content in generated_files.items():
            full_path = project_path / file_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(code_content, encoding="utf-8")

        # 生成README（如果AI支持）
        try:
            readme_content = self.ai_developer.generate_readme(project_name, project_idea)
            readme_file = project_path / "README.md"
            if readme_content:
                readme_file.write_text(readme_content, encoding="utf-8")
        except Exception as e:
            print(f"警告: 生成README失败: {e}")

    def _setup_github_repo(
        self, project_path: Path, repo_name: str, description: str
    ) -> None:
        """
        设置GitHub仓库

        Args:
            project_path: 项目路径
            repo_name: 仓库名称
            description: 仓库描述
        """
        if not self.github_client:
            return

        # 检查仓库是否已存在
        if self.github_client.repository_exists(repo_name):
            print(f"仓库 {repo_name} 已存在，跳过创建")
        else:
            # 创建仓库
            repo = self.github_client.create_repository(
                name=repo_name,
                description=description[:200] if description else "",
                private=False,
            )
            print(f"已创建GitHub仓库: {repo.html_url}")

        # 初始化本地Git仓库（如果还没有）
        from git import Repo

        if not (project_path / ".git").exists():
            repo = Repo.init(project_path)
            print(f"已初始化本地Git仓库")

        # 推送代码
        self.github_client.push_local_repo(project_path, repo_name)

    def _publish_to_pypi(self, project_path: Path) -> None:
        """
        发布到PyPI

        Args:
            project_path: 项目路径
        """
        if not self.pypi_client:
            return

        # 构建并发布
        self.pypi_client.publish(project_path, repository="pypi")
        print(f"已发布到PyPI")

