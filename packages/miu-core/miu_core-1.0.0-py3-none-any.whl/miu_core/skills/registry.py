"""Skill registry for managing loaded skills."""

from pathlib import Path

from miu_core.skills.base import Skill
from miu_core.skills.loader import SkillLoader


class SkillRegistry:
    """Registry for managing and querying skills."""

    def __init__(self) -> None:
        self._skills: dict[str, Skill] = {}
        self._loader = SkillLoader()

    def register(self, skill: Skill) -> None:
        """Register a skill."""
        self._skills[skill.name.lower()] = skill

    def get(self, name: str) -> Skill | None:
        """Get skill by name."""
        return self._skills.get(name.lower())

    def load_from_dir(self, path: Path) -> int:
        """Load skills from directory.

        Expects structure:
            path/
                skill-name-1/
                    SKILL.md
                skill-name-2/
                    SKILL.md

        Returns number of skills loaded.
        """
        if not path.exists() or not path.is_dir():
            return 0

        count = 0
        for skill_dir in path.iterdir():
            if not skill_dir.is_dir():
                continue
            skill = self._loader.load(skill_dir)
            if skill:
                self.register(skill)
                count += 1
        return count

    def build_system_prompt(self) -> str:
        """Build system prompt fragment from all skills."""
        if not self._skills:
            return ""

        parts = ["# Active Skills\n"]
        for skill in self._skills.values():
            parts.append(skill.to_prompt())
        return "\n".join(parts)

    def list_skills(self) -> list[Skill]:
        """Get all registered skills."""
        return list(self._skills.values())

    def __len__(self) -> int:
        return len(self._skills)

    def __iter__(self):  # type: ignore[no-untyped-def]
        return iter(self._skills.values())
