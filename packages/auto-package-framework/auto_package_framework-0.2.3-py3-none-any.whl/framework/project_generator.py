"""项目生成器模块 - 从模板创建新项目"""

import shutil
from pathlib import Path
from typing import Dict, Any, Optional
import re
from jinja2 import Environment, FileSystemLoader, select_autoescape


class ProjectGenerator:
    """从模板生成新项目"""

    def __init__(self, template_path: Path):
        """
        初始化项目生成器

        Args:
            template_path: 模板目录路径
        """
        self.template_path = Path(template_path)
        if not self.template_path.exists():
            raise ValueError(f"模板路径不存在: {template_path}")

        # 初始化Jinja2环境
        self.env = Environment(
            loader=FileSystemLoader(str(self.template_path)),
            autoescape=select_autoescape(["html", "xml"]),
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
            replacements: 替换映射，如 {"USERNAME": "myuser", "PROJECT_NAME": "mypackage"}
            project_idea: 项目想法描述（可选）

        Returns:
            生成的项目路径
        """
        output_path = Path(output_path)
        output_path.mkdir(parents=True, exist_ok=True)

        # 准备替换映射
        replacements = self._prepare_replacements(project_name, replacements)

        # 复制模板文件
        self._copy_template_files(output_path, replacements)

        # 如果提供了项目想法，写入PROJECT_IDEA.md
        if project_idea:
            self._write_project_idea(output_path, project_idea, project_name)

        return output_path

    def _prepare_replacements(
        self, project_name: str, replacements: Dict[str, str]
    ) -> Dict[str, str]:
        """
        准备替换映射

        Args:
            project_name: 项目名称
            replacements: 用户提供的替换映射

        Returns:
            完整的替换映射
        """
        # 生成包名（从项目名转换）
        package_name = project_name.lower().replace("-", "_").replace(" ", "_")

        # 计算主类名（从项目名生成，如 "my-package" -> "MyPackage"）
        main_class = "".join(word.capitalize() for word in project_name.replace("_", "-").split("-"))
        
        # 默认替换映射
        default_replacements = {
            "[Project Name]": project_name,
            "PROJECT_NAME": project_name.upper().replace("-", "_"),
            "project-name": project_name.lower().replace("_", "-"),
            "your-package-name": package_name,
            "your_package_name": package_name,
            "USERNAME": replacements.get("USERNAME", "USERNAME"),
            "your.email@example.com": replacements.get("email", "your.email@example.com"),
            "Your Name": replacements.get("author", "Your Name"),
            # llms.txt 模板变量
            "PACKAGE_NAME": package_name,
            "PROJECT_DESCRIPTION": replacements.get("PROJECT_DESCRIPTION", f"A Python package: {project_name}"),
            "MAIN_FUNCTIONALITY": replacements.get("MAIN_FUNCTIONALITY", "provides core functionality"),
            "ADDITIONAL_DESCRIPTION": replacements.get("ADDITIONAL_DESCRIPTION", ""),
            "PYTHON_VERSION": replacements.get("PYTHON_VERSION", "3.8"),
            "PLATFORMS": replacements.get("PLATFORMS", "Windows, macOS, Linux"),
            "LICENSE": replacements.get("LICENSE", "MIT"),
            "MAIN_CLASS": main_class,
            "UTILITY_CLASS": replacements.get("UTILITY_CLASS", "Utility"),
            "INTEGRATION_CLASS": replacements.get("INTEGRATION_CLASS", "Integration"),
            "UTILITY_FUNCTION": replacements.get("UTILITY_FUNCTION", "utility_function"),
        }

        # 合并用户提供的替换
        default_replacements.update(replacements)

        return default_replacements

    def _copy_template_files(
        self, output_path: Path, replacements: Dict[str, str]
    ) -> None:
        """
        复制并处理模板文件

        Args:
            output_path: 输出路径
            replacements: 替换映射
        """
        # 需要忽略的文件和目录
        ignore_patterns = [
            ".git",
            "__pycache__",
            "*.pyc",
            ".pytest_cache",
            ".mypy_cache",
            ".ruff_cache",
            "htmlcov",
            ".coverage",
            "coverage.xml",
            "dist",
            "build",
            "*.egg-info",
        ]

        # 遍历模板目录
        for item in self.template_path.rglob("*"):
            if item.is_dir():
                continue

            # 检查是否应该忽略
            if any(pattern in str(item) for pattern in ignore_patterns):
                continue

            # 计算相对路径
            rel_path = item.relative_to(self.template_path)
            output_file = output_path / rel_path

            # 创建目录
            output_file.parent.mkdir(parents=True, exist_ok=True)

            # 处理文件
            # 处理 .template 文件（使用 Jinja2 渲染）
            if item.suffix == ".template" or item.name.endswith(".template"):
                self._process_template_file(item, output_file, replacements)
            elif item.suffix in [".md", ".txt", ".toml", ".yaml", ".yml", ".json"]:
                # 文本文件，进行替换
                self._process_text_file(item, output_file, replacements)
            else:
                # 二进制文件，直接复制
                shutil.copy2(item, output_file)

    def _process_text_file(
        self, source: Path, target: Path, replacements: Dict[str, str]
    ) -> None:
        """
        处理文本文件，进行替换

        Args:
            source: 源文件路径
            target: 目标文件路径
            replacements: 替换映射
        """
        try:
            # 读取源文件
            content = source.read_text(encoding="utf-8")

            # 执行替换
            for old, new in replacements.items():
                content = content.replace(old, new)

            # 写入目标文件
            target.write_text(content, encoding="utf-8")
        except Exception as e:
            # 如果处理失败，直接复制
            print(f"警告: 处理文件 {source} 时出错: {e}，将直接复制")
            shutil.copy2(source, target)
    
    def _process_template_file(
        self, source: Path, target: Path, replacements: Dict[str, str]
    ) -> None:
        """
        处理模板文件（.template），使用 Jinja2 渲染
        
        Args:
            source: 源文件路径
            target: 目标文件路径（移除 .template 后缀）
            replacements: 替换映射
        """
        try:
            # 移除 .template 后缀作为目标文件名
            if target.suffix == ".template" or target.name.endswith(".template"):
                # 移除 .template 后缀
                target = target.with_suffix("")
                if target.name.endswith(".template"):
                    target = target.parent / target.name.replace(".template", "")
            
            # 获取模板相对路径
            template_name = source.relative_to(self.template_path).as_posix()
            
            # 使用 Jinja2 渲染模板
            template = self.env.get_template(template_name)
            
            # 准备模板变量（使用 replacements，已经包含了所有需要的变量）
            template_vars = replacements.copy()
            
            # 渲染模板
            content = template.render(**template_vars)
            
            # 写入目标文件
            target.write_text(content, encoding="utf-8")
        except Exception as e:
            # 如果模板渲染失败，尝试作为普通文本文件处理
            print(f"警告: 模板渲染失败 {source}, 使用普通文本处理: {e}")
            # 移除 .template 后缀后处理
            if target.suffix == ".template" or target.name.endswith(".template"):
                target = target.with_suffix("")
            self._process_text_file(source, target, replacements)

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

        # 读取模板（如果存在）
        if idea_file.exists():
            content = idea_file.read_text(encoding="utf-8")
        else:
            # 使用基本模板
            content = """# Project Idea & Kickoff Guide

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

**Last Updated**: {date}
**Status**: 🟡 Planning
"""

        # 替换占位符
        from datetime import datetime

        content = content.format(
            project_idea=project_idea,
            date=datetime.now().strftime("%Y-%m-%d"),
        )

        idea_file.write_text(content, encoding="utf-8")

