//! ANSI color codes with graceful TTY / NO_COLOR / Windows detection.
//! No external crates — uses `extern "C" { fn isatty }` on Unix
//! and `GetConsoleMode` on Windows for TTY detection.

use std::sync::OnceLock;

// ── TTY detection ─────────────────────────────────────────────────────────────

/// Returns true when stdout (fd 1) is a real terminal.
pub fn is_tty() -> bool {
    #[cfg(unix)]
    {
        extern "C" {
            fn isatty(fd: i32) -> i32;
        }
        unsafe { isatty(1) != 0 }
    }
    #[cfg(windows)]
    {
        use std::os::windows::io::AsRawHandle;
        #[link(name = "kernel32")]
        extern "system" {
            fn GetConsoleMode(handle: *mut core::ffi::c_void, mode: *mut u32) -> i32;
        }
        let handle = std::io::stdout().as_raw_handle();
        let mut mode: u32 = 0;
        unsafe { GetConsoleMode(handle as *mut _, &mut mode) != 0 }
    }
    #[cfg(not(any(unix, windows)))]
    { false }
}

// ── Color support ─────────────────────────────────────────────────────────────

static COLOR: OnceLock<bool> = OnceLock::new();

/// Returns true when ANSI color output should be emitted.
pub fn color_enabled() -> bool {
    *COLOR.get_or_init(|| {
        if std::env::var_os("FORCE_COLOR").is_some() { return true; }
        if !is_tty() { return false; }
        if std::env::var_os("NO_COLOR").is_some() { return false; }
        if std::env::var("TERM").as_deref() == Ok("dumb") { return false; }
        true
    })
}

// ── Color helper ──────────────────────────────────────────────────────────────

/// A simple ANSI color wrapper. Zero-cost when color is disabled.
#[derive(Clone, Copy)]
pub struct Color {
    open: &'static str,
}

impl Color {
    pub const fn new(open: &'static str) -> Self { Self { open } }

    /// Wrap `s` in ANSI codes, or return it unchanged if color is off.
    pub fn paint(self, s: &str) -> String {
        if color_enabled() { format!("{}{}\x1b[0m", self.open, s) }
        else { s.to_owned() }
    }

    /// The raw opening escape code, or "" if color is off.
    pub fn open(self) -> &'static str {
        if color_enabled() { self.open } else { "" }
    }
}

// ── Palette (mirrors ui.go exactly) ──────────────────────────────────────────

pub const RESET:   &str = "\x1b[0m";
pub const BOLD:    &str = "\x1b[1m";
pub const DIM:     &str = "\x1b[2m";
pub const ITALIC:  &str = "\x1b[3m";

pub const C_SUCCESS: Color = Color::new("\x1b[1;92m");
pub const C_ERROR:   Color = Color::new("\x1b[1;91m");
pub const C_WARN:    Color = Color::new("\x1b[1;93m");
pub const C_INFO:    Color = Color::new("\x1b[96m");
pub const C_STEP:    Color = Color::new("\x1b[36m");
pub const C_TITLE:   Color = Color::new("\x1b[1;97m");
pub const C_MUTED:   Color = Color::new("\x1b[90m");

pub const C_KEY:     Color = Color::new("\x1b[96m");
pub const C_VALUE:   Color = Color::new("\x1b[93m");
pub const C_STRING:  Color = Color::new("\x1b[92m");
pub const C_NUMBER:  Color = Color::new("\x1b[94m");
pub const C_BOOL:    Color = Color::new("\x1b[95m");
pub const C_NULL:    Color = Color::new("\x1b[90m");
pub const C_COMMENT: Color = Color::new("\x1b[2;3m");

pub const C_TB_BORDER:  Color = Color::new("\x1b[31m");
pub const C_TB_TITLE:   Color = Color::new("\x1b[1;91m");
pub const C_TB_FILE:    Color = Color::new("\x1b[96m");
pub const C_TB_LINE_C:  Color = Color::new("\x1b[93m");
pub const C_TB_FUNC:    Color = Color::new("\x1b[92m");
pub const C_TB_CODE:    Color = Color::new("\x1b[97m");
pub const C_TB_HIGH:    Color = Color::new("\x1b[1;91m");
pub const C_TB_LOCALS:  Color = Color::new("\x1b[93m");
pub const C_TB_ERRTYPE: Color = Color::new("\x1b[1;91m");
pub const C_TB_ERRMSG:  Color = Color::new("\x1b[97m");

// ── Helpers ───────────────────────────────────────────────────────────────────

/// Remove ANSI escape sequences for visible-length calculations.
pub fn strip_ansi(s: &str) -> String {
    let mut out = String::with_capacity(s.len());
    let mut in_esc = false;
    for c in s.chars() {
        match c {
            '\x1b' => { in_esc = true; }
            'm' if in_esc => { in_esc = false; }
            _ if in_esc => {}
            _ => out.push(c),
        }
    }
    out
}

/// Emit a raw ANSI escape string only when color is enabled.
pub fn ansi(code: &'static str) -> &'static str {
    if color_enabled() { code } else { "" }
}
