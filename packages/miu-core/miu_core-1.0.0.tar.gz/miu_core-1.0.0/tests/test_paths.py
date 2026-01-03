"""Tests for MiuPaths module."""

from pathlib import Path

import pytest

from miu_core.paths import MiuPaths


@pytest.fixture(autouse=True)
def reset_singleton() -> None:
    """Reset singleton before each test."""
    MiuPaths.reset()
    yield
    MiuPaths.reset()


class TestMiuPaths:
    """Test MiuPaths path resolution."""

    def test_default_path(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """Default path is ~/.miu when no env vars set."""
        monkeypatch.delenv("MIU_DATA_DIR", raising=False)
        monkeypatch.delenv("XDG_DATA_HOME", raising=False)

        paths = MiuPaths()
        assert paths.base == Path.home() / ".miu"

    def test_miu_data_dir_override(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """MIU_DATA_DIR takes highest priority."""
        monkeypatch.setenv("MIU_DATA_DIR", "/custom/miu")
        monkeypatch.setenv("XDG_DATA_HOME", "/xdg/data")

        paths = MiuPaths()
        assert paths.base == Path("/custom/miu")

    def test_xdg_data_home_fallback(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """XDG_DATA_HOME is used when MIU_DATA_DIR not set."""
        monkeypatch.delenv("MIU_DATA_DIR", raising=False)
        monkeypatch.setenv("XDG_DATA_HOME", "/xdg/data")

        paths = MiuPaths()
        assert paths.base == Path("/xdg/data/miu")

    def test_subdirectories(self, tmp_path: Path) -> None:
        """Verify subdirectory paths are correct."""
        paths = MiuPaths(base_dir=tmp_path)

        assert paths.sessions == tmp_path / "sessions"
        assert paths.logs == tmp_path / "logs"
        assert paths.code == tmp_path / "code"
        assert paths.studio == tmp_path / "studio"

    def test_get_session_path(self, tmp_path: Path) -> None:
        """Session path includes session ID."""
        paths = MiuPaths(base_dir=tmp_path)
        session_path = paths.get_session_path("test123")
        assert session_path == tmp_path / "sessions" / "test123.jsonl"

    def test_get_log_path(self, tmp_path: Path) -> None:
        """Log path includes session ID prefix."""
        paths = MiuPaths(base_dir=tmp_path)
        log_path = paths.get_log_path("test123")
        assert log_path == tmp_path / "logs" / "session_test123.jsonl"

    def test_ensure_dir(self, tmp_path: Path) -> None:
        """ensure_dir creates directory if needed."""
        paths = MiuPaths(base_dir=tmp_path)
        new_dir = tmp_path / "new" / "nested" / "dir"

        result = paths.ensure_dir(new_dir)

        assert result == new_dir
        assert new_dir.exists()
        assert new_dir.is_dir()

    def test_singleton_pattern(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        """get() returns same instance."""
        monkeypatch.setenv("MIU_DATA_DIR", str(tmp_path))

        paths1 = MiuPaths.get()
        paths2 = MiuPaths.get()

        assert paths1 is paths2

    def test_singleton_reset(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """reset() clears singleton."""
        monkeypatch.setenv("MIU_DATA_DIR", "/first/path")
        paths1 = MiuPaths.get()

        MiuPaths.reset()
        monkeypatch.setenv("MIU_DATA_DIR", "/second/path")
        paths2 = MiuPaths.get()

        assert paths1.base == Path("/first/path")
        assert paths2.base == Path("/second/path")
        assert paths1 is not paths2
