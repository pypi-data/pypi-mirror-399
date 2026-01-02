"""Base skill interface."""

from pathlib import Path

from pydantic import BaseModel


class Skill(BaseModel):
    """A skill that extends agent capabilities."""

    name: str
    description: str
    instructions: str
    scripts: list[Path] = []
    resources: list[Path] = []
    path: Path | None = None

    def to_prompt(self) -> str:
        """Convert skill to system prompt fragment."""
        parts = [f"## {self.name}\n"]
        if self.description:
            parts.append(f"{self.description}\n")
        if self.instructions:
            parts.append(f"\n{self.instructions}\n")
        if self.scripts:
            parts.append("\n### Available Scripts")
            for script in self.scripts:
                parts.append(f"- `{script.name}`: {script}")
            parts.append("")
        return "\n".join(parts)
