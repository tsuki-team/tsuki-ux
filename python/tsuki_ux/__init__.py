"""
tsuki_ux — Terminal UX library extracted from the Tsuki project.
"""

from tsuki_ux._color import (
    BOLD, DIM, ITALIC, UNDERLINE, BLINK, REVERSE, STRIKE, OVERLINE,
    RESET, ERASE,
    GREEN, CYAN, YELLOW, RED, BLUE, MAGENTA, WHITE,
    HI_GREEN, HI_CYAN, HI_YELLOW, HI_RED, HI_BLUE, HI_MAGENTA, HI_WHITE,
    C_SUCCESS, C_WARN, C_ERROR, C_INFO, C_STEP, C_DIM,
    C_HIGHLIGHT, C_ACCENT, C_MUTED,
    COLOR, strip_ansi,
    # Style helpers
    color256, bg_color256, truecolor, bg_truecolor,
    underline, strike, overline, blink, reverse, bold, dim, italic,
    Style,
)
from tsuki_ux._symbols import (
    SYM_OK, SYM_FAIL, SYM_WARN, SYM_INFO, SYM_STEP,
    SYM_BULLET, SYM_PIPE, SYM_ELL, SYM_ARROW, SYM_DASH,
    SYM_DOT, SYM_CHECK, SYM_CROSS, SYM_PTR,
    BOX_TL, BOX_TR, BOX_BL, BOX_BR, BOX_H, BOX_V,
    # Spinner frame sets
    SPINNER_FRAMES,
    SPINNER_FRAMES_DOTS,
    SPINNER_FRAMES_LINE,
    SPINNER_FRAMES_ARROW,
    SPINNER_FRAMES_MOON,
    SPINNER_FRAMES_CLOCK,
    SPINNER_FRAMES_BOUNCE,
    SPINNER_FRAMES_PULSE,
    SPINNER_FRAMES_SNAKE,
    SPINNER_FRAMES_PIXEL,
    SPINNER_FRAMES_TOGGLE,
    SPINNER_FRAMES_GROW,
)
from tsuki_ux._primitives import (
    term_w,
    # Status
    success, successf, fail, failf, warn, warnf, info, infof,
    step, stepf, note, notef, artifact,
    # Header / section
    header, section, section_end,
    # Layout
    rule, separator, blank,
    # Inline content
    badge, badge_line, key_value, key_valuef,
    list_items, numbered_list, check_list,
    indent, highlight, accent,
    # Timer
    Timer,
    # Progress bars
    progress_bar, progress_bar_thin, progress_bar_braille,
    progress_bar_dots, progress_bar_slim, progress_bar_gradient,
    progress_bar_arrow, progress_bar_steps, progress_bar_squares,
)
from tsuki_ux._box import box, config_table, ConfigEntry, traceback_box, Frame, CodeLine
from tsuki_ux._spinner import Spinner
from tsuki_ux._live import LiveBlock
from tsuki_ux._run import run

__all__ = [
    # color attributes
    "BOLD", "DIM", "ITALIC", "UNDERLINE", "BLINK", "REVERSE", "STRIKE", "OVERLINE",
    "RESET", "ERASE",
    # raw colors
    "GREEN", "CYAN", "YELLOW", "RED", "BLUE", "MAGENTA", "WHITE",
    "HI_GREEN", "HI_CYAN", "HI_YELLOW", "HI_RED", "HI_BLUE", "HI_MAGENTA", "HI_WHITE",
    # semantic colors
    "C_SUCCESS", "C_WARN", "C_ERROR", "C_INFO", "C_STEP", "C_DIM",
    "C_HIGHLIGHT", "C_ACCENT", "C_MUTED",
    "COLOR", "strip_ansi",
    # style helpers
    "color256", "bg_color256", "truecolor", "bg_truecolor",
    "underline", "strike", "overline", "blink", "reverse", "bold", "dim", "italic",
    "Style",
    # symbols
    "SYM_OK", "SYM_FAIL", "SYM_WARN", "SYM_INFO", "SYM_STEP",
    "SYM_BULLET", "SYM_PIPE", "SYM_ELL", "SYM_ARROW", "SYM_DASH",
    "SYM_DOT", "SYM_CHECK", "SYM_CROSS", "SYM_PTR",
    "BOX_TL", "BOX_TR", "BOX_BL", "BOX_BR", "BOX_H", "BOX_V",
    # spinner frames
    "SPINNER_FRAMES", "SPINNER_FRAMES_DOTS", "SPINNER_FRAMES_LINE",
    "SPINNER_FRAMES_ARROW", "SPINNER_FRAMES_MOON", "SPINNER_FRAMES_CLOCK",
    "SPINNER_FRAMES_BOUNCE", "SPINNER_FRAMES_PULSE", "SPINNER_FRAMES_SNAKE",
    "SPINNER_FRAMES_PIXEL", "SPINNER_FRAMES_TOGGLE", "SPINNER_FRAMES_GROW",
    # primitives
    "term_w",
    "success", "successf", "fail", "failf", "warn", "warnf", "info", "infof",
    "step", "stepf", "note", "notef", "artifact",
    "header", "section", "section_end",
    "rule", "separator", "blank",
    "badge", "badge_line", "key_value", "key_valuef",
    "list_items", "numbered_list", "check_list",
    "indent", "highlight", "accent",
    "Timer",
    "progress_bar", "progress_bar_thin", "progress_bar_braille",
    "progress_bar_dots", "progress_bar_slim", "progress_bar_gradient",
    "progress_bar_arrow", "progress_bar_steps", "progress_bar_squares",
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