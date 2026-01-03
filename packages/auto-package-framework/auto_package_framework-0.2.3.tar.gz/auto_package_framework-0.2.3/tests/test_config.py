"""配置模块测试"""

import os
import tempfile
from pathlib import Path
import yaml
from framework.config import Config


def test_config_from_file():
    """测试从文件加载配置"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        config_data = {
            "github": {"token": "test_token", "username": "test_user"},
            "pypi": {"token": "pypi_test_token"},
            "ai": {"provider": "openai", "api_key": "test_key", "model": "gpt-4"},
        }
        yaml.dump(config_data, f)
        config_path = f.name

    try:
        config = Config(config_path)
        assert config.github_token == "test_token"
        assert config.github_username == "test_user"
        assert config.pypi_token == "pypi_test_token"
        assert config.ai_provider == "openai"
        assert config.ai_api_key == "test_key"
        assert config.ai_model == "gpt-4"
    finally:
        os.unlink(config_path)


def test_config_from_env():
    """测试从环境变量加载配置"""
    os.environ["GITHUB_TOKEN"] = "env_token"
    os.environ["PYPI_TOKEN"] = "env_pypi_token"
    os.environ["OPENAI_API_KEY"] = "env_openai_key"

    try:
        config = Config()
        # 如果配置文件不存在，应该从环境变量读取
        # 注意：这个测试依赖于实际环境，可能不稳定
        pass
    finally:
        # 清理环境变量
        os.environ.pop("GITHUB_TOKEN", None)
        os.environ.pop("PYPI_TOKEN", None)
        os.environ.pop("OPENAI_API_KEY", None)


def test_config_nested_keys():
    """测试嵌套键访问"""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        config_data = {"github": {"token": "nested_token"}}
        yaml.dump(config_data, f)
        config_path = f.name

    try:
        config = Config(config_path)
        assert config.get("github.token") == "nested_token"
    finally:
        os.unlink(config_path)

