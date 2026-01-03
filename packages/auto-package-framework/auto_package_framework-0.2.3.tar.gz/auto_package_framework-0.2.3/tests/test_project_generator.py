"""项目生成器测试"""

import tempfile
import shutil
from pathlib import Path
from framework.project_generator import ProjectGenerator


def test_project_generator_init():
    """测试项目生成器初始化"""
    # 使用相对路径指向PROJECT_TEMPLATE
    template_path = Path(__file__).parent.parent.parent / "PROJECT_TEMPLATE"
    if template_path.exists():
        generator = ProjectGenerator(template_path)
        assert generator.template_path == template_path
    else:
        # 如果模板不存在，跳过测试
        pass


def test_generate_replacements():
    """测试替换映射准备"""
    template_path = Path(__file__).parent.parent.parent / "PROJECT_TEMPLATE"
    if not template_path.exists():
        return

    generator = ProjectGenerator(template_path)
    replacements = generator._prepare_replacements(
        "test-package", {"USERNAME": "testuser", "email": "test@example.com"}
    )

    assert "[Project Name]" in replacements
    assert replacements["[Project Name]"] == "test-package"
    assert "test_package" in replacements["your_package_name"]


def test_generate_project():
    """测试项目生成（需要模板存在）"""
    template_path = Path(__file__).parent.parent.parent / "PROJECT_TEMPLATE"
    if not template_path.exists():
        return

    generator = ProjectGenerator(template_path)

    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "test-project"
        replacements = {"USERNAME": "testuser", "email": "test@example.com"}

        project_path = generator.generate(
            project_name="test-package",
            output_path=output_path,
            replacements=replacements,
            project_idea="这是一个测试项目",
        )

        assert project_path.exists()
        assert (project_path / "PROJECT_IDEA.md").exists()
        # 检查PROJECT_IDEA.md包含项目想法
        idea_content = (project_path / "PROJECT_IDEA.md").read_text(encoding="utf-8")
        assert "这是一个测试项目" in idea_content

