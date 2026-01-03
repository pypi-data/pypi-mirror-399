"""项目生成器模块 - 从模板创建新项目（基于 Cookiecutter）"""

import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

try:
    import cookiecutter.main as cc_main
    import cookiecutter.generate as cc_generate
    COOKIECUTTER_AVAILABLE = True
except ImportError:
    COOKIECUTTER_AVAILABLE = False


class ProjectGenerator:
    """从模板生成新项目（使用 Cookiecutter）"""

    def __init__(self, template_path: Path):
        """
        初始化项目生成器

        Args:
            template_path: 模板目录路径
        """
        self.template_path = Path(template_path)
        if not self.template_path.exists():
            raise ValueError(f"模板路径不存在: {template_path}")

        # 检查是否是 cookiecutter 模板
        self.cookiecutter_json = self.template_path / "cookiecutter.json"
        self.is_cookiecutter = self.cookiecutter_json.exists()

        if not COOKIECUTTER_AVAILABLE:
            raise ImportError(
                "cookiecutter 未安装。请运行: pip install cookiecutter"
            )

        if not self.is_cookiecutter:
            raise ValueError(
                f"模板目录 {template_path} 不是有效的 cookiecutter 模板。"
                f"缺少 cookiecutter.json 文件。"
            )

    def generate(
        self,
        project_name: str,
        output_path: Path,
        replacements: Dict[str, str],
        project_idea: Optional[str] = None,
    ) -> Path:
        """
        生成新项目

        Args:
            project_name: 项目名称
            output_path: 输出路径
            replacements: 替换映射，如 {"github_username": "myuser", "author_name": "My Name"}
            project_idea: 项目想法描述（可选）

        Returns:
            生成的项目路径
        """
        output_path = Path(output_path)
        output_path.mkdir(parents=True, exist_ok=True)

        # 准备 cookiecutter 上下文
        context = self._prepare_context(project_name, replacements)

        # 使用 cookiecutter 生成项目
        # cookiecutter 会在 output_dir 下创建项目目录（使用 project_name）
        # 我们需要在 output_path 的父目录生成，然后移动到正确的位置
        parent_dir = output_path.parent
        expected_project_dir = parent_dir / project_name

        # 使用 cookiecutter 生成
        cc_generate.generate_files(
            repo_dir=str(self.template_path),
            context=context,
            output_dir=str(parent_dir),
            overwrite_if_exists=True,
        )

        # cookiecutter 会使用 project_name 作为目录名
        # 检查生成的目录
        if expected_project_dir.exists():
            # 如果生成的目录名与期望的不同，需要重命名
            if expected_project_dir != output_path:
                import shutil
                if output_path.exists():
                    shutil.rmtree(output_path)
                expected_project_dir.rename(output_path)
            else:
                output_path = expected_project_dir
        else:
            # 如果 cookiecutter 没有创建预期的目录，检查是否有其他目录
            # 这可能是因为模板结构不同
            # 在这种情况下，我们假设文件直接生成在 parent_dir 下
            # 需要手动处理（这种情况不应该发生，但为了健壮性）
            raise RuntimeError(
                f"Cookiecutter 未在预期位置创建项目目录: {expected_project_dir}"
            )

        # 如果提供了项目想法，写入PROJECT_IDEA.md
        if project_idea:
            self._write_project_idea(output_path, project_idea, project_name)

        return output_path

    def _prepare_context(
        self, project_name: str, replacements: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        准备 cookiecutter 上下文

        Args:
            project_name: 项目名称
            replacements: 用户提供的替换映射

        Returns:
            cookiecutter 上下文字典
        """
        # 读取 cookiecutter.json 获取默认值
        with open(self.cookiecutter_json, 'r', encoding='utf-8') as f:
            default_context = json.load(f)

        # 生成包名（从项目名转换）
        package_name = project_name.lower().replace("-", "_").replace(" ", "_")
        project_slug = project_name.lower().replace("_", "-").replace(" ", "-")

        # 计算主类名（从项目名生成，如 "my-package" -> "MyPackage"）
        main_class = "".join(
            word.capitalize() for word in project_name.replace("_", "-").split("-")
        )

        # 准备上下文，覆盖默认值
        context = {
            "project_name": project_name,
            "package_name": package_name,
            "project_slug": project_slug,
            "main_class": main_class,
            # 从 replacements 获取或使用默认值
            "github_username": replacements.get("USERNAME") or replacements.get("github_username") or default_context.get("github_username", "USERNAME"),
            "author_name": replacements.get("author") or replacements.get("author_name") or default_context.get("author_name", "Your Name"),
            "author_email": replacements.get("email") or replacements.get("author_email") or default_context.get("author_email", "your.email@example.com"),
            "project_description": replacements.get("PROJECT_DESCRIPTION") or replacements.get("project_description") or default_context.get("project_description", f"A Python package: {project_name}"),
            "main_functionality": replacements.get("MAIN_FUNCTIONALITY") or replacements.get("main_functionality") or default_context.get("main_functionality", "provides core functionality"),
            "additional_description": replacements.get("ADDITIONAL_DESCRIPTION") or replacements.get("additional_description") or default_context.get("additional_description", ""),
            "python_version": replacements.get("PYTHON_VERSION") or replacements.get("python_version") or default_context.get("python_version", "3.8"),
            "platforms": replacements.get("PLATFORMS") or replacements.get("platforms") or default_context.get("platforms", "Windows, macOS, Linux"),
            "license": replacements.get("LICENSE") or replacements.get("license") or default_context.get("license", "MIT"),
            "utility_class": replacements.get("UTILITY_CLASS") or replacements.get("utility_class") or default_context.get("utility_class", "Utility"),
            "integration_class": replacements.get("INTEGRATION_CLASS") or replacements.get("integration_class") or default_context.get("integration_class", "Integration"),
            "utility_function": replacements.get("UTILITY_FUNCTION") or replacements.get("utility_function") or default_context.get("utility_function", "utility_function"),
            "version": default_context.get("version", "0.1.0"),
        }

        # 合并用户提供的其他替换（覆盖上面的值）
        for key, value in replacements.items():
            if key not in ["USERNAME", "author", "email", "PROJECT_DESCRIPTION", 
                          "MAIN_FUNCTIONALITY", "ADDITIONAL_DESCRIPTION", 
                          "PYTHON_VERSION", "PLATFORMS", "LICENSE",
                          "UTILITY_CLASS", "INTEGRATION_CLASS", "UTILITY_FUNCTION"]:
                # 转换为小写下划线格式（cookiecutter 标准）
                cookiecutter_key = key.lower().replace("-", "_")
                context[cookiecutter_key] = value

        return context

    def _write_project_idea(
        self, output_path: Path, project_idea: str, project_name: str
    ) -> None:
        """
        写入项目想法到PROJECT_IDEA.md

        Args:
            output_path: 项目输出路径
            project_idea: 项目想法描述
            project_name: 项目名称
        """
        idea_file = output_path / "PROJECT_IDEA.md"

        # 如果文件已存在（从模板生成），读取并更新
        if idea_file.exists():
            content = idea_file.read_text(encoding="utf-8")
            # 在文件开头添加项目想法
            idea_section = f"""# Project Idea & Kickoff Guide

> **🎯 Purpose**: This is your project planning document.

## 📝 Project Concept

### What problem are we solving?

{project_idea}

---

"""
            # 如果内容中还没有项目想法部分，添加它
            if "What problem are we solving?" not in content:
                content = idea_section + content
            else:
                # 替换现有的项目想法部分
                import re
                pattern = r"### What problem are we solving?\s*\n\s*\n.*?(?=\n### |\n---|\Z)"
                content = re.sub(pattern, f"### What problem are we solving?\n\n{project_idea}", content, flags=re.DOTALL)
        else:
            # 使用基本模板
            content = f"""# Project Idea & Kickoff Guide

> **🎯 Purpose**: This is your project planning document.

## 📝 Project Concept

### What problem are we solving?

{project_idea}

### Why does this matter?

[Explain the significance and potential impact]

### Who is this for?

[Define target users/audience]

---

## 💡 Initial Ideas & Requirements

### Core Features (MVP)

- [ ] Feature 1: [Description]
- [ ] Feature 2: [Description]
- [ ] Feature 3: [Description]

---

## 🏗️ Architecture & Design Ideas

### High-Level Architecture

```
[Sketch your initial architecture ideas here]
```

### Technology Choices

- **Language**: Python 3.8+
- **Key Libraries**: [To be determined]
- **Storage**: [To be determined]

---

## 📊 Success Criteria

### Minimum Viable Product (MVP)

- [ ] Criterion 1: [Measurable goal]
- [ ] Criterion 2: [Measurable goal]

---

**Last Updated**: {datetime.now().strftime("%Y-%m-%d")}
**Status**: 🟡 Planning
"""

        idea_file.write_text(content, encoding="utf-8")
