"""
tsuki_ux._spinner
~~~~~~~~~~~~~~~~~
Standalone braille spinner for tasks that don't stream line output.
Port of ui.go's Spinner type.

Usage:
    s = Spinner("Detectando puerto…")
    s.start()
    time.sleep(2)
    s.stop(ok=True, msg="Puerto detectado: /dev/ttyUSB0")
"""

from __future__ import annotations
import itertools
import sys
import threading
import time

from tsuki_ux._color import C_INFO, C_SUCCESS, C_ERROR, DIM, RESET
from tsuki_ux._symbols import SPINNER_FRAMES, SYM_OK, SYM_FAIL, SYM_ELL


def _is_tty() -> bool:
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


class Spinner:
    """Braille spinner — TTY-safe, non-blocking."""

    _INTERVAL = 0.08  # seconds (≈ 12 fps — matches ui.go's 80 ms)

    def __init__(self, msg: str) -> None:
        self.msg = msg
        self._stop_event = threading.Event()
        self._thread: threading.Thread | None = None
        self._tty = _is_tty()

    def start(self) -> None:
        """Start the spinner animation (non-blocking)."""
        if not self._tty:
            sys.stdout.write(f"  {DIM}{SYM_ELL}{RESET}  {self.msg}\n")
            sys.stdout.flush()
            return

        # Print initial frame without trailing newline so \\r can overwrite it.
        sys.stdout.write(f"  {C_INFO}{SPINNER_FRAMES[0]}{RESET}  {self.msg}")
        sys.stdout.flush()

        def _run() -> None:
            for frame in itertools.cycle(SPINNER_FRAMES):
                if self._stop_event.is_set():
                    break
                sys.stdout.write(f"\r  {C_INFO}{frame}{RESET}  {self.msg}")
                sys.stdout.flush()
                self._stop_event.wait(self._INTERVAL)

        self._thread = threading.Thread(target=_run, daemon=True)
        self._thread.start()

    def stop(self, ok: bool = True, msg: str = "") -> None:
        """Stop the spinner and print the final status line."""
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=self._INTERVAL * 3)

        if self._tty:
            # Erase the spinner line before printing the result.
            sys.stdout.write(f"\r\033[K")

        final = msg or self.msg
        if ok:
            sys.stdout.write(f"  {C_SUCCESS}{SYM_OK}{RESET}  {final}\n")
        else:
            sys.stdout.write(f"  {C_ERROR}{SYM_FAIL}{RESET}  {final}\n")
        sys.stdout.flush()

    def stop_silent(self) -> None:
        """Stop and erase without printing anything — used by LiveBlock."""
        self._stop_event.set()
        if self._thread:
            self._thread.join(timeout=self._INTERVAL * 3)
        if self._tty:
            sys.stdout.write("\r\033[K")
            sys.stdout.flush()

    def __enter__(self) -> "Spinner":
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        self.stop(ok=exc_type is None, msg=str(exc_val) if exc_val else "")
        return False
