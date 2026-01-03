"""Command schema definitions."""

from pathlib import Path

from pydantic import BaseModel, Field


class Command(BaseModel):
    """Slash command definition."""

    name: str = Field(description="Command name without leading /")
    description: str = Field(default="", description="Short description of the command")
    argument_hint: str = Field(
        default="", alias="argument-hint", description="Hint for expected arguments"
    )
    content: str = Field(description="Command template content")
    source_path: Path | None = Field(default=None, description="Path to source file")

    def expand(self, arguments: str) -> str:
        """Expand command template with arguments.

        Args:
            arguments: Arguments to substitute

        Returns:
            Expanded command content
        """
        return self.content.replace("$ARGUMENTS", arguments)


def parse_command_file(content: str) -> tuple[dict[str, str], str]:
    """Parse a command markdown file with frontmatter.

    Args:
        content: File content

    Returns:
        Tuple of (frontmatter dict, body content)
    """
    frontmatter: dict[str, str] = {}
    body = content

    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            # Parse frontmatter
            for line in parts[1].strip().split("\n"):
                if ":" in line:
                    key, value = line.split(":", 1)
                    frontmatter[key.strip()] = value.strip()
            body = parts[2].strip()

    return frontmatter, body
