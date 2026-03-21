"""
tsuki_ux — Terminal UX library extracted from the Tsuki project.

Faithful port of cli/internal/ui/ui.go and tools/build.py to Python.

Usage:
    from tsuki_ux import success, fail, warn, info, step, note
    from tsuki_ux import LiveBlock, Spinner, box, section, run
"""

from tsuki_ux._color import (
    BOLD, DIM, RESET, ERASE,
    GREEN, CYAN, YELLOW, RED, BLUE, MAGENTA,
    C_SUCCESS, C_WARN, C_ERROR, C_INFO, C_STEP, C_DIM,
    COLOR, strip_ansi,
)
from tsuki_ux._symbols import (
    SYM_OK, SYM_FAIL, SYM_WARN, SYM_INFO, SYM_STEP,
    SYM_BULLET, SYM_PIPE, SYM_ELL,
    BOX_TL, BOX_TR, BOX_BL, BOX_BR, BOX_H, BOX_V,
    SPINNER_FRAMES,
)
from tsuki_ux._primitives import (
    success, fail, warn, info, step, note,
    artifact, header, section, section_end,
    progress_bar, term_w,
)
from tsuki_ux._box import box, config_table, ConfigEntry, traceback_box, Frame, CodeLine
from tsuki_ux._spinner import Spinner
from tsuki_ux._live import LiveBlock
from tsuki_ux._run import run

__all__ = [
    # color tokens
    "BOLD", "DIM", "RESET", "ERASE",
    "GREEN", "CYAN", "YELLOW", "RED", "BLUE", "MAGENTA",
    "C_SUCCESS", "C_WARN", "C_ERROR", "C_INFO", "C_STEP", "C_DIM",
    "COLOR", "strip_ansi",
    # symbols
    "SYM_OK", "SYM_FAIL", "SYM_WARN", "SYM_INFO", "SYM_STEP",
    "SYM_BULLET", "SYM_PIPE", "SYM_ELL",
    "BOX_TL", "BOX_TR", "BOX_BL", "BOX_BR", "BOX_H", "BOX_V",
    "SPINNER_FRAMES",
    # primitives
    "success", "fail", "warn", "info", "step", "note",
    "artifact", "header", "section", "section_end",
    "progress_bar", "term_w",
    # box / panel
    "box", "config_table", "ConfigEntry",
    "traceback_box", "Frame", "CodeLine",
    # spinner
    "Spinner",
    # live block
    "LiveBlock",
    # run helper
    "run",
]
