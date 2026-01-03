"""Auto Package Framework - AI驱动的自动化包创建和发布框架"""

__version__ = "0.2.3"

from .core import AutoPackageFramework
from .skill import SkillInterface, get_skill_interface

__all__ = ["AutoPackageFramework", "SkillInterface", "get_skill_interface"]
