"""
tsuki_ux._primitives
~~~~~~~~~~~~~~~~~~~~
Core output functions. Faithful port of tsukiux.go (Go).

Now includes everything from the Go implementation:
  rule, separator, blank, badge, badge_line, key_value, list,
  numbered_list, check_list, indent, highlight, accent, timer,
  and all progress bar variants.
"""

from __future__ import annotations
import math
import shutil
import sys
import time
from typing import Any, List, Optional, Sequence

from tsuki_ux._color import (
    BOLD, DIM, ITALIC, RESET, UNDERLINE, STRIKE, OVERLINE, BLINK, REVERSE,
    C_SUCCESS, C_WARN, C_ERROR, C_INFO, C_STEP, C_DIM,
    C_TITLE, C_KEY, C_VALUE, C_MUTED, C_HIGHLIGHT, C_ACCENT,
    strip_ansi, COLOR,
)
from tsuki_ux._symbols import (
    SYM_OK, SYM_FAIL, SYM_WARN, SYM_INFO, SYM_STEP,
    SYM_BULLET, SYM_PIPE, SYM_ARROW, SYM_DASH, SYM_CHECK, SYM_CROSS,
    BOX_TL, BOX_TR, BOX_BL, BOX_BR, BOX_H, BOX_V,
)


def term_w() -> int:
    """Current terminal width, defaulting to 100."""
    return shutil.get_terminal_size((100, 24)).columns


def _hline(n: int) -> str:
    return BOX_H * max(0, n)


# ── Status primitives ──────────────────────────────────────────────────────────

def success(msg: str) -> None:
    """  ✔  msg  (green)"""
    print(f"  {C_SUCCESS}{SYM_OK}{RESET}  {msg}")


def successf(fmt_str: str, *args: object) -> None:
    success(fmt_str % args)


def fail(msg: str, file=None) -> None:
    """  ✖  msg  (red, stderr by default)"""
    out = file or sys.stderr
    print(f"  {C_ERROR}{SYM_FAIL}{RESET}  {msg}", file=out)


def failf(fmt_str: str, *args: object) -> None:
    fail(fmt_str % args)


def warn(msg: str) -> None:
    """  ⚠  msg  (yellow)"""
    print(f"  {C_WARN}{SYM_WARN}{RESET}  {msg}")


def warnf(fmt_str: str, *args: object) -> None:
    warn(fmt_str % args)


def info(msg: str) -> None:
    """  ●  msg  (cyan)"""
    print(f"  {C_INFO}{SYM_INFO}{RESET}  {msg}")


def infof(fmt_str: str, *args: object) -> None:
    info(fmt_str % args)


def step(msg: str) -> None:
    """  ▶  msg  — main step header, preceded by blank line."""
    print(f"\n  {C_STEP}{SYM_STEP}{RESET}  {BOLD}{msg}{RESET}")


def stepf(fmt_str: str, *args: object) -> None:
    step(fmt_str % args)


def note(msg: str) -> None:
    """    ●  msg  — low-contrast auxiliary note."""
    print(f"  {DIM}{SYM_INFO}  {msg}{RESET}")


def notef(fmt_str: str, *args: object) -> None:
    note(fmt_str % args)


def artifact(name: str, size: str = "") -> None:
    """     •  name  (size)"""
    size_part = f"  {DIM}({size}){RESET}" if size else ""
    print(f"   {C_STEP}{SYM_BULLET}{RESET}  {name}{size_part}")


# ── Header / Section ───────────────────────────────────────────────────────────

def header(title: str) -> None:
    w = term_w()
    h = w - 2
    hbar = _hline(h)
    print(f"\n{DIM}{BOX_TL}{hbar}{BOX_TR}{RESET}")
    content = f"  🌙 {title}"
    pad = max(0, h - len(strip_ansi(content)) - 1)
    print(f"{DIM}{BOX_V}{RESET}{C_TITLE}{content}{RESET}{' ' * pad}{DIM}{BOX_V}{RESET}")
    print(f"{DIM}{BOX_BL}{hbar}{BOX_BR}{RESET}")


def section(title: str) -> None:
    w = min(term_w(), 72)
    inner = f" {title} "
    pad = max(0, w - len(inner) - 4)
    print(f"\n{DIM}{BOX_TL}{BOX_H}{RESET}{C_TITLE}{inner}{RESET}{DIM}{_hline(pad)}{BOX_TR}{RESET}")


def section_end() -> None:
    w = min(term_w(), 72)
    print(f"{DIM}{BOX_BL}{_hline(w - 2)}{BOX_BR}{RESET}")


