"""
tsuki_ux._box
~~~~~~~~~~~~~
Bordered panels, config tables and rich tracebacks.
Port of ui.go's Box(), PrintConfig() and Traceback().
"""

from __future__ import annotations
import sys
from dataclasses import dataclass, field
from typing import Any

from tsuki_ux._color import (
    BOLD, DIM, ITALIC, RESET,
    C_TITLE, C_KEY, C_VALUE, C_STRING, C_NUMBER, C_BOOL, C_NULL, C_COMMENT,
    C_TB_BORDER, C_TB_TITLE, C_TB_FILE, C_TB_LINE, C_TB_FUNC,
    C_TB_CODE, C_TB_HIGH, C_TB_LOCALS, C_TB_ERRTYPE, C_TB_ERRMSG,
    strip_ansi,
)
from tsuki_ux._symbols import BOX_TL, BOX_TR, BOX_BL, BOX_BR, BOX_H, BOX_V, SYM_PTR
from tsuki_ux._primitives import term_w


def _hline(n: int) -> str:
    return BOX_H * max(0, n)


# ── Generic box ────────────────────────────────────────────────────────────────

def box(
    content: str,
    title: str = "",
    title_color: str = "",
    out=None,
) -> None:
    """
    ╭── Title ──────────────────────────────────╮
    │  content line 1                           │
    │  content line 2                           │
    ╰───────────────────────────────────────────╯
    """
    out = out or sys.stderr
    w = term_w()
    inner = w - 2  # space for the two side borders

    # ── top border ────────────────────────────────────────────────────────────
    if title:
        title_str = f" {title} "
        dashes = inner - len(title_str) - 2
        left = dashes // 2
        right = dashes - left
        _p(out, f"{C_TB_BORDER}{BOX_TL}{_hline(left)}{RESET}")
        _p(out, f"{title_color or C_TITLE}{title_str}{RESET}", end="")
        _p(out, f"{C_TB_BORDER}{_hline(right)}{BOX_TR}{RESET}\n", end="")
    else:
        _p(out, f"{C_TB_BORDER}{BOX_TL}{_hline(inner)}{BOX_TR}{RESET}\n", end="")

    # ── content lines ─────────────────────────────────────────────────────────
    for line in content.split("\n"):
        visible = len(strip_ansi(line))
        pad = max(0, inner - visible - 1)  # -1 for leading space
        _p(out, f"{C_TB_BORDER}{BOX_V}{RESET} {line}{' ' * pad}{C_TB_BORDER}{BOX_V}{RESET}\n", end="")

    # ── bottom border ─────────────────────────────────────────────────────────
    _p(out, f"{C_TB_BORDER}{BOX_BL}{_hline(inner)}{BOX_BR}{RESET}\n", end="")


def _p(out, s: str, end: str = "") -> None:
    out.write(s + end)
    out.flush()


# ── Config table ───────────────────────────────────────────────────────────────

@dataclass
class ConfigEntry:
    key: str
    value: Any
    comment: str = ""


def _fmt_value(v: Any) -> str:
    if isinstance(v, str):
        return f'{C_STRING}"{v}"{RESET}'
    if isinstance(v, bool):
        return f"{C_BOOL}{v}{RESET}"
    if isinstance(v, (int, float)):
        return f"{C_NUMBER}{v}{RESET}"
    if v is None:
        return f"{C_NULL}null{RESET}"
    if isinstance(v, list):
        if not v:
            return f"{C_NULL}[]{RESET}"
        parts = ", ".join(_fmt_value(i) for i in v)
        return f"[{parts}]"
    return f"{C_VALUE}{v}{RESET}"


