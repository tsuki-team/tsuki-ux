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
    SYM_DASH   = "–"
    SYM_DOT    = "·"
    SYM_CHECK  = "✓"
    SYM_CROSS  = "✗"
    SYM_PTR    = "❱"

    # Box-drawing
    BOX_TL = "╭"
    BOX_TR = "╮"
    BOX_BL = "╰"
    BOX_BR = "╯"
    BOX_H  = "─"
    BOX_V  = "│"

    # ── Spinner frame sets ────────────────────────────────────────────────────

    # Default braille (matches ui.go and build.py exactly)
    SPINNER_FRAMES = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]

    # Heavy braille dots
    SPINNER_FRAMES_DOTS = ["⣾", "⣽", "⣻", "⢿", "⡿", "⣟", "⣯", "⣷"]

    # Minimal ASCII
    SPINNER_FRAMES_LINE = ["-", "\\", "|", "/"]

    # Animated arrow bar
    SPINNER_FRAMES_ARROW = ["▹▹▹▹▹", "▸▹▹▹▹", "▹▸▹▹▹", "▹▹▸▹▹", "▹▹▹▸▹", "▹▹▹▹▸"]

    # Moon phases
    SPINNER_FRAMES_MOON = ["🌑", "🌒", "🌓", "🌔", "🌕", "🌖", "🌗", "🌘"]

    # Clock faces
    SPINNER_FRAMES_CLOCK = ["🕛", "🕐", "🕑", "🕒", "🕓", "🕔", "🕕", "🕖", "🕗", "🕘", "🕙", "🕚"]

    # Bouncing ball on a track
    SPINNER_FRAMES_BOUNCE = [
        "[●    ]", "[●    ]", "[ ●   ]", "[  ●  ]", "[   ● ]", "[    ●]",
        "[    ●]", "[   ● ]", "[  ●  ]", "[ ●   ]",
    ]

    # Growing / shrinking block pulse
    SPINNER_FRAMES_PULSE = ["▏", "▎", "▍", "▌", "▋", "▊", "▉", "█", "▉", "▊", "▋", "▌", "▍", "▎"]

    # Snake-like filling bar
    SPINNER_FRAMES_SNAKE = [
        "⣀⣀⣀⣀⣀", "⣄⣀⣀⣀⣀", "⣤⣀⣀⣀⣀", "⣦⣄⣀⣀⣀",
        "⣶⣤⣄⣀⣀", "⣷⣦⣤⣄⣀", "⣿⣶⣦⣤⣄", "⣿⣿⣶⣦⣤",
        "⣿⣿⣿⣶⣦", "⣿⣿⣿⣿⣶", "⣿⣿⣿⣿⣿", "⣿⣿⣿⣿⣶",
        "⣿⣿⣿⣶⣦", "⣿⣿⣶⣦⣤", "⣿⣶⣦⣤⣄", "⣶⣦⣤⣄⣀",
        "⣦⣤⣄⣀⣀", "⣤⣀⣀⣀⣀", "⣄⣀⣀⣀⣀",
    ]

    # Small pixel grid cycling
    SPINNER_FRAMES_PIXEL = [
        "⣿⣿", "⣷⣿", "⣯⣿", "⣟⣿", "⡿⣿", "⢿⣿",
        "⣻⣿", "⣽⣿", "⣾⣿", "⣿⣾", "⣿⣽", "⣿⣻",
    ]

    # Blinking block toggle
    SPINNER_FRAMES_TOGGLE = ["▪▫▫▫▫", "▫▪▫▫▫", "▫▫▪▫▫", "▫▫▫▪▫", "▫▫▫▫▪", "▫▫▫▪▫", "▫▫▪▫▫", "▫▪▫▫▫"]

    # Expanding / contracting progress bar
    SPINNER_FRAMES_GROW = [
        "▰▱▱▱▱▱▱▱", "▰▰▱▱▱▱▱▱", "▰▰▰▱▱▱▱▱", "▰▰▰▰▱▱▱▱",
        "▰▰▰▰▰▱▱▱", "▰▰▰▰▰▰▱▱", "▰▰▰▰▰▰▰▱", "▰▰▰▰▰▰▰▰",
        "▱▰▰▰▰▰▰▰", "▱▱▰▰▰▰▰▰", "▱▱▱▰▰▰▰▰", "▱▱▱▱▰▰▰▰",
        "▱▱▱▱▱▰▰▰", "▱▱▱▱▱▱▰▰", "▱▱▱▱▱▱▱▰",
    ]

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
    SYM_DASH   = "-"
    SYM_DOT    = "."
    SYM_CHECK  = "v"
    SYM_CROSS  = "x"
    SYM_PTR    = ">"

    BOX_TL = "+"
    BOX_TR = "+"
    BOX_BL = "+"
    BOX_BR = "+"
    BOX_H  = "-"
    BOX_V  = "|"

    SPINNER_FRAMES        = ["-", "\\", "|", "/"]
    SPINNER_FRAMES_DOTS   = [".", "o", "O", "o"]
    SPINNER_FRAMES_LINE   = ["-", "\\", "|", "/"]
    SPINNER_FRAMES_ARROW  = [">    ", " >   ", "  >  ", "   > ", "    >"]
    SPINNER_FRAMES_MOON   = ["-", "\\", "|", "/"]
    SPINNER_FRAMES_CLOCK  = ["-", "\\", "|", "/"]
    SPINNER_FRAMES_BOUNCE = ["[o    ]", "[ o   ]", "[  o  ]", "[   o ]", "[    o]", "[   o ]", "[  o  ]", "[ o   ]"]
    SPINNER_FRAMES_PULSE  = [".", "o", "O", "0", "O", "o"]
    SPINNER_FRAMES_SNAKE  = [".....", "o....", "oo...", "ooo..", "oooo.", "ooooo", ".oooo", "..ooo", "...oo", "....o"]
    SPINNER_FRAMES_PIXEL  = ["..", "o.", "oo", ".o"]
    SPINNER_FRAMES_TOGGLE = ["*----", "-*---", "--*--", "---*-", "----*", "---*-", "--*--", "-*---"]
    SPINNER_FRAMES_GROW   = ["=       ", "==      ", "===     ", "====    ", "=====   ", "======  ", "======= ", "========", " =======", "  ======", "   =====", "    ====", "     ===", "      ==", "       ="]