# ── Layout helpers ─────────────────────────────────────────────────────────────

def rule(label: str = "") -> None:
    """Print a full-width horizontal rule with an optional centered label."""
    w = term_w()
    if not label:
        print(f"{DIM}{_hline(w)}{RESET}")
        return
    inner = f" {label} "
    sides = w - len(inner)
    left = sides // 2
    right = sides - left
    print(f"{DIM}{_hline(max(0, left))}{RESET}{C_MUTED}{inner}{RESET}{DIM}{_hline(max(0, right))}{RESET}")


def separator() -> None:
    """Blank line, dim rule, blank line."""
    print()
    rule()
    print()


def blank() -> None:
    """Print an empty line."""
    print()


# ── Inline content helpers ─────────────────────────────────────────────────────

def badge(label: str, style: str = "info") -> str:
    """Return a color-coded inline tag string: [ label ]
    style: 'success' | 'error' | 'warn' | 'info' | 'muted' | 'highlight' | 'accent'
    """
    codes = {
        "success":   C_SUCCESS,
        "error":     C_ERROR,
        "warn":      C_WARN,
        "muted":     C_MUTED,
        "highlight": C_HIGHLIGHT,
        "accent":    C_ACCENT,
    }
    code = codes.get(style, C_INFO)
    return f"{code}[ {label} ]{RESET}"


def badge_line(label: str, style: str, msg: str) -> None:
    """Print a badge followed by a message on the same line."""
    print(f"  {badge(label, style)}  {msg}")


def key_value(key: str, value: Any) -> None:
    """Print a single aligned key → value line."""
    print(f"  {C_KEY}{key}{RESET}  {C_MUTED}{SYM_ARROW}{RESET}  {C_VALUE}{value}{RESET}")


def key_valuef(key: str, fmt_str: str, *args: object) -> None:
    key_value(key, fmt_str % args)


def list_items(items: Sequence[str]) -> None:
    """Print a bulleted list."""
    for item in items:
        print(f"  {C_MUTED}{SYM_BULLET}{RESET}  {item}")


def numbered_list(items: Sequence[str]) -> None:
    """Print a numbered list."""
    for i, item in enumerate(items, 1):
        print(f"  {C_MUTED}{i}.{RESET}  {item}")


def check_list(items: Sequence[str], checked: Sequence[bool]) -> None:
    """Print a list where each item can be checked or unchecked."""
    for i, item in enumerate(items):
        sym = f"{C_SUCCESS}{SYM_CHECK}{RESET}" if i < len(checked) and checked[i] else f"{C_MUTED}{SYM_CROSS}{RESET}"
        print(f"  {sym}  {item}")


def indent(text: str) -> None:
    """Print each line with a left pipe indent."""
    for line in text.split("\n"):
        print(f"  {C_MUTED}{SYM_PIPE}{RESET}  {DIM}{line}{RESET}")


def highlight(msg: str) -> None:
    """Print msg with high-visibility magenta emphasis."""
    print(f"  {C_HIGHLIGHT}{msg}{RESET}")


def accent(msg: str) -> None:
    """Print msg in bold cyan — secondary emphasis."""
    print(f"  {C_ACCENT}{msg}{RESET}")


# ── Timer ──────────────────────────────────────────────────────────────────────

class Timer:
    """Wall-clock timer to embed in step output.

    Usage::

        t = Timer()
        # ... do work ...
        success(f"done  {t.elapsed_dim()}")
    """

    def __init__(self) -> None:
        self._start = time.monotonic()

    def _fmt(self) -> str:
        s = time.monotonic() - self._start
        if s < 1.0:
            return f"{int(s * 1000)}ms"
        return f"{s:.1f}s"

    def elapsed(self) -> str:
        """Human-readable elapsed time string."""
        return self._fmt()

    def elapsed_dim(self) -> str:
        """Elapsed time formatted as a dim string ready to embed in output."""
        return f"{DIM}[{self._fmt()}]{RESET}"


# ── Progress bar variants ──────────────────────────────────────────────────────

def progress_bar(label: str, done: int, total: int, width: int = 40) -> None:
    """Classic block bar:  label  [████████░░░░]  75%"""
    pct = done / total if total else 0.0
    filled = round(width * pct)
    bar = (f"{C_SUCCESS}{'█' * filled}{RESET}"
           + f"{DIM}{'░' * (width - filled)}{RESET}")
    print(f"  {label}  [{bar}]  {int(pct * 100)}%")


