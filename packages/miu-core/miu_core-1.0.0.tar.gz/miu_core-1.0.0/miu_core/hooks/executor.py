"""Hook script executor."""

import asyncio
import sys
from pathlib import Path

from miu_core.hooks.events import HookInput, HookResult


class HookExecutor:
    """Execute hook scripts in various languages."""

    async def execute(self, script: Path, input_data: HookInput, timeout: int = 30) -> HookResult:
        """Execute a hook script with input data.

        Supports:
        - Python (.py)
        - Node.js (.js, .mjs)
        - Shell (.sh)
        """
        if not script.exists():
            return HookResult(
                success=False, output=f"Script not found: {script}", should_block=False
            )

        suffix = script.suffix.lower()
        if suffix == ".py":
            cmd = [sys.executable, str(script)]
        elif suffix in (".js", ".mjs"):
            cmd = ["node", str(script)]
        elif suffix == ".sh":
            cmd = ["bash", str(script)]
        else:
            return HookResult(
                success=False,
                output=f"Unsupported script type: {suffix}",
                should_block=False,
            )

        try:
            proc = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            input_json = input_data.model_dump_json().encode()
            stdout, stderr = await asyncio.wait_for(proc.communicate(input_json), timeout=timeout)

            if proc.returncode != 0:
                return HookResult(
                    success=False,
                    output=stderr.decode("utf-8", errors="replace"),
                    should_block=False,
                )

            # Try to parse JSON output
            output_text = stdout.decode("utf-8", errors="replace").strip()
            try:
                return HookResult.model_validate_json(output_text)
            except Exception:
                # If not JSON, treat as plain text output
                return HookResult(success=True, output=output_text)

        except TimeoutError:
            if proc:
                proc.kill()
            return HookResult(
                success=False, output=f"Hook timed out after {timeout}s", should_block=False
            )
        except Exception as e:
            return HookResult(success=False, output=str(e), should_block=False)
