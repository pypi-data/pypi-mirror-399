"""代码生成器抽象接口和实现"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional, Dict, Any
import sys
import os


class CodeGenerator(ABC):
    """代码生成器抽象接口"""
    
    @abstractmethod
    def generate_code(
        self,
        project_idea: str,
        project_structure: Dict[str, Any],
        existing_files: Optional[Dict[str, str]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, str]:
        """
        生成代码文件
        
        Args:
            project_idea: 项目想法描述
            project_structure: 项目结构信息
            existing_files: 现有文件内容（用于上下文）
            context: 额外上下文信息
            
        Returns:
            生成的代码文件字典 {文件路径: 代码内容}
        """
        pass
    
    @abstractmethod
    def can_generate(self) -> bool:
        """
        检查是否可以生成代码
        
        Returns:
            如果可以生成返回 True，否则返回 False
        """
        pass
    
    @abstractmethod
    def get_status(self) -> str:
        """
        获取生成器状态
        
        Returns:
            状态描述字符串
        """
        pass
    
    def validate_result(
        self,
        generated_files: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        验证生成的结果
        
        Args:
            generated_files: 生成的代码文件字典
            
        Returns:
            验证结果字典，包含 errors 和 warnings
        """
        errors = []
        warnings = []
        
        # 基本验证
        if not generated_files:
            warnings.append("未生成任何文件")
        
        for file_path, content in generated_files.items():
            if not content.strip():
                warnings.append(f"文件 {file_path} 为空")
        
        return {
            "errors": errors,
            "warnings": warnings,
            "valid": len(errors) == 0,
        }


class CodeGeneratorFactory:
    """代码生成器工厂"""
    
    @staticmethod
    def create(
        mode: str = "auto",
        config: Optional[Dict[str, Any]] = None,
        project_path: Optional[Path] = None,
    ) -> Optional[CodeGenerator]:
        """
        创建代码生成器
        
        Args:
            mode: 生成模式 ("api", "cursor", "agent", "auto")
            config: 配置字典
            project_path: 项目路径（Cursor 模式需要）
            
        Returns:
            代码生成器实例，如果无法创建返回 None
        """
        config = config or {}
        
        if mode == "auto":
            # 自动选择可用的生成器
            # 优先级: Cursor > API > Agent
            if project_path:
                cursor_gen = CursorCodeGenerator(project_path)
                if cursor_gen.can_generate():
                    return cursor_gen
            
            api_gen = APICodeGenerator.from_config(config)
            if api_gen and api_gen.can_generate():
                return api_gen
            
            return None
        
        elif mode == "api":
            return APICodeGenerator.from_config(config)
        
        elif mode == "cursor":
            if not project_path:
                raise ValueError("Cursor 模式需要 project_path")
            return CursorCodeGenerator(project_path)
        
        elif mode == "agent":
            # 未来实现
            raise NotImplementedError("Agent 模式尚未实现")
        
        else:
            raise ValueError(f"不支持的生成模式: {mode}")


# 导入 AIDeveloper 用于 API 代码生成
from .ai_developer import AIDeveloper


