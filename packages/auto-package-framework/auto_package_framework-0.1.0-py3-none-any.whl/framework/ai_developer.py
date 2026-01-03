"""AI代码生成器模块"""

from pathlib import Path
from typing import Optional, Dict, Any
import openai
from anthropic import Anthropic


class AIDeveloper:
    """AI代码生成器"""

    def __init__(
        self,
        provider: str = "openai",
        api_key: Optional[str] = None,
        model: Optional[str] = None,
    ):
        """
        初始化AI开发者

        Args:
            provider: AI提供商 ("openai" 或 "anthropic")
            api_key: API密钥
            model: 模型名称
        """
        self.provider = provider.lower()

        if self.provider == "openai":
            if not api_key:
                raise ValueError("OpenAI需要api_key")
            openai.api_key = api_key
            self.client = openai.OpenAI(api_key=api_key)
            self.model = model or "gpt-4"
        elif self.provider == "anthropic":
            if not api_key:
                raise ValueError("Anthropic需要api_key")
            self.client = Anthropic(api_key=api_key)
            self.model = model or "claude-3-opus-20240229"
        else:
            raise ValueError(f"不支持的AI提供商: {provider}")

    def generate_code(
        self,
        project_idea: str,
        project_structure: Dict[str, Any],
        existing_files: Optional[Dict[str, str]] = None,
    ) -> Dict[str, str]:
        """
        根据项目想法生成代码

        Args:
            project_idea: 项目想法描述
            project_structure: 项目结构信息
            existing_files: 现有文件内容（用于上下文）

        Returns:
            生成的代码文件字典 {文件路径: 代码内容}
        """
        # 构建提示词
        prompt = self._build_prompt(project_idea, project_structure, existing_files)

        # 调用AI生成代码
        if self.provider == "openai":
            response = self._generate_with_openai(prompt)
        else:
            response = self._generate_with_anthropic(prompt)

        # 解析响应，提取代码文件
        return self._parse_code_response(response)

    def _build_prompt(
        self,
        project_idea: str,
        project_structure: Dict[str, Any],
        existing_files: Optional[Dict[str, str]],
    ) -> str:
        """
        构建AI提示词

        Args:
            project_idea: 项目想法
            project_structure: 项目结构
            existing_files: 现有文件

        Returns:
            完整的提示词
        """
        prompt = f"""你是一个专业的Python开发助手。请根据以下项目想法生成完整的Python包代码。

## 项目想法
{project_idea}

## 项目结构
项目名称: {project_structure.get('name', 'unknown')}
包名: {project_structure.get('package_name', 'unknown')}
Python版本: {project_structure.get('python_version', '3.8+')}

## 要求
1. 遵循PEP 8代码规范
2. 所有公共函数必须有类型注解和文档字符串
3. 代码注释使用中文
4. 代码使用英文
5. 包含基本的单元测试
6. 确保代码可以通过ruff和mypy检查

## 需要生成的文件
1. src/{project_structure.get('package_name', 'package')}/__init__.py - 包初始化文件
2. src/{project_structure.get('package_name', 'package')}/main.py - 主要功能模块
3. tests/test_main.py - 基本测试文件

请生成完整的、可运行的代码。对于每个文件，使用以下格式：
```python:文件路径
代码内容
```

如果项目需要多个模块，请生成相应的文件。
"""

        if existing_files:
            prompt += "\n## 现有文件（供参考）\n"
            for file_path, content in existing_files.items():
                prompt += f"\n### {file_path}\n```\n{content[:500]}...\n```\n"

        return prompt

    def _generate_with_openai(self, prompt: str) -> str:
        """使用OpenAI生成代码"""
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "你是一个专业的Python开发助手，擅长生成高质量、符合规范的Python代码。",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0.7,
            max_tokens=4000,
        )
        return response.choices[0].message.content

    def _generate_with_anthropic(self, prompt: str) -> str:
        """使用Anthropic生成代码"""
        response = self.client.messages.create(
            model=self.model,
            max_tokens=4000,
            messages=[
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
        )
        return response.content[0].text

    def _parse_code_response(self, response: str) -> Dict[str, str]:
        """
        解析AI响应，提取代码文件

        Args:
            response: AI响应文本

        Returns:
            代码文件字典
        """
        files = {}
        current_file = None
        current_code = []
        in_code_block = False

        lines = response.split("\n")
        for line in lines:
            # 检测代码块开始
            if line.strip().startswith("```python:"):
                # 提取文件路径
                file_path = line.strip().replace("```python:", "").strip()
                current_file = file_path
                current_code = []
                in_code_block = True
            elif line.strip().startswith("```"):
                # 代码块结束
                if current_file and current_code:
                    files[current_file] = "\n".join(current_code)
                current_file = None
                current_code = []
                in_code_block = False
            elif in_code_block and current_file:
                # 在代码块中，收集代码
                current_code.append(line)

        # 处理最后一个代码块
        if current_file and current_code:
            files[current_file] = "\n".join(current_code)

        return files

    def generate_readme(self, project_name: str, project_idea: str) -> str:
        """
        生成README.md内容

        Args:
            project_name: 项目名称
            project_idea: 项目想法

        Returns:
            README内容
        """
        prompt = f"""请为以下Python项目生成一个专业的README.md文件。

项目名称: {project_name}
项目描述: {project_idea}

要求:
1. 包含项目简介
2. 功能特性列表
3. 安装说明
4. 快速开始示例
5. 使用Markdown格式
6. 内容使用中文

请直接输出README.md的内容，不要包含代码块标记。
"""

        if self.provider == "openai":
            response = self._generate_with_openai(prompt)
        else:
            response = self._generate_with_anthropic(prompt)

        return response.strip()

