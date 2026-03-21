"""
tsuki_ux._run
~~~~~~~~~~~~~
run() — execute a subprocess displaying its output inside a LiveBlock.

Port of the run() function from build.py:
  - Uses readline() instead of iter(file) to avoid buffering bursts
    from cargo/npm/etc.
  - Opens stdout in binary mode and decodes per-line to guarantee UTF-8
    on Windows without reconfiguring the codec.
  - Collapses on success, expands on failure.
"""

from __future__ import annotations
import subprocess
import sys
from typing import Sequence

from tsuki_ux._live import LiveBlock
from tsuki_ux._symbols import SYM_ELL


def run(
    cmd: Sequence[str],
    *,
    cwd: str | None = None,
    env: dict | None = None,
    check: bool = True,
    label: str | None = None,
) -> subprocess.CompletedProcess:
    """
    Execute *cmd* with its output streamed into a LiveBlock.

    Success → block collapses:  ✔  <label>  [1.3s]
    Failure → block expands:    ✖  <label>
                                │  error output…
                                ╰─ exit 1

    Args:
        cmd:    Command and arguments.
        cwd:    Working directory (passed to Popen).
        env:    Environment variables (passed to Popen).
        check:  If True (default), raise CalledProcessError on non-zero exit.
        label:  Override the display label shown in the block header.
                Defaults to a truncated command string.

    Returns:
        subprocess.CompletedProcess with stdout captured in .stdout.
    """
    if label:
        display = label
    else:
        parts = [str(x) for x in cmd]
        display = " ".join(parts)
        if len(display) > 64:
            # Shorten: keep binary name + as many args as fit
            display = parts[0].split("/")[-1].split("\\")[-1]
            for p in parts[1:]:
                candidate = display + " " + p
                if len(candidate) > 62:
                    display += f" {SYM_ELL}"
                    break
                display = candidate

    blk = LiveBlock(display)
    blk.start()

    proc = subprocess.Popen(
        cmd,
        cwd=cwd,
        env=env,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        bufsize=0,   # unbuffered — we want every byte as it arrives
    )

    captured: list[bytes] = []

    # readline() instead of iter(proc.stdout) avoids the 8 KB read-buffer
    # delay that causes cargo/npm output to arrive in large bursts.
    assert proc.stdout is not None
    while True:
        raw = proc.stdout.readline()
        if not raw:
            break
        captured.append(raw)
        line = raw.decode("utf-8", errors="replace").rstrip("\r\n")
        blk.line(line)

    proc.wait()
    stdout_bytes = b"".join(captured)

    ok = proc.returncode == 0
    blk._rc = proc.returncode  # type: ignore[attr-defined]
    blk.finish(ok=ok, summary="" if ok else f"exit {proc.returncode}")

    if check and not ok:
        raise subprocess.CalledProcessError(
            proc.returncode, cmd, output=stdout_bytes
        )

    return subprocess.CompletedProcess(
        args=cmd,
        returncode=proc.returncode,
        stdout=stdout_bytes,
    )
