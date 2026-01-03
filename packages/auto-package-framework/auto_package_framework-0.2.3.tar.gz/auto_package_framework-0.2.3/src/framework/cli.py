"""命令行接口"""

import sys
import json
import click
from pathlib import Path
from typing import Optional

# 修复 Windows 控制台编码问题
if sys.platform == "win32":
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

from .core import AutoPackageFramework
from .config_manager import ConfigManager


@click.group()
def cli():
    """Auto Package Framework - 自动化Python包创建和发布工具"""
    pass


@cli.command()
@click.option(
    "--config",
    "-c",
    default="config.yaml",
    help="配置文件路径",
)
@click.option(
    "--project-name",
    "-n",
    required=True,
    help="项目名称",
)
@click.option(
    "--idea",
    "-i",
    required=True,
    help="项目想法描述",
)
@click.option(
    "--output",
    "-o",
    help="输出路径（默认：当前目录）",
)
@click.option(
    "--github-repo",
    "-g",
    help="GitHub仓库名称（如果为None，使用项目名）",
)
@click.option(
    "--publish",
    "-p",
    is_flag=True,
    help="自动发布到PyPI",
)
@click.option(
    "--username",
    "-u",
    help="GitHub用户名（覆盖配置）",
)
@click.option(
    "--email",
    "-e",
    help="作者邮箱（覆盖配置）",
)
def create(
    config: str,
    project_name: str,
    idea: str,
    output: Optional[str],
    github_repo: Optional[str],
    publish: bool,
    username: Optional[str],
    email: Optional[str],
):
    """创建新的Python包项目"""
    click.echo(f"🚀 开始创建项目: {project_name}")

    # 初始化框架
    framework = AutoPackageFramework(config_path=config)

    # 准备替换映射
    replacements = {}
    if username:
        replacements["USERNAME"] = username
    if email:
        replacements["email"] = email

    # 确定输出路径
    output_path = Path(output) if output else None

    # 确定GitHub仓库名
    if not github_repo:
        github_repo = project_name

    # 创建包
    result = framework.create_package(
        project_name=project_name,
        project_idea=idea,
        output_path=output_path,
        github_repo=github_repo,
        auto_publish=publish,
        replacements=replacements,
    )

    # 输出结果
    if result["success"]:
        click.echo("✅ 项目创建成功！")
        click.echo(f"📁 项目路径: {result.get('project_path', 'N/A')}")
        if "github_repo" in result:
            click.echo(f"🔗 GitHub: {result['github_repo']}")
        if result.get("pypi_published"):
            click.echo("📦 已发布到PyPI")
    else:
        click.echo("❌ 项目创建失败！")
        for error in result.get("errors", []):
            click.echo(f"  - {error}")


@cli.group()
def config():
    """配置管理命令"""
    pass


@config.command()
@click.option(
    "--provider",
    "-p",
    type=click.Choice(["openai", "anthropic"], case_sensitive=False),
    required=True,
    help="AI提供商",
)
@click.option(
    "--api-key",
    "-k",
    required=True,
    help="API密钥",
)
@click.option(
    "--model",
    "-m",
    help="模型名称（可选）",
)
def set_ai(
    provider: str,
    api_key: str,
    model: Optional[str],
):
    """配置AI API密钥"""
    config_manager = ConfigManager()
    try:
        config_manager.set_api_key(provider, api_key, model)
        click.echo(f"✅ 已配置 {provider} API密钥")
        click.echo(f"📁 配置保存在: {config_manager.get_config_dir()}")
    except Exception as e:
        click.echo(f"❌ 配置失败: {e}", err=True)


@config.command()
@click.option(
    "--token",
    "-t",
    required=True,
    help="GitHub Token",
)
@click.option(
    "--username",
    "-u",
    help="GitHub用户名（可选）",
)
def set_github(token: str, username: Optional[str]):
    """配置GitHub Token"""
    config_manager = ConfigManager()
    try:
        config_manager.set_github_token(token, username)
        click.echo("✅ 已配置GitHub Token")
        click.echo(f"📁 配置保存在: {config_manager.get_config_dir()}")
    except Exception as e:
        click.echo(f"❌ 配置失败: {e}", err=True)


@config.command()
@click.option(
    "--token",
    "-t",
    required=True,
    help="PyPI Token",
)
@click.option(
    "--username",
    "-u",
    help="PyPI用户名（可选）",
)
def set_pypi(token: str, username: Optional[str]):
    """配置PyPI Token"""
    config_manager = ConfigManager()
    try:
        config_manager.set_pypi_token(token, username)
        click.echo("✅ 已配置PyPI Token")
        click.echo(f"📁 配置保存在: {config_manager.get_config_dir()}")
    except Exception as e:
        click.echo(f"❌ 配置失败: {e}", err=True)


@config.command()
def show():
    """显示当前配置"""
    config_manager = ConfigManager()
    config_data = config_manager.get_config()
    
    if not config_data:
        click.echo("📝 当前没有保存的配置")
        click.echo("💡 使用 'auto-package config set-ai' 等命令来配置")
        return
    
    click.echo("📋 当前配置:")
    click.echo(f"📁 配置目录: {config_manager.get_config_dir()}")
    click.echo("")
    
    if "ai" in config_data:
        ai_config = config_data["ai"]
        provider = ai_config.get("provider", "unknown")
        api_key = ai_config.get("api_key", "")
        model = ai_config.get("model", "default")
        masked_key = api_key[:8] + "..." if api_key else "未设置"
        click.echo(f"🤖 AI配置:")
        click.echo(f"   提供商: {provider}")
        click.echo(f"   API密钥: {masked_key}")
        click.echo(f"   模型: {model}")
        click.echo("")
    
    if "github" in config_data:
        github_config = config_data["github"]
        token = github_config.get("token", "")
        username = github_config.get("username", "")
        masked_token = token[:8] + "..." if token else "未设置"
        click.echo(f"🐙 GitHub配置:")
        click.echo(f"   Token: {masked_token}")
        if username:
            click.echo(f"   用户名: {username}")
        click.echo("")
    
    if "pypi" in config_data:
        pypi_config = config_data["pypi"]
        token = pypi_config.get("token", "")
        username = pypi_config.get("username", "")
        masked_token = token[:8] + "..." if token else "未设置"
        click.echo(f"📦 PyPI配置:")
        click.echo(f"   Token: {masked_token}")
        if username:
            click.echo(f"   用户名: {username}")
        click.echo("")


@config.command()
@click.confirmation_option(prompt="确定要清除所有配置吗？")
def clear():
    """清除所有配置"""
    config_manager = ConfigManager()
    try:
        config_manager.clear_config()
        click.echo("✅ 已清除所有配置")
    except Exception as e:
        click.echo(f"❌ 清除失败: {e}", err=True)


@cli.command()
@click.option(
    "--format",
    "-f",
    type=click.Choice(["json", "markdown"], case_sensitive=False),
    default="json",
    help="导出格式",
)
@click.option(
    "--output",
    "-o",
    help="输出文件路径（默认：stdout）",
)
def skill(format: str, output: Optional[str]):
    """导出IDE skill信息"""
    from .skill import get_skill_interface
    
    skill_interface = get_skill_interface()
    
    if format.lower() == "json":
        content = json.dumps(skill_interface.get_skill_info(), indent=2, ensure_ascii=False)
    else:
        content = skill_interface.get_skill_markdown()
    
    if output:
        output_path = Path(output)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(content, encoding="utf-8")
        click.echo(f"✅ Skill信息已导出到: {output_path}")
    else:
        click.echo(content)


def main():
    """主入口函数"""
    cli()


if __name__ == "__main__":
    main()

