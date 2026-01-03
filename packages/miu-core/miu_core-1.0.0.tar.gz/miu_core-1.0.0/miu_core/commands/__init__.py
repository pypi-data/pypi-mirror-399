"""Slash commands system."""

from miu_core.commands.executor import CommandExecutor
from miu_core.commands.registry import CommandRegistry
from miu_core.commands.schema import Command

__all__ = [
    "Command",
    "CommandExecutor",
    "CommandRegistry",
]
