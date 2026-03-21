"""
tsuki_ux._symbols
~~~~~~~~~~~~~~~~~
Adaptive symbols: Unicode box-drawing + braille on modern terminals,
plain ASCII fallback for legacy Windows consoles.
Mirrors the _supports_unicode() logic from build.py.
"""

from __future__ import annotations
import sys


def _supports_unicode() -> bool:
    enc = getattr(sys.stdout, "encoding", "") or ""
    if enc.lower().replace("-", "") in ("utf8", "utf16", "utf32"):
        return True
    if sys.platform == "win32":
        try:
            import ctypes
            cp = ctypes.windll.kernel32.GetConsoleOutputCP()  # type: ignore[attr-defined]
            return cp == 65001  # UTF-8 code page
        except Exception:
            return False
    return True  # Linux / macOS always UTF-8


UNICODE: bool = _supports_unicode()

if UNICODE:
    # Status symbols
    SYM_OK     = "✔"
    SYM_FAIL   = "✖"
    SYM_WARN   = "⚠"
    SYM_INFO   = "●"
    SYM_STEP   = "▶"
    SYM_BULLET = "•"
    SYM_PIPE   = "│"
    SYM_ELL    = "…"
    SYM_ARROW  = "→"

    # Box-drawing
    BOX_TL = "╭"
    BOX_TR = "╮"
    BOX_BL = "╰"
    BOX_BR = "╯"
    BOX_H  = "─"
    BOX_V  = "│"

    # Traceback pointer
    SYM_PTR = "❱"

    # Braille spinner frames (matches ui.go and build.py exactly)
    SPINNER_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

else:
    # Pure ASCII fallback
    SYM_OK     = "+"
    SYM_FAIL   = "x"
    SYM_WARN   = "!"
    SYM_INFO   = "*"
    SYM_STEP   = ">"
    SYM_BULLET = "-"
    SYM_PIPE   = "|"
    SYM_ELL    = "..."
    SYM_ARROW  = "->"

    BOX_TL = "+"
    BOX_TR = "+"
    BOX_BL = "+"
    BOX_BR = "+"
    BOX_H  = "-"
    BOX_V  = "|"

    SYM_PTR = ">"

    SPINNER_FRAMES = ["-", "\\", "|", "/"]
