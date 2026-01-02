"""Hook registry for managing hooks."""

from pathlib import Path

from miu_core.hooks.events import HookEvent, HookInput, HookResult
from miu_core.hooks.executor import HookExecutor


class HookRegistry:
    """Registry for managing and executing hooks."""

    def __init__(self) -> None:
        self._hooks: dict[HookEvent, list[Path]] = {event: [] for event in HookEvent}
        self._executor = HookExecutor()

    def register(self, event: HookEvent, script: Path) -> None:
        """Register a hook script for an event."""
        if script.exists():
            self._hooks[event].append(script)

    def load_from_dir(self, path: Path) -> int:
        """Load hooks from directory.

        Expected structure:
            path/
                session-start.py
                pre-tool-use.sh
                post-message.js
        """
        if not path.exists() or not path.is_dir():
            return 0

        # Map filenames to events
        name_map = {
            "session-start": HookEvent.SESSION_START,
            "session-end": HookEvent.SESSION_END,
            "pre-message": HookEvent.PRE_MESSAGE,
            "post-message": HookEvent.POST_MESSAGE,
            "pre-tool-use": HookEvent.PRE_TOOL_USE,
            "post-tool-use": HookEvent.POST_TOOL_USE,
        }

        count = 0
        for script in path.iterdir():
            if not script.is_file():
                continue
            stem = script.stem.lower()
            if stem in name_map:
                self.register(name_map[stem], script)
                count += 1
        return count

    async def execute(self, event: HookEvent, input_data: HookInput) -> list[HookResult]:
        """Execute all hooks for an event."""
        results: list[HookResult] = []
        for script in self._hooks[event]:
            result = await self._executor.execute(script, input_data)
            results.append(result)
            if result.should_block:
                break
        return results

    def has_hooks(self, event: HookEvent) -> bool:
        """Check if event has registered hooks."""
        return len(self._hooks[event]) > 0

    def __len__(self) -> int:
        return sum(len(hooks) for hooks in self._hooks.values())