def config_table(title: str, entries: list[ConfigEntry], raw: bool = False, out=None) -> None:
    """
    ╭── title ─────────────────────────────────────────────────╮
    │  key        =  "value"      # optional comment           │
    ╰──────────────────────────────────────────────────────────╯
    """
    out = out or sys.stdout

    if raw:
        for e in entries:
            print(f"{e.key} = {e.value}", file=out)
        return

    key_w = max((len(e.key) for e in entries), default=0)

    lines_plain: list[str] = []
    lines_rich: list[str] = []
    for e in entries:
        key_str = f"{C_KEY}{e.key:<{key_w}}{RESET}"
        sep = f"{DIM}  =  {RESET}"
        val_str = _fmt_value(e.value)
        rich = key_str + sep + val_str
        plain = f"{e.key:<{key_w}}  =  {e.value}"
        if e.comment:
            c = f"  # {e.comment}"
            rich += f"{C_COMMENT}{c}{RESET}"
            plain += c
        lines_rich.append(rich)
        lines_plain.append(plain)

    w = term_w()
    inner = w - 2
    min_inner = max(len(title) + 6, *(len(p) + 2 for p in lines_plain))
    if min_inner > inner:
        inner = min_inner

    # header
    title_str = f" {title} "
    pad_right = max(0, inner - len(title_str) - 2)
    out.write(f"{C_TB_BORDER}{BOX_TL}{BOX_H}{BOX_H}{RESET}{C_TITLE}{title_str}{RESET}{C_TB_BORDER}{_hline(pad_right)}{BOX_TR}{RESET}\n")

    for rich, plain in zip(lines_rich, lines_plain):
        pad = max(0, inner - len(plain) - 1)
        out.write(f"{C_TB_BORDER}{BOX_V}{RESET} {rich}{' ' * pad}{C_TB_BORDER}{BOX_V}{RESET}\n")

    out.write(f"{C_TB_BORDER}{BOX_BL}{_hline(inner)}{BOX_BR}{RESET}\n")
    out.flush()


# ── Rich traceback ─────────────────────────────────────────────────────────────

@dataclass
class CodeLine:
    number: int
    text: str
    is_pointer: bool = False   # the line that caused the error (❱)


@dataclass
class Frame:
    file: str
    line: int
    func: str
    code: list[CodeLine] = field(default_factory=list)
    locals: dict[str, str] = field(default_factory=dict)


def traceback_box(err_type: str, err_msg: str, frames: list[Frame], out=None) -> None:
    """
    ╭─── Traceback (most recent call last) ──────────────────────╮
    │  • main.go:21 in divide_all                                │
    │                                                            │
    │   19 │ try:                                               │
    │ ❱ 21 │   result = divide_by(n, d)                         │
    │   22 │   print(result)                                     │
    │                                                            │
    │  locals ──────────────────────────────────────────────    │
    │  │  divisor = 0                                            │
    ╰────────────────────────────────────────────────────────────╯
    ZeroDivisionError: division by zero
    """
    out = out or sys.stderr
    w = term_w()
    inner = w - 2

    def emit(text: str = "") -> None:
        visible = len(strip_ansi(text))
        pad = max(0, inner - visible - 1)
        out.write(f"{C_TB_BORDER}{BOX_V}{RESET} {text}{' ' * pad}{C_TB_BORDER}{BOX_V}{RESET}\n")

    def empty() -> None:
        out.write(f"{C_TB_BORDER}{BOX_V}{RESET}{' ' * inner}{C_TB_BORDER}{BOX_V}{RESET}\n")

    # header
    hdr = " Traceback (most recent call last) "
    right = max(0, inner - len(hdr) - 3)
    out.write(f"{C_TB_BORDER}{BOX_TL}{BOX_H * 3}{RESET}{C_TB_TITLE}{hdr}{RESET}{C_TB_BORDER}{_hline(right)}{BOX_TR}{RESET}\n")

    for frame in frames:
        loc = f"{C_TB_FILE}{frame.file}{RESET}:{C_TB_LINE}{frame.line}{RESET} in {C_TB_FUNC}{frame.func}{RESET}"
        emit(loc)
        empty()

        for cl in frame.code:
            num = f"{cl.number:4d}"
            sep = f"{C_TB_BORDER} {BOX_V} {RESET}"
            if cl.is_pointer:
                emit(f"{C_TB_HIGH} {SYM_PTR} {num}{RESET}{sep}{C_TB_HIGH}{cl.text}{RESET}")
            else:
                emit(f"   {DIM}{num}{RESET}{sep}{C_TB_CODE}{cl.text}{RESET}")

        if frame.locals:
            empty()
            loc_title = f"{C_TB_LOCALS} locals {RESET}{C_TB_BORDER}{_hline(inner - 12)}{RESET}"
            emit(loc_title)
            for k, v in frame.locals.items():
                emit(f"{C_TB_BORDER}{BOX_V}  {RESET}{C_KEY}{k}{RESET} = {C_VALUE}{v}{RESET}")

        empty()

    out.write(f"{C_TB_BORDER}{BOX_BL}{_hline(inner)}{BOX_BR}{RESET}\n")
    out.write(f"{C_TB_ERRTYPE}{err_type}{RESET}: {C_TB_ERRMSG}{err_msg}{RESET}\n")
    out.flush()
