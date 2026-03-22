"""
tsuki_ux._color
~~~~~~~~~~~~~~~
ANSI color codes with graceful TTY / NO_COLOR / Windows detection.
Includes text decoration (underline, strikethrough, overline, blink, reverse),
256-color, and truecolor/RGB support.
"""

from __future__ import annotations
import os
import re
import sys
from typing import Optional


# ── Windows ANSI activation ────────────────────────────────────────────────────

def _enable_windows_ansi() -> None:
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
    # Text attributes
    BOLD       = "\033[1m"
    DIM        = "\033[2m"
    ITALIC     = "\033[3m"
    UNDERLINE  = "\033[4m"
    BLINK      = "\033[5m"
    REVERSE    = "\033[7m"
    STRIKE     = "\033[9m"
    OVERLINE   = "\033[53m"
    RESET      = "\033[0m"
    ERASE      = "\r\033[K"

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

    # Semantic aliases
    C_SUCCESS   = f"\033[1;92m"
    C_WARN      = f"\033[1;93m"
    C_ERROR     = f"\033[1;91m"
    C_INFO      = HI_CYAN
    C_STEP      = CYAN
    C_DIM       = DIM
    C_HIGHLIGHT = f"\033[1;95m"
    C_ACCENT    = f"\033[1;96m"

    C_TITLE   = f"{HI_WHITE}{BOLD}"
    C_KEY     = HI_CYAN
    C_VALUE   = HI_YELLOW
    C_STRING  = HI_GREEN
    C_NUMBER  = HI_BLUE
    C_BOOL    = HI_MAGENTA
    C_NULL    = "\033[90m"
    C_COMMENT = f"{DIM}{ITALIC}"
    C_MUTED   = "\033[90m"

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
    BOLD = DIM = ITALIC = UNDERLINE = BLINK = REVERSE = STRIKE = OVERLINE = RESET = ERASE = ""
    GREEN = CYAN = YELLOW = RED = BLUE = MAGENTA = WHITE = ""
    HI_GREEN = HI_CYAN = HI_YELLOW = HI_RED = HI_BLUE = HI_MAGENTA = HI_WHITE = ""
    C_SUCCESS = C_WARN = C_ERROR = C_INFO = C_STEP = C_DIM = C_HIGHLIGHT = C_ACCENT = ""
    C_TITLE = C_KEY = C_VALUE = C_STRING = C_NUMBER = C_BOOL = C_NULL = C_COMMENT = C_MUTED = ""
    C_TB_BORDER = C_TB_TITLE = C_TB_FILE = C_TB_LINE = C_TB_FUNC = ""
    C_TB_CODE = C_TB_HIGH = C_TB_LOCALS = C_TB_ERRTYPE = C_TB_ERRMSG = ""


# ── Helpers ────────────────────────────────────────────────────────────────────

_ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def strip_ansi(s: str) -> str:
    """Remove ANSI escape sequences for length calculations."""
    return _ANSI_RE.sub("", s)


def color256(n: int, text: str) -> str:
    """Apply a 256-color palette index (0–255) as foreground."""
    if not COLOR:
        return text
    return f"\033[38;5;{n}m{text}{RESET}"


def bg_color256(n: int, text: str) -> str:
    """Apply a 256-color palette index (0–255) as background."""
    if not COLOR:
        return text
    return f"\033[48;5;{n}m{text}{RESET}"


def truecolor(r: int, g: int, b: int, text: str) -> str:
    """Apply an RGB foreground color (0–255 per channel)."""
    if not COLOR:
        return text
    return f"\033[38;2;{r};{g};{b}m{text}{RESET}"


def bg_truecolor(r: int, g: int, b: int, text: str) -> str:
    """Apply an RGB background color."""
    if not COLOR:
        return text
    return f"\033[48;2;{r};{g};{b}m{text}{RESET}"


def underline(text: str) -> str:
    """Return text with underline decoration."""
    return f"{UNDERLINE}{text}{RESET}" if COLOR else text


def strike(text: str) -> str:
    """Return text with strikethrough decoration."""
    return f"{STRIKE}{text}{RESET}" if COLOR else text


def overline(text: str) -> str:
    """Return text with overline decoration."""
    return f"{OVERLINE}{text}{RESET}" if COLOR else text


def blink(text: str) -> str:
    """Return blinking text (not supported in all terminals)."""
    return f"{BLINK}{text}{RESET}" if COLOR else text


def reverse(text: str) -> str:
    """Return text with foreground/background swapped."""
    return f"{REVERSE}{text}{RESET}" if COLOR else text


def bold(text: str) -> str:
    """Return bold text."""
    return f"{BOLD}{text}{RESET}" if COLOR else text


def dim(text: str) -> str:
    """Return dim/faint text."""
    return f"{DIM}{text}{RESET}" if COLOR else text


def italic(text: str) -> str:
    """Return italic text."""
    return f"{ITALIC}{text}{RESET}" if COLOR else text


# ── Style builder ──────────────────────────────────────────────────────────────

class Style:
    """
    Composable ANSI text styler. Chains attributes and colors.

    Usage::

        s = Style().bold().underline().fg_256(208)
        print(s.paint("warning message"))

        # Inline:
        print(Style().strike().fg_truecolor(200, 80, 80).paint("deprecated"))
    """

    def __init__(self) -> None:
        self._codes: list[str] = []

    def _add(self, code: str) -> "Style":
        self._codes.append(code)
        return self

    # ── Text attributes ───────────────────────────────────────────────────────

    def bold(self) -> "Style":       return self._add(BOLD or "\033[1m")
    def dim(self) -> "Style":        return self._add(DIM or "\033[2m")
    def italic(self) -> "Style":     return self._add(ITALIC or "\033[3m")
    def underline(self) -> "Style":  return self._add(UNDERLINE or "\033[4m")
    def blink(self) -> "Style":      return self._add(BLINK or "\033[5m")
    def reverse(self) -> "Style":    return self._add(REVERSE or "\033[7m")
    def strike(self) -> "Style":     return self._add(STRIKE or "\033[9m")
    def overline(self) -> "Style":   return self._add(OVERLINE or "\033[53m")

    # ── Foreground colors ─────────────────────────────────────────────────────

    def fg(self, ansi_code: str) -> "Style":
        """Apply a raw ANSI foreground code."""
        return self._add(ansi_code)

    def fg_256(self, n: int) -> "Style":
        """256-color foreground (0–255)."""
        return self._add(f"\033[38;5;{n}m")

    def fg_rgb(self, r: int, g: int, b: int) -> "Style":
        """Truecolor RGB foreground."""
        return self._add(f"\033[38;2;{r};{g};{b}m")

    # ── Background colors ─────────────────────────────────────────────────────

    def bg_256(self, n: int) -> "Style":
        """256-color background (0–255)."""
        return self._add(f"\033[48;5;{n}m")

    def bg_rgb(self, r: int, g: int, b: int) -> "Style":
        """Truecolor RGB background."""
        return self._add(f"\033[48;2;{r};{g};{b}m")

    # ── Output ────────────────────────────────────────────────────────────────

    def paint(self, text: str) -> str:
        """Wrap text in all accumulated ANSI codes."""
        if not COLOR or not self._codes:
            return text
        return "".join(self._codes) + text + RESET

    def println(self, text: str) -> None:
        """Print styled text followed by a newline."""
        print(self.paint(text))

    def printf(self, fmt_str: str, *args: object) -> None:
        """Print a styled formatted string."""
        print(self.paint(fmt_str % args), end="")