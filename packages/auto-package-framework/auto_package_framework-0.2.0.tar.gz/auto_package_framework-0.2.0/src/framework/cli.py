"""命令行接口"""

import click
from pathlib import Path
from typing import Optional

from .core import AutoPackageFramework


@click.command()
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
def main(
    config: str,
    project_name: str,
    idea: str,
    output: Optional[str],
    github_repo: Optional[str],
    publish: bool,
    username: Optional[str],
    email: Optional[str],
):
    """
    Auto Package Framework - 自动化Python包创建和发布工具
    """
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


if __name__ == "__main__":
    main()

