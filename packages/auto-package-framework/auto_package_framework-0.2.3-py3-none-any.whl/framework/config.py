"""配置管理模块"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
import yaml
from dotenv import load_dotenv

# 尝试导入 ConfigManager 以支持从用户配置目录加载
try:
    from .config_manager import ConfigManager
    _config_manager_available = True
except ImportError:
    _config_manager_available = False


class Config:
    """框架配置管理类"""

    def __init__(self, config_path: Optional[str] = None):
        """
        初始化配置

        Args:
            config_path: 配置文件路径，如果为None则使用默认路径
        """
        # 加载环境变量
        load_dotenv()
        
        # 如果可用，从用户配置目录加载配置
        if _config_manager_available:
            try:
                config_manager = ConfigManager()
                user_env_file = config_manager.get_config_dir() / ".env"
                if user_env_file.exists():
                    load_dotenv(user_env_file)
            except Exception:
                pass  # 忽略错误，继续使用默认配置

        # 默认配置路径
        if config_path is None:
            config_path = Path(__file__).parent.parent.parent / "config.yaml"

        self.config_path = Path(config_path)
        self.config: Dict[str, Any] = {}

        if self.config_path.exists():
            with open(self.config_path, "r", encoding="utf-8") as f:
                self.config = yaml.safe_load(f) or {}

    def get(self, key: str, default: Any = None) -> Any:
        """
        获取配置值，支持点号分隔的嵌套键

        Args:
            key: 配置键，支持 "github.token" 这样的嵌套格式
            default: 默认值

        Returns:
            配置值，如果不存在则返回默认值
        """
        keys = key.split(".")
        value = self.config

        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
                if value is None:
                    return self._get_from_env(key, default)
            else:
                return self._get_from_env(key, default)

        if value is None:
            return self._get_from_env(key, default)

        return value

    def _get_from_env(self, key: str, default: Any) -> Any:
        """
        从环境变量获取配置值

        Args:
            key: 配置键
            default: 默认值

        Returns:
            环境变量值或默认值
        """
        # 将键转换为环境变量格式
        env_key = key.upper().replace(".", "_")
        return os.getenv(env_key, default)

    @property
    def github_token(self) -> Optional[str]:
        """获取GitHub Token"""
        return self.get("github.token") or os.getenv("GITHUB_TOKEN")

    @property
    def github_username(self) -> Optional[str]:
        """获取GitHub用户名"""
        return self.get("github.username") or os.getenv("GITHUB_USERNAME")

    @property
    def pypi_username(self) -> Optional[str]:
        """获取PyPI用户名"""
        return self.get("pypi.username") or os.getenv("PYPI_USERNAME")

    @property
    def pypi_password(self) -> Optional[str]:
        """获取PyPI密码"""
        return self.get("pypi.password") or os.getenv("PYPI_PASSWORD")

    @property
    def pypi_token(self) -> Optional[str]:
        """获取PyPI API Token"""
        return self.get("pypi.token") or os.getenv("PYPI_TOKEN")

    @property
    def ai_provider(self) -> str:
        """获取AI提供商"""
        return self.get("ai.provider", "openai")

    @property
    def ai_api_key(self) -> Optional[str]:
        """获取AI API密钥"""
        provider = self.ai_provider
        if provider == "openai":
            return self.get("ai.api_key") or os.getenv("OPENAI_API_KEY")
        elif provider == "anthropic":
            return self.get("ai.api_key") or os.getenv("ANTHROPIC_API_KEY")
        return None

    @property
    def ai_model(self) -> str:
        """获取AI模型名称"""
        provider = self.ai_provider
        if provider == "openai":
            return self.get("ai.model", "gpt-4")
        elif provider == "anthropic":
            return self.get("ai.model", "claude-3-opus-20240229")
        return self.get("ai.model", "gpt-4")

    @property
    def code_generation_mode(self) -> str:
        """获取代码生成模式"""
        return self.get("code_generation.mode", "auto")
    
    @property
    def code_generation_config(self) -> Dict[str, Any]:
        """获取代码生成配置"""
        return {
            "mode": self.code_generation_mode,
            "api": {
                "provider": self.ai_provider,
                "api_key": self.ai_api_key,
                "model": self.ai_model,
            },
            "cursor": {
                "enabled": self.get("code_generation.cursor.enabled", True),
                "auto_processed": self.get("code_generation.cursor.auto_processed", True),
                "dialogue_file": self.get("code_generation.cursor.dialogue_file", ".cursor_dialogue.md"),
                "timeout": self.get("code_generation.cursor.timeout", 300),
            },
        }
    
    @property
    def template_path(self) -> Path:
        """获取模板路径"""
        # 首先检查配置文件中指定的路径（允许用户自定义模板）
        template_str = self.get("template_path")
        if template_str:
            custom_path = Path(template_str).resolve()
            if custom_path.exists():
                return custom_path
        
        # 使用内置模板（包内模板）
        # 获取framework包的安装路径
        try:
            import importlib.util
            spec = importlib.util.find_spec("framework")
            if spec and spec.origin:
                # 从包的__file__获取路径
                framework_path = Path(spec.origin).parent
            else:
                # 回退到当前文件路径
                framework_path = Path(__file__).parent
        except Exception:
            # 如果导入失败，使用当前文件路径
            framework_path = Path(__file__).parent
        
        builtin_template = framework_path / "templates"
        if builtin_template.exists():
            return builtin_template.resolve()
        
        # 回退到相对路径（向后兼容，用于开发环境）
        fallback_path = Path(__file__).parent.parent.parent.parent / "PROJECT_TEMPLATE"
        if fallback_path.exists():
            return fallback_path.resolve()
        
        raise ValueError(
            f"找不到模板目录。请确保：\n"
            f"1. 模板已内置到包中（位于 {builtin_template}）\n"
            f"2. 或在配置文件中指定 template_path\n"
            f"3. 或在项目根目录存在 PROJECT_TEMPLATE 目录（开发环境）\n"
            f"   模板仓库: https://github.com/flashpoint493/python-package-template"
        )

