"""
tsuki_ux._color
~~~~~~~~~~~~~~~
ANSI color codes with graceful TTY / NO_COLOR / Windows detection.
Mirrors the _enable_windows_ansi() + _detect_color_support() logic from build.py.
"""

from __future__ import annotations
import os
import re
import sys


# ── Windows ANSI activation ────────────────────────────────────────────────────

def _enable_windows_ansi() -> None:
    """Enable ANSI escape processing on Windows 10+ consoles."""
    if sys.platform != "win32":
        return
    try:
        import ctypes
        import ctypes.wintypes
        kernel32 = ctypes.windll.kernel32  # type: ignore[attr-defined]
        for handle_id in (kernel32.GetStdHandle(-10), kernel32.GetStdHandle(-11)):
            mode = ctypes.wintypes.DWORD()
            if kernel32.GetConsoleMode(handle_id, ctypes.byref(mode)):
                kernel32.SetConsoleMode(handle_id, mode.value | 0x0004)
    except Exception:
        pass


_enable_windows_ansi()


# ── Color support detection ────────────────────────────────────────────────────

def _detect_color() -> bool:
    if os.environ.get("FORCE_COLOR"):
        return True
    if not hasattr(sys.stdout, "isatty") or not sys.stdout.isatty():
        return False
    if os.environ.get("TERM") == "dumb":
        return False
    if os.environ.get("NO_COLOR"):
        return False
    return True


COLOR: bool = _detect_color()


# ── ANSI code table ────────────────────────────────────────────────────────────

if COLOR:
    BOLD    = "\033[1m"
    DIM     = "\033[2m"
    ITALIC  = "\033[3m"
    RESET   = "\033[0m"
    ERASE   = "\r\033[K"

    # Base colors
    GREEN   = "\033[32m"
    CYAN    = "\033[36m"
    YELLOW  = "\033[33m"
    RED     = "\033[31m"
    BLUE    = "\033[34m"
    MAGENTA = "\033[35m"
    WHITE   = "\033[37m"

    # Bright variants
    HI_GREEN   = "\033[92m"
    HI_CYAN    = "\033[96m"
    HI_YELLOW  = "\033[93m"
    HI_RED     = "\033[91m"
    HI_BLUE    = "\033[94m"
    HI_MAGENTA = "\033[95m"
    HI_WHITE   = "\033[97m"

    # Semantic aliases (matching ui.go color roles)
    C_SUCCESS = HI_GREEN
    C_WARN    = HI_YELLOW
    C_ERROR   = HI_RED
    C_INFO    = HI_CYAN
    C_STEP    = CYAN
    C_DIM     = DIM

    C_TITLE   = f"{HI_WHITE}{BOLD}"
    C_KEY     = HI_CYAN
    C_VALUE   = HI_YELLOW
    C_STRING  = HI_GREEN
    C_NUMBER  = HI_BLUE
    C_BOOL    = HI_MAGENTA
    C_NULL    = "\033[90m"   # dark gray / bright black
    C_COMMENT = f"{DIM}{ITALIC}"

    C_TB_BORDER  = RED
    C_TB_TITLE   = f"{HI_RED}{BOLD}"
    C_TB_FILE    = HI_CYAN
    C_TB_LINE    = HI_YELLOW
    C_TB_FUNC    = HI_GREEN
    C_TB_CODE    = HI_WHITE
    C_TB_HIGH    = f"{HI_RED}{BOLD}"
    C_TB_LOCALS  = HI_YELLOW
    C_TB_ERRTYPE = f"{HI_RED}{BOLD}"
    C_TB_ERRMSG  = HI_WHITE

else:
    BOLD = DIM = ITALIC = RESET = ERASE = ""
    GREEN = CYAN = YELLOW = RED = BLUE = MAGENTA = WHITE = ""
    HI_GREEN = HI_CYAN = HI_YELLOW = HI_RED = HI_BLUE = HI_MAGENTA = HI_WHITE = ""
    C_SUCCESS = C_WARN = C_ERROR = C_INFO = C_STEP = C_DIM = ""
    C_TITLE = C_KEY = C_VALUE = C_STRING = C_NUMBER = C_BOOL = C_NULL = C_COMMENT = ""
    C_TB_BORDER = C_TB_TITLE = C_TB_FILE = C_TB_LINE = C_TB_FUNC = ""
    C_TB_CODE = C_TB_HIGH = C_TB_LOCALS = C_TB_ERRTYPE = C_TB_ERRMSG = ""


# ── Helpers ────────────────────────────────────────────────────────────────────

_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def strip_ansi(s: str) -> str:
    """Remove ANSI escape sequences for length calculations."""
    return _ANSI_RE.sub("", s)
