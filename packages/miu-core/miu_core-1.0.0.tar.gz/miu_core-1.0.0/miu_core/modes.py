"""Agent mode management with safety levels."""

from collections.abc import Callable
from dataclasses import dataclass, field
from enum import StrEnum, auto
from typing import Any


class ModeSafety(StrEnum):
    """Safety level for agent modes."""

    SAFE = auto()  # Read-only, no dangerous operations
    NEUTRAL = auto()  # Default, requires approval for dangerous ops
    DESTRUCTIVE = auto()  # Auto-approves some write operations
    YOLO = auto()  # Auto-approves all operations


class AgentMode(StrEnum):
    """Agent operation modes."""

    NORMAL = auto()  # Default mode, requires approval
    PLAN = auto()  # Read-only planning mode
    ASK = auto()  # Always ask before any action
    AUTO = auto()  # Auto-approve all operations

    @property
    def display_name(self) -> str:
        """Human-readable name."""
        return MODE_CONFIGS[self].display_name

    @property
    def description(self) -> str:
        """Mode description."""
        return MODE_CONFIGS[self].description

    @property
    def safety(self) -> ModeSafety:
        """Safety level for this mode."""
        return MODE_CONFIGS[self].safety

    @property
    def auto_approve(self) -> bool:
        """Whether this mode auto-approves tools."""
        return MODE_CONFIGS[self].auto_approve

    @property
    def config_overrides(self) -> dict[str, Any]:
        """Config overrides for this mode."""
        return MODE_CONFIGS[self].config_overrides


@dataclass(frozen=True)
class ModeConfig:
    """Configuration for an agent mode."""

    display_name: str
    description: str
    safety: ModeSafety = ModeSafety.NEUTRAL
    auto_approve: bool = False
    config_overrides: dict[str, Any] = field(default_factory=dict)


# Read-only tools for plan mode
PLAN_MODE_TOOLS = ["read", "glob", "grep", "ls"]


MODE_CONFIGS: dict[AgentMode, ModeConfig] = {
    AgentMode.NORMAL: ModeConfig(
        display_name="normal",
        description="Requires approval for write operations",
        safety=ModeSafety.NEUTRAL,
        auto_approve=False,
    ),
    AgentMode.PLAN: ModeConfig(
        display_name="plan mode",
        description="Read-only mode for exploration",
        safety=ModeSafety.SAFE,
        auto_approve=True,
        config_overrides={"enabled_tools": PLAN_MODE_TOOLS},
    ),
    AgentMode.ASK: ModeConfig(
        display_name="ask mode",
        description="Always ask before any action",
        safety=ModeSafety.SAFE,
        auto_approve=False,
    ),
    AgentMode.AUTO: ModeConfig(
        display_name="auto mode",
        description="Auto-approves all operations",
        safety=ModeSafety.YOLO,
        auto_approve=True,
    ),
}


# Mode cycle order
MODE_ORDER = [AgentMode.NORMAL, AgentMode.PLAN, AgentMode.ASK, AgentMode.AUTO]


def next_mode(current: AgentMode) -> AgentMode:
    """Get next mode in cycle."""
    idx = MODE_ORDER.index(current)
    return MODE_ORDER[(idx + 1) % len(MODE_ORDER)]


class ModeManager:
    """Manage agent mode state."""

    def __init__(self, initial: AgentMode = AgentMode.NORMAL) -> None:
        self._mode = initial
        self._on_change: list[Callable[[AgentMode], None]] = []

    @property
    def mode(self) -> AgentMode:
        """Current mode."""
        return self._mode

    @mode.setter
    def mode(self, value: AgentMode) -> None:
        """Set mode and notify listeners."""
        if value != self._mode:
            self._mode = value
            for callback in self._on_change:
                callback(value)

    def cycle(self) -> AgentMode:
        """Cycle to next mode."""
        self.mode = next_mode(self._mode)
        return self._mode

    def on_change(self, callback: Callable[[AgentMode], None]) -> None:
        """Register mode change callback."""
        self._on_change.append(callback)

    @property
    def label(self) -> str:
        """Display label."""
        return self._mode.display_name

    @property
    def safety(self) -> ModeSafety:
        """Current mode safety level."""
        return self._mode.safety

    @property
    def auto_approve(self) -> bool:
        """Whether current mode auto-approves."""
        return self._mode.auto_approve

    def format_status(self) -> str:
        """Format for status bar."""
        return f"{self.label} (shift+tab to cycle)"