def progress_bar_thin(label: str, done: int, total: int, width: int = 40) -> None:
    """Slim line bar:  label  ──────────────╴          40%"""
    pct = done / total if total else 0.0
    filled = round(width * pct)
    tip = "╴" if 0 < filled < width else ""
    bar = (f"{C_SUCCESS}{'─' * max(0, filled - len(tip))}{tip}{RESET}"
           + f"{C_MUTED}{' ' * max(0, width - filled)}{RESET}")
    print(f"  {label}  {bar}  {int(pct * 100)}%")


def progress_bar_braille(label: str, done: int, total: int, width: int = 20) -> None:
    """High-resolution braille bar:  label  ⣿⣿⣿⣿⣦⣀⣀  60%"""
    pct = done / total if total else 0.0
    eighths = round(width * 8 * pct)
    full, rem = divmod(eighths, 8)
    blocks = ["⣀", "⣄", "⣤", "⣦", "⣶", "⣷", "⣿"]
    bar = ""
    for i in range(width):
        if i < full:
            bar += f"{C_SUCCESS}⣿{RESET}"
        elif i == full and rem > 0:
            bar += f"{C_INFO}{blocks[rem - 1]}{RESET}"
        else:
            bar += f"{C_MUTED}⣀{RESET}"
    print(f"  {label}  {bar}  {int(pct * 100)}%")


def progress_bar_dots(label: str, done: int, total: int, width: int = 30) -> None:
    """Dot bar:  label  ●●●●●●●●○○○○  67%"""
    pct = done / total if total else 0.0
    filled = round(width * pct)
    bar = (f"{C_SUCCESS}{'●' * filled}{RESET}"
           + f"{C_MUTED}{'○' * (width - filled)}{RESET}")
    print(f"  {label}  {bar}  {int(pct * 100)}%")


def progress_bar_slim(label: str, done: int, total: int, width: int = 30) -> None:
    """Slim filled/empty block bar:  label  ▰▰▰▰▰▰▱▱▱▱  60%"""
    pct = done / total if total else 0.0
    filled = round(width * pct)
    bar = (f"{C_SUCCESS}{'▰' * filled}{RESET}"
           + f"{C_MUTED}{'▱' * (width - filled)}{RESET}")
    print(f"  {label}  {bar}  {int(pct * 100)}%")


def progress_bar_gradient(label: str, done: int, total: int, width: int = 40) -> None:
    """Gradient shaded bar:  label  [████▓▒░      ]  45%"""
    pct = done / total if total else 0.0
    units = round(width * 4 * pct)
    full, rem = divmod(units, 4)
    shades = [" ", "░", "▒", "▓"]
    bar = ""
    for i in range(width):
        if i < full:
            bar += f"{C_SUCCESS}█{RESET}"
        elif i == full:
            bar += f"{C_INFO}{shades[rem]}{RESET}"
        else:
            bar += f"{C_MUTED} {RESET}"
    print(f"  {label}  [{bar}]  {int(pct * 100)}%")


def progress_bar_arrow(label: str, done: int, total: int, width: int = 40) -> None:
    """Classic arrow bar:  label  [=======>    ]  56%"""
    pct = done / total if total else 0.0
    filled = round(width * pct)
    if filled == 0:
        body = f"{C_MUTED}{'-' * width}{RESET}"
    elif filled >= width:
        body = f"{C_SUCCESS}{'=' * width}{RESET}"
    else:
        body = (f"{C_SUCCESS}{'=' * (filled - 1)}>{RESET}"
                + f"{C_MUTED}{'-' * (width - filled)}{RESET}")
    print(f"  {label}  [{body}]  {int(pct * 100)}%")


def progress_bar_steps(label: str, done: int, total: int) -> None:
    """Step counter with fraction:  label  [■■■□□□□□]  3/8"""
    done = min(done, total)
    bar = (f"{C_SUCCESS}{'■' * done}{RESET}"
           + f"{C_MUTED}{'□' * (total - done)}{RESET}")
    print(f"  {label}  [{bar}]  {done}/{total}")


def progress_bar_squares(label: str, done: int, total: int, width: int = 30) -> None:
    """Segmented square bar:  label  ▪▪▪▪▪▫▫▫▫▫  50%"""
    pct = done / total if total else 0.0
    filled = round(width * pct)
    bar = (f"{C_SUCCESS}{'▪' * filled}{RESET}"
           + f"{C_MUTED}{'▫' * (width - filled)}{RESET}")
    print(f"  {label}  {bar}  {int(pct * 100)}%")