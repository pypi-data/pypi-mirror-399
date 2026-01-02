"""Hooks system for lifecycle events."""

from miu_core.hooks.events import HookEvent, HookInput, HookResult
from miu_core.hooks.executor import HookExecutor
from miu_core.hooks.registry import HookRegistry

__all__ = ["HookEvent", "HookExecutor", "HookInput", "HookRegistry", "HookResult"]
