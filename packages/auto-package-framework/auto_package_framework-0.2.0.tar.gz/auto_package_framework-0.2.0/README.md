# Auto Package Framework

<p align="center">
  <a href="https://pypi.org/project/auto-package-framework/"><img src="https://img.shields.io/pypi/v/auto-package-framework.svg" alt="PyPI Version"></a>
  <a href="https://pypi.org/project/auto-package-framework/"><img src="https://img.shields.io/pypi/pyversions/auto-package-framework.svg" alt="Python Versions"></a>
  <a href="https://pepy.tech/project/auto-package-framework"><img src="https://static.pepy.tech/badge/auto-package-framework" alt="Downloads"></a>
  <a href="https://codecov.io/gh/flashpoint493/auto-package-framework"><img src="https://codecov.io/gh/flashpoint493/auto-package-framework/branch/main/graph/badge.svg" alt="Codecov"></a>
  <a href="https://github.com/flashpoint493/auto-package-framework/actions/workflows/ci.yml"><img src="https://github.com/flashpoint493/auto-package-framework/actions/workflows/ci.yml/badge.svg" alt="CI"></a>
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
</p>

<p align="center">
  <a href="https://www.python.org/"><img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python"></a>
  <a href="https://github.com/flashpoint493/auto-package-framework"><img src="https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey.svg" alt="Platform"></a>
  <a href="https://github.com/flashpoint493/auto-package-framework/actions/workflows/release.yml"><img src="https://github.com/flashpoint493/auto-package-framework/actions/workflows/release.yml/badge.svg?branch=main" alt="Release"></a>
  <a href="https://github.com/flashpoint493/auto-package-framework/releases"><img src="https://img.shields.io/github/v/release/flashpoint493/auto-package-framework?display_name=tag" alt="Latest Release"></a>
  <a href="https://pre-commit.com/"><img src="https://img.shields.io/badge/pre--commit-enabled-brightgreen.svg" alt="pre-commit"></a>
</p>

<p align="center">
  <a href="https://github.com/flashpoint493/auto-package-framework/stargazers"><img src="https://img.shields.io/github/stars/flashpoint493/auto-package-framework?style=social" alt="GitHub Stars"></a>
  <a href="https://github.com/flashpoint493/auto-package-framework/releases"><img src="https://img.shields.io/github/downloads/flashpoint493/auto-package-framework/total" alt="GitHub Downloads"></a>
  <a href="https://github.com/flashpoint493/auto-package-framework/commits/main"><img src="https://img.shields.io/github/last-commit/flashpoint493/auto-package-framework" alt="Last Commit"></a>
  <a href="https://github.com/flashpoint493/auto-package-framework/graphs/commit-activity"><img src="https://img.shields.io/github/commit-activity/m/flashpoint493/auto-package-framework" alt="Commit Activity"></a>
</p>

<p align="center">
  <a href="https://github.com/flashpoint493/auto-package-framework/issues"><img src="https://img.shields.io/github/issues/flashpoint493/auto-package-framework" alt="Open Issues"></a>
  <a href="https://github.com/flashpoint493/auto-package-framework/pulls"><img src="https://img.shields.io/github/issues-pr/flashpoint493/auto-package-framework" alt="Open PRs"></a>
  <a href="https://github.com/flashpoint493/auto-package-framework/graphs/contributors"><img src="https://img.shields.io/github/contributors/flashpoint493/auto-package-framework" alt="Contributors"></a>
  <a href="https://conventionalcommits.org"><img src="https://img.shields.io/badge/Conventional%20Commits-1.0.0-yellow.svg" alt="Conventional Commits"></a>
</p>

<p align="center">
  <a href="https://github.com/googleapis/release-please"><img src="https://img.shields.io/badge/release--please-enabled-blue" alt="release-please"></a>
  <a href="./.github/dependabot.yml"><img src="https://img.shields.io/badge/dependabot-enabled-025E8C?logo=dependabot" alt="Dependabot"></a>
  <a href="https://docs.astral.sh/ruff/"><img src="https://img.shields.io/badge/code%20style-ruff-000000.svg" alt="Code Style: ruff"></a>
  <a href="http://mypy-lang.org/"><img src="https://img.shields.io/badge/type%20checked-mypy-2A6DB0.svg" alt="Type Checked: mypy"></a>
</p>

<p align="center">
  <a href="./CODE_OF_CONDUCT.md">Code of Conduct</a> •
  <a href="./SECURITY.md">Security Policy</a> •
  <a href="https://github.com/flashpoint493/auto-package-framework/issues">Issue Tracker</a>
