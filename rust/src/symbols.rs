//! Adaptive symbols: Unicode on modern terminals, ASCII fallback elsewhere.
//! Mirrors `_supports_unicode()` from build.py.

use std::sync::OnceLock;

static UNICODE: OnceLock<bool> = OnceLock::new();

fn supports_unicode() -> bool {
    #[cfg(windows)]
    {
        #[link(name = "kernel32")]
        extern "system" {
            fn GetConsoleOutputCP() -> u32;
        }
        unsafe { GetConsoleOutputCP() == 65001 }
    }
    #[cfg(not(windows))]
    {
        for var in &["LC_ALL", "LC_CTYPE", "LANG"] {
            if let Ok(v) = std::env::var(var) {
                let v = v.to_lowercase();
                if v.contains("utf-8") || v.contains("utf8") {
                    return true;
                }
            }
        }
        true
    }
}

/// Returns true when the terminal can render Unicode box-drawing and braille.
pub fn unicode_enabled() -> bool {
    *UNICODE.get_or_init(supports_unicode)
}

// ── Symbol constants ──────────────────────────────────────────────────────────

pub fn sym_ok()     -> &'static str { if unicode_enabled() { "✔" } else { "+" } }
pub fn sym_fail()   -> &'static str { if unicode_enabled() { "✖" } else { "x" } }
pub fn sym_warn()   -> &'static str { if unicode_enabled() { "⚠" } else { "!" } }
pub fn sym_info()   -> &'static str { if unicode_enabled() { "●" } else { "*" } }
pub fn sym_step()   -> &'static str { if unicode_enabled() { "▶" } else { ">" } }
pub fn sym_bullet() -> &'static str { if unicode_enabled() { "•" } else { "-" } }
pub fn sym_pipe()   -> &'static str { if unicode_enabled() { "│" } else { "|" } }
pub fn sym_ell()    -> &'static str { if unicode_enabled() { "…" } else { "..." } }
pub fn sym_ptr()    -> &'static str { if unicode_enabled() { "❱" } else { ">" } }
pub fn sym_arrow()  -> &'static str { if unicode_enabled() { "→" } else { "->" } }
pub fn sym_check()  -> &'static str { if unicode_enabled() { "✓" } else { "v" } }
pub fn sym_cross()  -> &'static str { if unicode_enabled() { "✗" } else { "x" } }

pub fn box_tl() -> &'static str { if unicode_enabled() { "╭" } else { "+" } }
pub fn box_tr() -> &'static str { if unicode_enabled() { "╮" } else { "+" } }
pub fn box_bl() -> &'static str { if unicode_enabled() { "╰" } else { "+" } }
pub fn box_br() -> &'static str { if unicode_enabled() { "╯" } else { "+" } }
pub fn box_h()  -> &'static str { if unicode_enabled() { "─" } else { "-" } }
pub fn box_v()  -> &'static str { if unicode_enabled() { "│" } else { "|" } }

// ── Spinner frame sets ────────────────────────────────────────────────────────

/// Default braille spinner — matches ui.go and build.py exactly.
pub fn spinner_frames() -> &'static [&'static str] {
    if unicode_enabled() {
        &["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    } else {
        &["-", "\\", "|", "/"]
    }
}

/// Heavy braille dots.
pub fn spinner_frames_dots() -> &'static [&'static str] {
    if unicode_enabled() {
        &["⣾", "⣽", "⣻", "⢿", "⡿", "⣟", "⣯", "⣷"]
    } else {
        &[".", "o", "O", "o"]
    }
}

/// Minimal ASCII line spinner.
pub fn spinner_frames_line() -> &'static [&'static str] {
    &["-", "\\", "|", "/"]
}

/// Animated arrow bar.
pub fn spinner_frames_arrow() -> &'static [&'static str] {
    if unicode_enabled() {
        &["▹▹▹▹▹", "▸▹▹▹▹", "▹▸▹▹▹", "▹▹▸▹▹", "▹▹▹▸▹", "▹▹▹▹▸"]
    } else {
        &[">    ", " >   ", "  >  ", "   > ", "    >"]
    }
}

/// Moon phases.
pub fn spinner_frames_moon() -> &'static [&'static str] {
    if unicode_enabled() {
        &["🌑", "🌒", "🌓", "🌔", "🌕", "🌖", "🌗", "🌘"]
    } else {
        &["-", "\\", "|", "/"]
    }
}

