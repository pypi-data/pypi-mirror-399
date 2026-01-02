"""SKILL.md manifest parser."""

import re

from pydantic import BaseModel


class SkillManifest(BaseModel):
    """Parsed SKILL.md manifest."""

    name: str
    description: str = ""
    instructions: str = ""
    scripts: list[str] = []
    resources: list[str] = []

    @classmethod
    def parse(cls, content: str, name: str | None = None) -> "SkillManifest":
        """Parse SKILL.md content into manifest."""
        # Extract title (first # heading)
        title_match = re.search(r"^#\s+(.+)$", content, re.MULTILINE)
        skill_name = title_match.group(1).strip() if title_match else (name or "Unknown")

        # Extract sections
        sections: dict[str, str] = {}
        current_section = "preamble"
        current_content: list[str] = []

        for line in content.split("\n"):
            if line.startswith("## "):
                if current_content:
                    sections[current_section] = "\n".join(current_content).strip()
                current_section = line[3:].strip().lower()
                current_content = []
            else:
                current_content.append(line)

        if current_content:
            sections[current_section] = "\n".join(current_content).strip()

        # Parse lists from sections
        def parse_list(text: str) -> list[str]:
            items = []
            for line in text.split("\n"):
                match = re.match(r"^[-*]\s+(.+)$", line)
                if match:
                    items.append(match.group(1).strip())
            return items

        return cls(
            name=skill_name,
            description=sections.get("description", ""),
            instructions=sections.get("instructions", ""),
            scripts=parse_list(sections.get("scripts", "")),
            resources=parse_list(sections.get("resources", "")),
        )
