"""
tsuki_ux._spinner
~~~~~~~~~~~~~~~~~
Standalone spinner for tasks that don't stream line output.
Port of ui.go's Spinner type.

Usage:
    s = Spinner("Detectando puerto…")
    s.start()
    time.sleep(2)
    s.stop(ok=True, msg="Puerto detectado: /dev/ttyUSB0")

    # Custom frames:
    from tsuki_ux import SPINNER_FRAMES_MOON
    s = Spinner("Compilando…", frames=SPINNER_FRAMES_MOON)
    s.start()
    ...
    s.stop(ok=True)

    # Context manager:
    with Spinner("Instalando paquetes…") as s:
        time.sleep(1)
"""

from __future__ import annotations
import itertools
import sys
import threading
import time
from typing import List, Optional

from tsuki_ux._color import C_INFO, C_SUCCESS, C_ERROR, DIM, RESET
from tsuki_ux._symbols import SPINNER_FRAMES, SYM_OK, SYM_FAIL, SYM_ELL


def _is_tty() -> bool:
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


class Spinner:
    """Animated spinner — TTY-safe, non-blocking, supports custom frames."""

    _INTERVAL = 0.08  # seconds (≈ 12 fps — matches ui.go's 80 ms)

    def __init__(self, msg: str, frames: Optional[List[str]] = None) -> None:
        self.msg = msg
        self._frames = frames if frames is not None else SPINNER_FRAMES
        self._stop_event = threading.Event()
        self._thread: Optional[threading.Thread] = None
        self._tty = _is_tty()
        self._lock = threading.Lock()
        self._start_time: Optional[float] = None

    # ── Internal ───────────────────────────────────────────────────────────────

    def _fmt_elapsed(self) -> str:
        if self._start_time is None:
            return ""
        s = time.monotonic() - self._start_time
        if s < 1.0:
            return f"{int(s * 1000)}ms"
        return f"{s:.1f}s"

    # ── Public API ─────────────────────────────────────────────────────────────

    def start(self) -> None:
        """Start the spinner animation (non-blocking)."""
        self._start_time = time.monotonic()
        if not self._tty:
            sys.stdout.write(f"  {DIM}{SYM_ELL}{RESET}  {self.msg}\n")
            sys.stdout.flush()
            return

        sys.stdout.write(f"\033[?25l  {C_INFO}{self._frames[0]}{RESET}  {self.msg}")
        sys.stdout.flush()

        def _run() -> None:
            for frame in itertools.cycle(self._frames):
                if self._stop_event.is_set():
                    break
                with self._lock:
                    sys.stdout.write(f"\r  {C_INFO}{frame}{RESET}  {self.msg}")
                    sys.stdout.flush()
                self._stop_event.wait(self._INTERVAL)

        self._thread = threading.Thread(target=_run, daemon=True)
        self._thread.start()

    def update_label(self, msg: str) -> None:
        """Change the spinner label mid-animation."""
        with self._lock:
            self.msg = msg

    def stop(self, ok: bool = True, msg: str = "") -> None:
        """Stop the spinner and print the final status line.

        ok=True  →  ✔  label  [1.2s]
        ok=False →  ✖  label  reason
        """
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=self._INTERVAL * 3)

        elapsed = self._fmt_elapsed()

        if self._tty:
            sys.stdout.write("\r\033[K\033[?25h")

        final = msg or self.msg
        if ok:
            timing = f"  {DIM}[{elapsed}]{RESET}" if elapsed else ""
            sys.stdout.write(f"  {C_SUCCESS}{SYM_OK}{RESET}  {final}{timing}\n")
        else:
            reason = msg or "failed"
            sys.stdout.write(f"  {C_ERROR}{SYM_FAIL}{RESET}  {self.msg}  {DIM}{reason}{RESET}\n")
        sys.stdout.flush()

    def stop_silent(self) -> None:
        """Stop and erase without printing anything — used by LiveBlock."""
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=self._INTERVAL * 3)
        if self._tty:
            sys.stdout.write("\r\033[K\033[?25h")
            sys.stdout.flush()

    # ── Context manager ────────────────────────────────────────────────────────

    def __enter__(self) -> "Spinner":
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        self.stop(ok=exc_type is None, msg=str(exc_val) if exc_val else "")
        return False