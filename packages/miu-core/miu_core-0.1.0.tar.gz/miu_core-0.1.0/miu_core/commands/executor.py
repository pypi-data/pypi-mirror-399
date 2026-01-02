"""Command executor for parsing and expanding slash commands."""

from miu_core.commands.registry import CommandRegistry


class CommandExecutor:
    """Execute slash commands by parsing and expanding templates."""

    def __init__(self, registry: CommandRegistry) -> None:
        """Initialize executor with command registry.

        Args:
            registry: Registry containing available commands
        """
        self.registry = registry

    def parse(self, input_str: str) -> tuple[str, str] | None:
        """Parse '/command args' format.

        Args:
            input_str: Input string to parse

        Returns:
            Tuple of (command_name, args) or None if not a command
        """
        if not input_str.startswith("/"):
            return None

        stripped = input_str[1:].strip()
        if not stripped:
            return None

        parts = stripped.split(maxsplit=1)
        command_name = parts[0]
        args = parts[1] if len(parts) > 1 else ""

        return (command_name, args)

    def expand(self, command_name: str, args: str) -> str:
        """Expand command template with arguments.

        Args:
            command_name: Name of the command (without /)
            args: Arguments to pass to the command

        Returns:
            Expanded command content

        Raises:
            ValueError: If command not found
        """
        command = self.registry.get(command_name)
        if not command:
            raise ValueError(f"Unknown command: /{command_name}")
        return command.expand(args)

    def execute(self, input_str: str) -> str | None:
        """Parse and expand a command string.

        Args:
            input_str: Input string that may be a command

        Returns:
            Expanded command content or None if not a command

        Raises:
            ValueError: If command not found
        """
        parsed = self.parse(input_str)
        if not parsed:
            return None

        command_name, args = parsed
        return self.expand(command_name, args)

    def is_command(self, input_str: str) -> bool:
        """Check if input is a slash command.

        Args:
            input_str: Input to check

        Returns:
            True if input starts with /
        """
        return input_str.strip().startswith("/")
