"""配置管理模块"""

import os
from pathlib import Path
from typing import Optional, Dict, Any
import yaml
from dotenv import load_dotenv


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
    def template_path(self) -> Path:
        """获取模板路径"""
        template_str = self.get("template_path", "../PROJECT_TEMPLATE")
        return Path(template_str).resolve()

