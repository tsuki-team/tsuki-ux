"""
tsuki_ux._live
~~~~~~~~~~~~~~
LiveBlock — Docker-style collapsible command output block.

Faithful port of the LiveBlock class from build.py, including:
  - Anti-flicker design: single write() + flush() per frame
  - Rolling window of LIVE_LINES content rows
  - Cursor hide/show via ANSI codes
  - TTY vs pipe/CI mode detection
  - Context manager protocol (__enter__ / __exit__)

Success (collapsed):
    ✔  cargo build --release  [3.2s]

Failure (expanded):
    ✖  cargo build --release
    │  error[E0382]: use of moved value
    │  --> src/main.rs:42:5
    ╰─ exit 1
"""

from __future__ import annotations
import itertools
import shutil
import sys
import threading
import time

from tsuki_ux._color import C_SUCCESS, C_ERROR, C_STEP, DIM, RESET, strip_ansi
from tsuki_ux._symbols import (
    SPINNER_FRAMES, SYM_OK, SYM_FAIL, SYM_PIPE, SYM_ELL, BOX_BL, BOX_H,
)

# Number of content rows visible in the rolling window at any time.
LIVE_LINES = 6


def _is_tty() -> bool:
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


def _term_w() -> int:
    return shutil.get_terminal_size((100, 24)).columns


def _trunc(s: str, max_len: int) -> str:
    if max_len <= 3 or len(s) <= max_len:
        return s
    return s[: max_len - 1] + SYM_ELL


def _fmt_elapsed(s: float) -> str:
    if s < 1.0:
        return f"{int(s * 1000)}ms"
    return f"{s:.1f}s"


class LiveBlock:
    """
    Docker-style collapsible command block with rolling-window output.

    Anti-flicker design:
    ─ Every _redraw() builds the ENTIRE frame as one str and calls
      sys.stdout.write() exactly ONCE, then flush() once.
    ─ Cursor is repositioned with \\r + \\033[{n}A + \\033[J
      (3 escape codes, constant cost regardless of window height).
    ─ Spinner interval is 100 ms (10 fps) — smooth but not CPU-hungry.
    ─ line() only appends to the buffer; the spinner thread picks it up
      on the next tick.
    """

    _INTERVAL = 0.10  # seconds between redraws

    def __init__(self, label: str) -> None:
        w = _term_w()
        max_lbl = max(w - 10, 20)
        self.label = label if len(label) <= max_lbl else label[: max_lbl - 1] + SYM_ELL
        self._full_label = label
        self._lines: list[str] = []
        self._tty = _is_tty()
        self._stop = threading.Event()
        self._lock = threading.Lock()
        self._thread: threading.Thread | None = None
        self._t0: float | None = None
        self._painted = 0   # content rows currently drawn on screen

    # ── Internal ───────────────────────────────────────────────────────────────

    def _redraw(self, frame: str) -> None:
        """Compose and emit one atomic terminal frame (must hold _lock)."""
        w = _term_w()
        buf: list[str] = []

        # 1. Erase previous frame atomically
        buf.append("\r")
        if self._painted > 0:
            buf.append(f"\033[{self._painted}A")
        buf.append("\033[J")   # erase to end of screen — one shot

        # 2. Rolling content window
        visible = self._lines[-LIVE_LINES:] if self._lines else []
        col_w = w - 8
        for s in visible:
            display = s if len(s) <= col_w else s[:col_w]
            buf.append(f"  {DIM}{SYM_PIPE}{RESET}  {DIM}{display}{RESET}\n")

        # 3. Spinner line — no trailing \n so cursor stays here
        buf.append(f"  {C_STEP}{frame}{RESET}  {self.label}\033[K")

        sys.stdout.write("".join(buf))
        sys.stdout.flush()
        self._painted = len(visible)

    def _start_spinner(self) -> None:
        def _spin() -> None:
            for frame in itertools.cycle(SPINNER_FRAMES):
                if self._stop.is_set():
                    break
                with self._lock:
                    self._redraw(frame)
                self._stop.wait(self._INTERVAL)

        self._thread = threading.Thread(target=_spin, daemon=True)
        self._thread.start()

    # ── Public API ─────────────────────────────────────────────────────────────

    def start(self) -> None:
        """Print the spinner header and begin animation."""
        self._t0 = time.monotonic()
        if self._tty:
            # Hide cursor; emit first frame so _redraw knows which row to go back to.
            sys.stdout.write(f"\033[?25l  {C_STEP}{SPINNER_FRAMES[0]}{RESET}  {self.label}\033[K")
            sys.stdout.flush()
            self._start_spinner()
        else:
            print(f"  {DIM}{SYM_ELL}{RESET}  {self.label}")

    def line(self, s: str) -> None:
        """
        Buffer one content line.
        TTY: picked up by the spinner on the next tick.
        Non-TTY / CI: printed immediately for log capture.
        """
        if not s:
            return
        with self._lock:
            self._lines.append(s)
        if not self._tty:
            w = _term_w()
            sys.stdout.write(f"  {DIM}{SYM_PIPE}{RESET}  {s[:w - 8]}\n")
            sys.stdout.flush()

    def finish(self, ok: bool, summary: str = "") -> None:
        """Collapse (ok=True) or expand (ok=False) the block."""
        elapsed = time.monotonic() - self._t0 if self._t0 else 0.0
        elapsed_str = _fmt_elapsed(elapsed)

        # Stop spinner thread before touching the terminal.
        self._stop.set()
        if self._thread:
            self._thread.join(timeout=self._INTERVAL * 3)

        if self._tty:
            buf: list[str] = []
            buf.append("\r")
            if self._painted > 0:
                buf.append(f"\033[{self._painted}A")
            buf.append("\033[J")   # erase block area

            if ok:
                buf.append(
                    f"  {C_SUCCESS}{SYM_OK}{RESET}  {self.label}"
                    f"  {DIM}[{elapsed_str}]{RESET}\n"
                )
            else:
                buf.append(f"  {C_ERROR}{SYM_FAIL}{RESET}  {self.label}\n")
                w = _term_w()
                for l in self._lines:
                    if l:
                        buf.append(f"  {DIM}{SYM_PIPE}{RESET}  {l[:w - 8]}\n")
                msg = summary or "failed"
                buf.append(f"  {DIM}{BOX_BL}{BOX_H} {msg}{RESET}\n")

            # Restore cursor visibility
            buf.append("\033[?25h")
            sys.stdout.write("".join(buf))
            sys.stdout.flush()
        else:
            if ok:
                print(f"  {C_SUCCESS}{SYM_OK}{RESET}  {self.label}  {DIM}[{elapsed_str}]{RESET}")
            else:
                print(f"  {C_ERROR}{SYM_FAIL}{RESET}  {self.label}")
                w = _term_w()
                for l in self._lines:
                    if l:
                        print(f"  {DIM}{SYM_PIPE}{RESET}  {l[:w - 8]}")
                msg = summary or "failed"
                print(f"  {DIM}{BOX_BL}{BOX_H} {msg}{RESET}")

    # ── Context manager ────────────────────────────────────────────────────────

    def __enter__(self) -> "LiveBlock":
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        if exc_type is None:
            self.finish(ok=True)
        else:
            self.finish(ok=False, summary=str(exc_val) if exc_val else "error")
        return False
