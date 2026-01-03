from __future__ import annotations

import subprocess
from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class CommandResult:
    ok: bool
    stdout: str
    stderr: str
    error: str | None = None


def run_cmd(cmd: list[str], *, timeout: int = 5) -> CommandResult:
    try:
        p = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
        )
        out = (p.stdout or "").strip()
        err = (p.stderr or "").strip()
        return CommandResult(ok=(p.returncode == 0), stdout=out, stderr=err, error=None)
    except FileNotFoundError:
        return CommandResult(ok=False, stdout="", stderr="", error="command not found")
    except Exception as e:
        return CommandResult(ok=False, stdout="", stderr="", error=str(e))
