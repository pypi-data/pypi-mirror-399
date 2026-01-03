"""Skills framework for extending agent capabilities."""

from miu_core.skills.base import Skill
from miu_core.skills.loader import SkillLoader
from miu_core.skills.manifest import SkillManifest
from miu_core.skills.registry import SkillRegistry

__all__ = ["Skill", "SkillLoader", "SkillManifest", "SkillRegistry"]