class APICodeGenerator(CodeGenerator):
    """API 代码生成器（使用 AIDeveloper）"""
    
    def __init__(self, ai_developer: AIDeveloper):
        """
        初始化 API 代码生成器
        
        Args:
            ai_developer: AIDeveloper 实例
        """
        self.ai_developer = ai_developer
    
    @classmethod
    def from_config(cls, config: Dict[str, Any]) -> Optional["APICodeGenerator"]:
        """
        从配置创建实例
        
        Args:
            config: 配置字典，包含 api 配置
            
        Returns:
            APICodeGenerator 实例，如果配置不完整返回 None
        """
        api_config = config.get("api", {})
        provider = api_config.get("provider", "openai")
        api_key = api_config.get("api_key")
        model = api_config.get("model")
        
        if not api_key:
            return None
        
        try:
            ai_developer = AIDeveloper(
                provider=provider,
                api_key=api_key,
                model=model,
            )
            return cls(ai_developer)
        except Exception:
            return None
    
    def generate_code(
        self,
        project_idea: str,
        project_structure: Dict[str, Any],
        existing_files: Optional[Dict[str, str]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, str]:
        """生成代码"""
        return self.ai_developer.generate_code(
            project_idea=project_idea,
            project_structure=project_structure,
            existing_files=existing_files,
        )
    
    def can_generate(self) -> bool:
        """检查是否可以生成"""
        return self.ai_developer is not None
    
    def get_status(self) -> str:
        """获取状态"""
        if self.ai_developer:
            return f"就绪 (Provider: {self.ai_developer.provider}, Model: {self.ai_developer.model})"
        return "未就绪"


class CursorCodeGenerator(CodeGenerator):
    """Cursor IDE 代码生成器"""
    
    def __init__(self, project_path: Path):
        """
        初始化 Cursor 代码生成器
        
        Args:
            project_path: 项目路径
        """
        self.project_path = Path(project_path)
        self.dialogue_file = self.project_path / ".cursor_dialogue.md"
    
    def generate_code(
        self,
        project_idea: str,
        project_structure: Dict[str, Any],
        existing_files: Optional[Dict[str, str]] = None,
        context: Optional[Dict[str, Any]] = None,
    ) -> Dict[str, str]:
        """
        通过 Cursor IDE 生成代码
        
        实现方式：
        1. 创建对话提示文件
        2. 等待用户在 Cursor 中完成
        3. 收集生成的文件
        """
        # 1. 创建对话提示文件
        prompt = self._build_dialogue_prompt(
            project_idea, project_structure, existing_files
        )
        self.dialogue_file.write_text(prompt, encoding="utf-8")
        
        # 2. 提示用户
        print("\n" + "="*60)
        print("📝 Cursor 代码生成模式")
        print("="*60)
        print(f"已创建对话文件: {self.dialogue_file}")
        print("\n请在 Cursor IDE 中：")
        print("1. 打开此文件")
        print("2. 使用 Cursor 的对话功能或 auto processed 模式")
        print("3. 让 AI 根据提示生成代码")
        print("4. 完成后，框架会自动收集生成的文件")
        print("\n等待中...（可以按 Ctrl+C 取消）")
        print("="*60 + "\n")
        
        # 3. 等待用户完成（这里可以添加文件监控）
        input("按 Enter 键继续（当代码生成完成后）...")
        
        # 4. 收集生成的文件
        return self._collect_generated_files(project_structure)
    
    def _build_dialogue_prompt(
        self,
        project_idea: str,
        project_structure: Dict[str, Any],
        existing_files: Optional[Dict[str, str]] = None,
    ) -> str:
        """构建对话提示"""
        package_name = project_structure.get("package_name", "package")
        project_name = project_structure.get("name", "Project")
        
        # 尝试读取 llms.txt 作为参考格式
        llms_reference = self._load_llms_reference()
        
        prompt = f"""# Cursor Auto Processed Mode - 代码生成请求

## 项目想法
{project_idea}

## 项目结构
- 项目名称: {project_structure.get('name', 'unknown')}
- 包名: {package_name}
- Python版本: {project_structure.get('python_version', '3.8+')}

## 需要生成的文件

请生成以下文件：

1. **src/{package_name}/__init__.py**
   - 包初始化文件
   - 导出主要功能

2. **src/{package_name}/main.py**
   - 主要功能模块
   - 实现核心业务逻辑

3. **tests/test_main.py**
   - 基本测试文件
   - 包含单元测试

## 代码要求

1. **代码规范**
   - 遵循 PEP 8
   - 使用类型注解
   - 所有公共函数必须有文档字符串

2. **代码风格**
   - 代码使用英文
   - 注释使用中文
   - 函数和类名使用英文

3. **质量要求**
   - 确保代码可以通过 ruff 检查
   - 确保代码可以通过 mypy 类型检查
   - 包含基本的错误处理

4. **测试要求**
   - 包含基本的单元测试
   - 测试覆盖率至少 50%

## 现有文件参考

"""
        if existing_files:
            for file_path, content in existing_files.items():
                prompt += f"\n### {file_path}\n```\n{content[:500]}...\n```\n"
        else:
            prompt += "\n无现有文件。\n"
        
        prompt += """
## 执行方式

请使用 Cursor 的以下功能之一：
1. **对话模式**: 在 Cursor 中打开对话，粘贴此内容
2. **Auto Processed 模式**: 使用 Cursor 的自动处理功能
3. **Composer 模式**: 使用 Cursor Composer 批量生成

生成完成后，请确保所有文件都已创建并符合要求。
"""
        
        return prompt
    
    def _collect_generated_files(
        self,
        project_structure: Dict[str, Any]
    ) -> Dict[str, str]:
        """收集生成的文件"""
        package_name = project_structure.get("package_name", "package")
        files = {}
        
        # 预期的文件路径
        expected_files = [
            f"src/{package_name}/__init__.py",
            f"src/{package_name}/main.py",
            "tests/test_main.py",
        ]
        
        for file_path in expected_files:
            full_path = self.project_path / file_path
            if full_path.exists():
                files[file_path] = full_path.read_text(encoding="utf-8")
        
        return files
    
    def can_generate(self) -> bool:
        """检查是否可以生成（检查 Cursor 环境）"""
        # 检查项目路径是否存在
        if not self.project_path.exists():
            return False
        
        # 可以添加更多检查，比如检测 Cursor IDE 是否运行
        # 目前简单返回 True
        return True
    
    def get_status(self) -> str:
        """获取状态"""
        if self.project_path.exists():
            return f"就绪 (项目路径: {self.project_path})"
        return "未就绪 (项目路径不存在)"


# 未来实现
class AgentCodeGenerator(CodeGenerator):
    """Agent 代码生成器（未来实现）"""
    
    def generate_code(self, *args, **kwargs) -> Dict[str, str]:
        raise NotImplementedError("Agent 模式尚未实现")
    
    def can_generate(self) -> bool:
        return False
    
    def get_status(self) -> str:
        return "未实现（计划在 v1.0.0 中实现）"