/// Clock faces.
pub fn spinner_frames_clock() -> &'static [&'static str] {
    if unicode_enabled() {
        &["🕛", "🕐", "🕑", "🕒", "🕓", "🕔", "🕕", "🕖", "🕗", "🕘", "🕙", "🕚"]
    } else {
        &["-", "\\", "|", "/"]
    }
}

/// Bouncing ball on a track.
pub fn spinner_frames_bounce() -> &'static [&'static str] {
    if unicode_enabled() {
        &[
            "[●    ]", "[●    ]", "[ ●   ]", "[  ●  ]", "[   ● ]", "[    ●]",
            "[    ●]", "[   ● ]", "[  ●  ]", "[ ●   ]",
        ]
    } else {
        &["[o    ]", "[ o   ]", "[  o  ]", "[   o ]", "[    o]", "[   o ]", "[  o  ]", "[ o   ]"]
    }
}

/// Growing / shrinking block pulse.
pub fn spinner_frames_pulse() -> &'static [&'static str] {
    if unicode_enabled() {
        &["▏", "▎", "▍", "▌", "▋", "▊", "▉", "█", "▉", "▊", "▋", "▌", "▍", "▎"]
    } else {
        &[".", "o", "O", "0", "O", "o"]
    }
}

/// Snake-like filling bar.
pub fn spinner_frames_snake() -> &'static [&'static str] {
    if unicode_enabled() {
        &[
            "⣀⣀⣀⣀⣀", "⣄⣀⣀⣀⣀", "⣤⣀⣀⣀⣀", "⣦⣄⣀⣀⣀",
            "⣶⣤⣄⣀⣀", "⣷⣦⣤⣄⣀", "⣿⣶⣦⣤⣄", "⣿⣿⣶⣦⣤",
            "⣿⣿⣿⣶⣦", "⣿⣿⣿⣿⣶", "⣿⣿⣿⣿⣿", "⣿⣿⣿⣿⣶",
            "⣿⣿⣿⣶⣦", "⣿⣿⣶⣦⣤", "⣿⣶⣦⣤⣄", "⣶⣦⣤⣄⣀",
            "⣦⣤⣄⣀⣀", "⣤⣀⣀⣀⣀", "⣄⣀⣀⣀⣀",
        ]
    } else {
        &[".....", "o....", "oo...", "ooo..", "oooo.", "ooooo", ".oooo", "..ooo", "...oo", "....o"]
    }
}

/// Small pixel grid cycling.
pub fn spinner_frames_pixel() -> &'static [&'static str] {
    if unicode_enabled() {
        &["⣿⣿", "⣷⣿", "⣯⣿", "⣟⣿", "⡿⣿", "⢿⣿", "⣻⣿", "⣽⣿", "⣾⣿", "⣿⣾", "⣿⣽", "⣿⣻"]
    } else {
        &["..", "o.", "oo", ".o"]
    }
}

/// Blinking block toggle.
pub fn spinner_frames_toggle() -> &'static [&'static str] {
    if unicode_enabled() {
        &["▪▫▫▫▫", "▫▪▫▫▫", "▫▫▪▫▫", "▫▫▫▪▫", "▫▫▫▫▪", "▫▫▫▪▫", "▫▫▪▫▫", "▫▪▫▫▫"]
    } else {
        &["*----", "-*---", "--*--", "---*-", "----*", "---*-", "--*--", "-*---"]
    }
}

/// Expanding / contracting progress bar.
pub fn spinner_frames_grow() -> &'static [&'static str] {
    if unicode_enabled() {
        &[
            "▰▱▱▱▱▱▱▱", "▰▰▱▱▱▱▱▱", "▰▰▰▱▱▱▱▱", "▰▰▰▰▱▱▱▱",
            "▰▰▰▰▰▱▱▱", "▰▰▰▰▰▰▱▱", "▰▰▰▰▰▰▰▱", "▰▰▰▰▰▰▰▰",
            "▱▰▰▰▰▰▰▰", "▱▱▰▰▰▰▰▰", "▱▱▱▰▰▰▰▰", "▱▱▱▱▰▰▰▰",
            "▱▱▱▱▱▰▰▰", "▱▱▱▱▱▱▰▰", "▱▱▱▱▱▱▱▰",
        ]
    } else {
        &[
            "=       ", "==      ", "===     ", "====    ",
            "=====   ", "======  ", "======= ", "========",
            " =======", "  ======", "   =====", "    ====",
            "     ===", "      ==", "       =",
        ]
    }
}