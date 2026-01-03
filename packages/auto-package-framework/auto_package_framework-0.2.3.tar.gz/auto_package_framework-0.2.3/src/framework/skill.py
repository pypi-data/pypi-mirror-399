"""IDE Skill 接口 - 为 AI IDE 提供包的能力描述"""

from pathlib import Path
from typing import Dict, Any, List
import json


class SkillInterface:
    """IDE Skill 接口 - 提供包的能力描述给 AI IDE"""
    
    def __init__(self):
        """初始化 Skill 接口"""
        self.skill_info = self._load_skill_info()
    
    def _load_skill_info(self) -> Dict[str, Any]:
        """加载技能信息"""
        return {
            "name": "auto-package-framework",
            "version": "0.2.1",
            "description": "AI驱动的自动化Python包创建、开发和发布框架",
            "capabilities": [
                {
                    "name": "create_package",
                    "description": "创建新的Python包项目",
                    "parameters": {
                        "project_name": "项目名称（必需）",
                        "project_idea": "项目想法描述（必需）",
                        "output_path": "输出路径（可选）",
                        "github_repo": "GitHub仓库名称（可选）",
                        "auto_publish": "是否自动发布到PyPI（可选，默认False）",
                    },
                    "example": {
                        "python": """
from framework.core import AutoPackageFramework

framework = AutoPackageFramework()
result = framework.create_package(
    project_name="my-awesome-package",
    project_idea="一个用于自动化任务调度的Python包",
)
""",
                        "cli": """
auto-package create \\
    --project-name "my-package" \\
    --idea "我的项目描述"
""",
                    },
                },
                {
                    "name": "configure_api",
                    "description": "配置AI API密钥",
                    "parameters": {
                        "provider": "AI提供商（openai 或 anthropic）",
                        "api_key": "API密钥",
                        "model": "模型名称（可选）",
                    },
                    "example": {
                        "cli": """
auto-package config set-ai \\
    --provider openai \\
    --api-key "sk-xxxxx" \\
    --model "gpt-4"
""",
                    },
                },
                {
                    "name": "configure_github",
                    "description": "配置GitHub Token",
                    "parameters": {
                        "token": "GitHub Token",
                        "username": "GitHub用户名（可选）",
                    },
                    "example": {
                        "cli": """
auto-package config set-github \\
    --token "ghp_xxxxx" \\
    --username "your_username"
""",
                    },
                },
                {
                    "name": "configure_pypi",
                    "description": "配置PyPI Token",
                    "parameters": {
                        "token": "PyPI Token",
                        "username": "PyPI用户名（可选）",
                    },
                    "example": {
                        "cli": """
auto-package config set-pypi \\
    --token "pypi-xxxxx" \\
    --username "your_username"
""",
                    },
                },
            ],
            "usage_patterns": [
                {
                    "name": "基础使用",
                    "description": "仅生成项目结构",
                    "code": """
from framework.core import AutoPackageFramework

framework = AutoPackageFramework()
result = framework.create_package(
    project_name="test-package",
    project_idea="测试项目",
)
""",
                },
                {
                    "name": "完整流程",
                    "description": "生成项目 + GitHub + PyPI发布",
                    "code": """
from framework.core import AutoPackageFramework

framework = AutoPackageFramework()
result = framework.create_package(
    project_name="production-package",
    project_idea="生产环境使用的包",
    github_repo="production-package",
    auto_publish=True,
)
""",
                },
            ],
            "configuration": {
                "environment_variables": [
                    "GITHUB_TOKEN - GitHub Personal Access Token",
                    "PYPI_TOKEN - PyPI API Token",
                    "OPENAI_API_KEY - OpenAI API Key",
                    "ANTHROPIC_API_KEY - Anthropic API Key",
                ],
                "config_file": {
                    "path": "config.yaml",
                    "example": """
github:
  username: your_github_username
  token: your_github_token

pypi:
  token: pypi-xxxxx

ai:
  provider: openai
  api_key: your_api_key
  model: gpt-4
""",
                },
            },
            "installation": {
                "pip": "pip install auto-package-framework",
                "with_dev": "pip install auto-package-framework[dev]",
            },
        }
    
    def get_skill_info(self) -> Dict[str, Any]:
        """获取技能信息"""
        return self.skill_info
    
    def get_capabilities(self) -> List[Dict[str, Any]]:
        """获取能力列表"""
        return self.skill_info.get("capabilities", [])
    
    def get_capability(self, name: str) -> Dict[str, Any]:
        """获取特定能力的信息"""
        for cap in self.skill_info.get("capabilities", []):
            if cap.get("name") == name:
                return cap
        return {}
    
    def export_skill_file(self, output_path: Path) -> None:
        """
        导出技能文件（用于 IDE 集成）
        
        Args:
            output_path: 输出文件路径
        """
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(self.skill_info, f, indent=2, ensure_ascii=False)
    
    def get_skill_markdown(self) -> str:
        """获取技能描述的 Markdown 格式"""
        md = f"""# {self.skill_info['name']}

{self.skill_info['description']}

## 安装

```bash
{self.skill_info['installation']['pip']}
```

## 能力

"""
        for cap in self.skill_info.get("capabilities", []):
            md += f"### {cap['name']}\n\n"
            md += f"{cap['description']}\n\n"
            md += "**参数:**\n"
            for param, desc in cap.get("parameters", {}).items():
                md += f"- `{param}`: {desc}\n"
            md += "\n"
            
            if "example" in cap:
                if "python" in cap["example"]:
                    md += "**Python 示例:**\n"
                    md += f"```python\n{cap['example']['python']}\n```\n\n"
                if "cli" in cap["example"]:
                    md += "**CLI 示例:**\n"
                    md += f"```bash\n{cap['example']['cli']}\n```\n\n"
        
        return md


def get_skill_interface() -> SkillInterface:
    """获取技能接口实例"""
    return SkillInterface()

