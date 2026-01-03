"""Centralized path management for miu packages.

Provides consistent storage paths across all miu packages with XDG compliance
and environment variable overrides.
"""

import os
from pathlib import Path


class MiuPaths:
    """Centralized path resolver for miu storage.

    Path resolution priority:
    1. MIU_DATA_DIR env var (explicit override)
    2. XDG_DATA_HOME/miu (Linux/freedesktop compliance)
    3. ~/.miu (cross-platform default)
    """

    _instance: "MiuPaths | None" = None

    def __init__(self, base_dir: Path | None = None) -> None:
        """Initialize paths.

        Args:
            base_dir: Override base directory (for testing)
        """
        self._base_dir = base_dir or self._resolve_base_dir()

    @classmethod
    def get(cls) -> "MiuPaths":
        """Get singleton instance."""
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    @classmethod
    def reset(cls) -> None:
        """Reset singleton (for testing)."""
        cls._instance = None

    @staticmethod
    def _resolve_base_dir() -> Path:
        """Resolve base directory with priority fallbacks."""
        # Priority 1: Explicit override
        if env_dir := os.environ.get("MIU_DATA_DIR"):
            return Path(env_dir)

        # Priority 2: XDG compliance
        if xdg_data := os.environ.get("XDG_DATA_HOME"):
            return Path(xdg_data) / "miu"

        # Priority 3: Default ~/.miu
        return Path.home() / ".miu"

    @property
    def base(self) -> Path:
        """Base miu data directory."""
        return self._base_dir

    @property
    def sessions(self) -> Path:
        """Shared sessions directory."""
        return self._base_dir / "sessions"

    @property
    def logs(self) -> Path:
        """Shared logs directory."""
        return self._base_dir / "logs"

    @property
    def code(self) -> Path:
        """miu_code specific directory."""
        return self._base_dir / "code"

    @property
    def studio(self) -> Path:
        """miu_studio specific directory."""
        return self._base_dir / "studio"

    def ensure_dir(self, path: Path) -> Path:
        """Ensure directory exists, create if needed.

        Args:
            path: Directory path to ensure

        Returns:
            The path (for chaining)
        """
        path.mkdir(parents=True, exist_ok=True)
        return path

    def get_session_path(self, session_id: str) -> Path:
        """Get path for a session file.

        Args:
            session_id: Session identifier

        Returns:
            Path to session JSONL file
        """
        return self.sessions / f"{session_id}.jsonl"

    def get_log_path(self, session_id: str) -> Path:
        """Get path for a log file.

        Args:
            session_id: Session identifier

        Returns:
            Path to log JSONL file
        """
        return self.logs / f"session_{session_id}.jsonl"

    @property
    def history(self) -> Path:
        """Command history file path."""
        return self.code / "history"