</p>

---

**AI驱动的自动化Python包创建、开发和发布框架**

> ⚠️ **Development Status**: This project is under active development. APIs may change before v1.0.0 release.

## Quick Try

Try Auto Package Framework instantly without installation using `uvx`:

```bash
uvx auto-package-framework --help
```

## Overview

Auto Package Framework 是一个自动化框架，能够帮助你从想法到发布，全自动创建Python包。只需提供一个项目想法，框架就能自动生成项目结构、编写代码、创建GitHub仓库并发布到PyPI。

### Key Features

- **自动化项目生成**: 基于内置模板自动创建完整的Python包项目结构
- **内置专业模板**: 包含完整的项目模板（CI/CD、文档、代码规范等），开箱即用
- **AI代码生成**: 使用AI根据项目想法自动生成高质量代码
- **GitHub集成**: 自动创建仓库、推送代码、设置CI/CD
- **PyPI发布**: 自动构建和发布包到PyPI
- **命令行工具**: 提供便捷的CLI接口

## Architecture

```
用户输入想法
    ↓
1. 解析项目需求 (PROJECT_IDEA.md格式)
    ↓
2. 从模板生成项目结构
    ↓
3. AI生成初始代码
    ↓
4. 运行测试和代码检查
    ↓
5. 创建GitHub仓库并推送代码
    ↓
6. 设置CI/CD工作流
    ↓
7. 构建包
    ↓
8. 发布到PyPI
    ↓
9. 创建GitHub Release
```

### Technical Framework

- **Core Stack**: Python 3.8+, PyGithub, GitPython, OpenAI/Anthropic
- **Key Libraries**: PyYAML, Jinja2, Click, Twine, Build
- **Build System**: setuptools with pyproject.toml
- **Testing**: pytest with coverage

### Technical Details

- **API Design**: 模块化设计，支持灵活配置
- **Performance**: 快速生成项目，AI代码生成异步处理
- **Security**: 支持环境变量和密钥管理，不存储敏感信息
- **Testing**: 单元测试和集成测试覆盖

## Features

### Core Features

- [OK] **项目生成器**: 从模板自动生成项目结构
- [OK] **GitHub集成**: 自动创建仓库并推送代码
- [OK] **PyPI发布**: 自动构建和发布包
- [OK] **AI代码生成**: 支持OpenAI和Anthropic
- [OK] **命令行工具**: 提供便捷的CLI接口
- [OK] **配置管理**: 支持YAML文件和环境变量

### Advanced Features

- [OK] **模板系统**: 基于Jinja2的模板渲染
- [OK] **Git操作**: 自动初始化仓库和提交
- [OK] **版本管理**: 自动更新版本号
- [OK] **错误处理**: 完善的错误处理和日志

### Integration Features

- [OK] **GitHub API**: 完整的GitHub操作支持
- [OK] **PyPI API**: 支持Token和密码认证
- [OK] **AI API**: 支持多个AI提供商

## Quick Start

### Installation

#### Basic Installation

```bash
pip install auto-package-framework
```

#### With Development Dependencies

```bash
pip install auto-package-framework[dev]
```

#### From Source

```bash
git clone https://github.com/flashpoint493/auto-package-framework.git
cd auto-package-framework
pip install -e ".[dev]"
```

### Basic Usage

**Simple Example (Python):**

```python
from framework.core import AutoPackageFramework

# 初始化框架
framework = AutoPackageFramework()

# 创建包
result = framework.create_package(
    project_name="my-awesome-package",
    project_idea="一个用于自动化任务调度的Python包",
)
```

**Command-Line Example:**

```bash
# 基本使用
auto-package \
    --project-name "my-package" \
    --idea "我的项目描述"

# 完整流程（生成+GitHub+PyPI）
auto-package \
    --project-name "my-package" \
    --idea "我的项目描述" \
    --github-repo "my-package" \
    --publish
```

### Configuration

**方式1: 环境变量（推荐）**

```bash
export GITHUB_TOKEN=ghp_xxxxx
export PYPI_TOKEN=pypi-xxxxx
export OPENAI_API_KEY=sk-xxxxx
```

**方式2: 配置文件**

创建 `config.yaml`:

```yaml
github:
  username: your_username
  token: your_github_token

pypi:
  token: pypi-xxxxx

ai:
  provider: openai
  api_key: your_api_key
  model: gpt-4

# 模板路径（可选，默认使用内置模板）
# template_path: /path/to/custom/template
```

> **注意**: 框架已内置完整的项目模板，无需额外配置。只有在需要使用自定义模板时才需要指定 `template_path`。

