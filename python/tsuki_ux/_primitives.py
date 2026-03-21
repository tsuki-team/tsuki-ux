"""
tsuki_ux._primitives
~~~~~~~~~~~~~~~~~~~~
Core output functions: success, fail, warn, info, step, note, section, header.
Faithful port of build.py's info/warn/error/step/section/artifact functions
and ui.go's Success/Fail/Info/Warn/Step/Header/SectionTitle.
"""

from __future__ import annotations
import math
import shutil
import sys

from tsuki_ux._color import (
    BOLD, DIM, RESET,
    C_SUCCESS, C_WARN, C_ERROR, C_INFO, C_STEP, C_DIM,
    C_TITLE, strip_ansi,
)
from tsuki_ux._symbols import (
    SYM_OK, SYM_FAIL, SYM_WARN, SYM_INFO, SYM_STEP,
    SYM_BULLET, BOX_TL, BOX_TR, BOX_BL, BOX_BR, BOX_H,
)


def term_w() -> int:
    """Current terminal width, defaulting to 100."""
    return shutil.get_terminal_size((100, 24)).columns


# ── Status primitives ──────────────────────────────────────────────────────────

def success(msg: str) -> None:
    """  ✔  msg  (green)"""
    print(f"  {C_SUCCESS}{SYM_OK}{RESET}  {msg}")


def fail(msg: str, file=None) -> None:
    """  ✖  msg  (red, stderr by default)"""
    out = file or sys.stderr
    print(f"  {C_ERROR}{SYM_FAIL}{RESET}  {msg}", file=out)


def warn(msg: str) -> None:
    """  ⚠  msg  (yellow)"""
    print(f"  {C_WARN}{SYM_WARN}{RESET}  {msg}")


def info(msg: str) -> None:
    """  ●  msg  (cyan)"""
    print(f"  {C_INFO}{SYM_INFO}{RESET}  {msg}")


def step(msg: str) -> None:
    """  ▶  msg  — main step header, preceded by a blank line."""
    print(f"\n{C_STEP}{SYM_STEP}{RESET}  {BOLD}{msg}{RESET}")


def note(msg: str) -> None:
    """    ●  msg  — low-contrast auxiliary note."""
    print(f"  {DIM}{SYM_INFO}  {msg}{RESET}")


# ── Artifact entry ─────────────────────────────────────────────────────────────

def artifact(name: str, size: str = "") -> None:
    """     •  name  (size)"""
    size_part = f"  {DIM}({size}){RESET}" if size else ""
    print(f"   {C_STEP}{SYM_BULLET}{RESET}  {name}{size_part}")


# ── Header (full-width rounded box) ───────────────────────────────────────────

def header(title: str) -> None:
    """
    ╭──────────────────────────────────────────────────────────╮
    │  🌙 tsuki — build completo                               │
    ╰──────────────────────────────────────────────────────────╯
    """
    w = term_w()
    h = w - 2
    hbar = BOX_H * h
    print(f"\n{DIM}{BOX_TL}{hbar}{BOX_TR}{RESET}")
    content = f"  🌙 {title}"
    pad = h - len(strip_ansi(content)) - 1
    pad = max(0, pad)
    print(f"{DIM}{BOX_TL[0] if False else '│'}{RESET}{C_TITLE}{content}{RESET}{' ' * pad}{DIM}│{RESET}")
    print(f"{DIM}{BOX_BL}{hbar}{BOX_BR}{RESET}")


# ── Section (platform block) ───────────────────────────────────────────────────

def section(title: str) -> None:
    """
    ╭─ Platform: linux-amd64 ────────────────────────────────╮
    """
    w = min(term_w(), 72)
    inner = f" {title} "
    pad = max(0, w - len(inner) - 4)  # 4 = len("╭─" + "╮")
    line = BOX_H * pad
    print(f"\n{DIM}{BOX_TL}{BOX_H}{RESET}{BOLD}{inner}{RESET}{DIM}{line}{BOX_TR}{RESET}")


def section_end() -> None:
    """╰────────────────────────────────────────────────────────╯"""
    w = min(term_w(), 72)
    print(f"{DIM}{BOX_BL}{BOX_H * (w - 2)}{BOX_BR}{RESET}")


# ── Progress bar ───────────────────────────────────────────────────────────────

def progress_bar(label: str, done: int, total: int, width: int = 40) -> None:
    """  label  [████████░░░░]  75%"""
    pct = done / total if total else 0.0
    filled = int(round(width * pct))
    bar = (
        f"{C_SUCCESS}{'█' * filled}{RESET}"
        + f"{DIM}{'░' * (width - filled)}{RESET}"
    )
    print(f"  {label}  [{bar}]  {int(pct * 100)}%")
