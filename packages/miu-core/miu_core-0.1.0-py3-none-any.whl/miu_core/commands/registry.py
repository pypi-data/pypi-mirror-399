"""Command registry for managing slash commands."""

from collections.abc import Iterator
from pathlib import Path

from miu_core.commands.schema import Command, parse_command_file


class CommandRegistry:
    """Registry for managing slash commands."""

    def __init__(self) -> None:
        self._commands: dict[str, Command] = {}

    def register(self, command: Command) -> None:
        """Register a command.

        Args:
            command: Command to register
        """
        self._commands[command.name] = command

    def get(self, name: str) -> Command | None:
        """Get a command by name.

        Args:
            name: Command name (without leading /)

        Returns:
            Command if found, None otherwise
        """
        return self._commands.get(name)

    def load_from_file(self, path: Path) -> Command | None:
        """Load a command from a markdown file.

        Args:
            path: Path to command file

        Returns:
            Loaded command or None if failed
        """
        if not path.exists() or path.suffix != ".md":
            return None

        content = path.read_text(encoding="utf-8")
        frontmatter, body = parse_command_file(content)

        command = Command(
            name=path.stem,
            description=frontmatter.get("description", ""),
            argument_hint=frontmatter.get("argument-hint", ""),
            content=body,
            source_path=path,
        )
        self.register(command)
        return command

    def load_from_directory(self, path: Path) -> int:
        """Load all commands from a directory.

        Args:
            path: Directory path containing command files

        Returns:
            Number of commands loaded
        """
        if not path.is_dir():
            return 0

        count = 0
        for file_path in path.glob("*.md"):
            if self.load_from_file(file_path):
                count += 1
        return count

    def list_commands(self) -> list[Command]:
        """Get all registered commands.

        Returns:
            List of all commands
        """
        return list(self._commands.values())

    def __len__(self) -> int:
        return len(self._commands)

    def __iter__(self) -> Iterator[Command]:
        return iter(self._commands.values())

    def __contains__(self, name: str) -> bool:
        return name in self._commands
