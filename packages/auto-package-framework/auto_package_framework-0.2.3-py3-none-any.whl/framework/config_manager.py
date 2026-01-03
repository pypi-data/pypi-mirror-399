"""配置管理模块 - 用于保存和管理用户配置"""

import os
import json
from pathlib import Path
from typing import Optional, Dict, Any
from dotenv import load_dotenv


class ConfigManager:
    """配置管理器 - 管理用户配置的持久化存储"""
    
    def __init__(self, config_dir: Optional[Path] = None):
        """
        初始化配置管理器
        
        Args:
            config_dir: 配置目录路径，默认为用户主目录下的 .auto_package_framework
        """
        if config_dir is None:
            # 使用用户主目录下的配置目录
            home = Path.home()
            self.config_dir = home / ".auto_package_framework"
        else:
            self.config_dir = Path(config_dir)
        
        # 确保配置目录存在
        self.config_dir.mkdir(parents=True, exist_ok=True)
        
        # 配置文件路径
        self.config_file = self.config_dir / "config.json"
        self.env_file = self.config_dir / ".env"
        
        # 加载现有配置
        self._load_config()
    
    def _load_config(self) -> None:
        """加载配置文件"""
        self.config: Dict[str, Any] = {}
        
        # 加载 JSON 配置
        if self.config_file.exists():
            try:
                with open(self.config_file, "r", encoding="utf-8") as f:
                    self.config = json.load(f)
            except Exception:
                self.config = {}
        
        # 加载 .env 文件
        if self.env_file.exists():
            load_dotenv(self.env_file)
    
    def _save_config(self) -> None:
        """保存配置到文件"""
        try:
            with open(self.config_file, "w", encoding="utf-8") as f:
                json.dump(self.config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise ValueError(f"保存配置失败: {e}")
    
    def set_api_key(
        self,
        provider: str,
        api_key: str,
        model: Optional[str] = None,
    ) -> None:
        """
        设置API密钥
        
        Args:
            provider: AI提供商 ("openai" 或 "anthropic")
            api_key: API密钥
            model: 模型名称（可选）
        """
        provider = provider.lower()
        if provider not in ["openai", "anthropic"]:
            raise ValueError(f"不支持的AI提供商: {provider}")
        
        # 保存到配置
        if "ai" not in self.config:
            self.config["ai"] = {}
        
        self.config["ai"]["provider"] = provider
        self.config["ai"]["api_key"] = api_key
        if model:
            self.config["ai"]["model"] = model
        
        # 保存到 .env 文件
        env_key = "OPENAI_API_KEY" if provider == "openai" else "ANTHROPIC_API_KEY"
        self._update_env_file(env_key, api_key)
        
        # 保存配置
        self._save_config()
    
    def set_github_token(self, token: str, username: Optional[str] = None) -> None:
        """
        设置GitHub Token
        
        Args:
            token: GitHub Token
            username: GitHub用户名（可选）
        """
        if "github" not in self.config:
            self.config["github"] = {}
        
        self.config["github"]["token"] = token
        if username:
            self.config["github"]["username"] = username
        
        self._update_env_file("GITHUB_TOKEN", token)
        if username:
            self._update_env_file("GITHUB_USERNAME", username)
        
        self._save_config()
    
    def set_pypi_token(self, token: str, username: Optional[str] = None) -> None:
        """
        设置PyPI Token
        
        Args:
            token: PyPI Token
            username: PyPI用户名（可选）
        """
        if "pypi" not in self.config:
            self.config["pypi"] = {}
        
        self.config["pypi"]["token"] = token
        if username:
            self.config["pypi"]["username"] = username
        
        self._update_env_file("PYPI_TOKEN", token)
        if username:
            self._update_env_file("PYPI_USERNAME", username)
        
        self._save_config()
    
    def _update_env_file(self, key: str, value: str) -> None:
        """更新 .env 文件"""
        env_lines = []
        
        # 读取现有内容
        if self.env_file.exists():
            with open(self.env_file, "r", encoding="utf-8") as f:
                env_lines = f.readlines()
        
        # 更新或添加键值对
        updated = False
        for i, line in enumerate(env_lines):
            if line.strip().startswith(f"{key}="):
                env_lines[i] = f"{key}={value}\n"
                updated = True
                break
        
        if not updated:
            env_lines.append(f"{key}={value}\n")
        
        # 写入文件
        with open(self.env_file, "w", encoding="utf-8") as f:
            f.writelines(env_lines)
    
    def get_api_key(self, provider: Optional[str] = None) -> Optional[str]:
        """
        获取API密钥
        
        Args:
            provider: AI提供商，如果为None则返回当前配置的provider的key
        
        Returns:
            API密钥，如果不存在返回None
        """
        if provider:
            provider = provider.lower()
            env_key = "OPENAI_API_KEY" if provider == "openai" else "ANTHROPIC_API_KEY"
            return os.getenv(env_key) or self.config.get("ai", {}).get("api_key")
        
        # 返回当前配置的provider的key
        current_provider = self.config.get("ai", {}).get("provider", "openai")
        env_key = "OPENAI_API_KEY" if current_provider == "openai" else "ANTHROPIC_API_KEY"
        return os.getenv(env_key) or self.config.get("ai", {}).get("api_key")
    
    def get_config(self) -> Dict[str, Any]:
        """获取完整配置"""
        return self.config.copy()
    
    def clear_config(self) -> None:
        """清除所有配置"""
        self.config = {}
        if self.config_file.exists():
            self.config_file.unlink()
        if self.env_file.exists():
            self.env_file.unlink()
    
    def get_config_dir(self) -> Path:
        """获取配置目录路径"""
        return self.config_dir

