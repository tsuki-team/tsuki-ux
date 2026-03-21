//! Adaptive symbols: Unicode on modern terminals, ASCII fallback elsewhere.
//! Mirrors `_supports_unicode()` from build.py.

use std::sync::OnceLock;

static UNICODE: OnceLock<bool> = OnceLock::new();

fn supports_unicode() -> bool {
    // On Unix/macOS the locale encoding is almost always UTF-8.
    // On Windows we'd check the code page; we assume UTF-8 here
    // (Windows Terminal / modern PowerShell default to UTF-8).
    #[cfg(windows)]
    {
        // Try to read the active code page via GetConsoleOutputCP.
        #[link(name = "kernel32")]
        extern "system" {
            fn GetConsoleOutputCP() -> u32;
        }
        unsafe { GetConsoleOutputCP() == 65001 }
    }
    #[cfg(not(windows))]
    {
        // Check LANG / LC_ALL / LC_CTYPE env vars.
        for var in &["LC_ALL", "LC_CTYPE", "LANG"] {
            if let Ok(v) = std::env::var(var) {
                let v = v.to_lowercase();
                if v.contains("utf-8") || v.contains("utf8") {
                    return true;
                }
            }
        }
        // Default true on Linux/macOS — modern systems are always UTF-8.
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

pub fn box_tl() -> &'static str { if unicode_enabled() { "╭" } else { "+" } }
pub fn box_tr() -> &'static str { if unicode_enabled() { "╮" } else { "+" } }
pub fn box_bl() -> &'static str { if unicode_enabled() { "╰" } else { "+" } }
pub fn box_br() -> &'static str { if unicode_enabled() { "╯" } else { "+" } }
pub fn box_h()  -> &'static str { if unicode_enabled() { "─" } else { "-" } }
pub fn box_v()  -> &'static str { if unicode_enabled() { "│" } else { "|" } }

/// Braille spinner frames — matches ui.go and build.py exactly.
pub fn spinner_frames() -> &'static [&'static str] {
    if unicode_enabled() {
        &["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
    } else {
        &["-", "\\", "|", "/"]
    }
}
