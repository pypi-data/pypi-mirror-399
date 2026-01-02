"""Skill directory loader."""

from pathlib import Path

from miu_core.skills.base import Skill
from miu_core.skills.manifest import SkillManifest


class SkillLoader:
    """Loads skills from directories."""

    def load(self, skill_dir: Path) -> Skill | None:
        """Load a skill from directory containing SKILL.md."""
        manifest_path = skill_dir / "SKILL.md"
        if not manifest_path.exists():
            return None

        content = manifest_path.read_text(encoding="utf-8")
        manifest = SkillManifest.parse(content, name=skill_dir.name)

        # Resolve script paths
        scripts: list[Path] = []
        for script_ref in manifest.scripts:
            # Handle "scripts/xxx.py" or just "xxx.py"
            if ":" in script_ref:
                script_ref = script_ref.split(":")[0].strip().strip("`")
            script_path = skill_dir / script_ref
            if script_path.exists():
                scripts.append(script_path)

        # Resolve resource paths
        resources: list[Path] = []
        for resource_ref in manifest.resources:
            if ":" in resource_ref:
                resource_ref = resource_ref.split(":")[0].strip().strip("`")
            resource_path = skill_dir / resource_ref
            if resource_path.exists():
                resources.append(resource_path)

        return Skill(
            name=manifest.name,
            description=manifest.description,
            instructions=manifest.instructions,
            scripts=scripts,
            resources=resources,
            path=skill_dir,
        )