## Usage Patterns

Auto Package Framework 支持多种使用模式：

### Pattern 1: 仅生成项目（推荐用于测试）

Best for: **快速原型、测试框架功能**

```python
from framework.core import AutoPackageFramework

framework = AutoPackageFramework()

result = framework.create_package(
    project_name="test-package",
    project_idea="测试项目",
    # 不指定github_repo，不会创建GitHub仓库
    auto_publish=False,
)
```

### Pattern 2: 生成 + GitHub（推荐用于开源项目）

Best for: **开源项目、需要版本控制**

```python
result = framework.create_package(
    project_name="my-package",
    project_idea="我的项目描述",
    github_repo="my-package",  # 指定仓库名
    auto_publish=False,
)
```

### Pattern 3: 完整流程（推荐用于生产环境）

Best for: **生产环境、需要自动发布**

```python
result = framework.create_package(
    project_name="production-package",
    project_idea="生产环境使用的包",
    github_repo="production-package",
    auto_publish=True,  # 自动发布到PyPI
)
```

### Pattern Comparison

| Aspect | 仅生成 | 生成+GitHub | 完整流程 |
|--------|--------|-------------|----------|
| **复杂度** | ⭐ 简单 | ⭐⭐ 中等 | ⭐⭐⭐ 高级 |
| **最佳场景** | 测试 | 开源项目 | 生产环境 |
| **GitHub** | ❌ | ✅ | ✅ |
| **PyPI** | ❌ | ❌ | ✅ |
| **时间** | ~10秒 | ~20秒 | ~60秒 |

## Advanced Usage

### 自定义配置

```python
from framework.core import AutoPackageFramework

framework = AutoPackageFramework(config_path="custom_config.yaml")

result = framework.create_package(
    project_name="custom-package",
    project_idea="自定义配置的项目",
    replacements={
        "USERNAME": "my_github_username",
        "email": "my.email@example.com",
        "author": "My Name",
    },
)
```

### 批量创建

```python
projects = [
    ("package-1", "描述1"),
    ("package-2", "描述2"),
    ("package-3", "描述3"),
]

for name, idea in projects:
    framework.create_package(
        project_name=name,
        project_idea=idea,
    )
```

## Documentation

- [快速开始指南](./QUICK_START.md) - 5分钟快速上手
- [发布指南](./PUBLISH_GUIDE.md) - 详细发布说明
- [外部工具说明](./EXTERNAL_TOOLS.md) - 所需工具和API
- [最小原型测试](./MINIMAL_PROTOTYPE.md) - 测试指南
- [项目总结](./SUMMARY.md) - 项目概述

## Requirements

- Python 3.8+
- GitHub Personal Access Token (用于GitHub集成)
- PyPI API Token (用于发布)
- OpenAI或Anthropic API Key (用于AI代码生成，可选)

## Development

### Prerequisites

- Python 3.8+
- Git
- pip

### Setup Development Environment

```bash
# Clone repository
git clone https://github.com/flashpoint493/auto-package-framework.git
cd auto-package-framework

# Install dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install

# Run tests
pytest
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test suite
pytest tests/test_config.py
```

### Code Quality

```bash
# Format code
ruff format .

# Lint code
ruff check .

# Type check
mypy .
```

## Contributing

Contributions are welcome! Please read our [Contributing Guide](./CONTRIBUTING.md) first.

1. Fork the repository
2. Create your feature branch (`git checkout -b feat/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feat/amazing-feature`)
5. Open a Pull Request

## Code of Conduct

This project adheres to a [Code of Conduct](./CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## Security

Please report security issues privately. See [SECURITY.md](./SECURITY.md) for details.

**重要提示**:
- 不要将API Token提交到代码库
- 使用环境变量或密钥管理服务
- 使用最小权限的Token

## License

This project is licensed under the MIT License - see the [LICENSE](./LICENSE) file for details.

## Acknowledgments

- 基于 [PROJECT_TEMPLATE](../PROJECT_TEMPLATE) 模板
- 使用 PyGithub、GitPython 等优秀库
- 感谢 OpenAI 和 Anthropic 提供的AI服务

## Contact

- **Author**: Auto Project Team
- **GitHub**: [@flashpoint493](https://github.com/flashpoint493)
- **Issues**: [GitHub Issues](https://github.com/flashpoint493/auto-package-framework/issues)
- **PyPI**: [auto-package-framework](https://pypi.org/project/auto-package-framework/)

---

**Made with ❤️ by Auto Project Team**

