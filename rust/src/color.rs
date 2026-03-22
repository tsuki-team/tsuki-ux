//! ANSI color codes with graceful TTY / NO_COLOR / Windows detection.
//! Includes text decoration, 256-color, truecolor, and a composable Style builder.

use std::sync::OnceLock;

// ── TTY detection ─────────────────────────────────────────────────────────────

/// Returns true when stdout (fd 1) is a real terminal.
pub fn is_tty() -> bool {
    #[cfg(unix)]
    {
        extern "C" { fn isatty(fd: i32) -> i32; }
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

// ── Palette ───────────────────────────────────────────────────────────────────

pub const RESET:     &str = "\x1b[0m";
pub const BOLD:      &str = "\x1b[1m";
pub const DIM:       &str = "\x1b[2m";
pub const ITALIC:    &str = "\x1b[3m";
pub const UNDERLINE: &str = "\x1b[4m";
pub const BLINK:     &str = "\x1b[5m";
pub const REVERSE:   &str = "\x1b[7m";
pub const STRIKE:    &str = "\x1b[9m";
pub const OVERLINE:  &str = "\x1b[53m";

pub const C_SUCCESS:   Color = Color::new("\x1b[1;92m");
pub const C_ERROR:     Color = Color::new("\x1b[1;91m");
pub const C_WARN:      Color = Color::new("\x1b[1;93m");
pub const C_INFO:      Color = Color::new("\x1b[96m");
pub const C_STEP:      Color = Color::new("\x1b[36m");
pub const C_TITLE:     Color = Color::new("\x1b[1;97m");
pub const C_MUTED:     Color = Color::new("\x1b[90m");
pub const C_HIGHLIGHT: Color = Color::new("\x1b[1;95m");
pub const C_ACCENT:    Color = Color::new("\x1b[1;96m");

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

// ── Text decoration helpers ───────────────────────────────────────────────────

/// Emit a raw ANSI escape string only when color is enabled.
pub fn ansi(code: &'static str) -> &'static str {
    if color_enabled() { code } else { "" }
}

/// Return text with underline decoration.
pub fn underline(s: &str) -> String {
    if color_enabled() { format!("{}{}{}", UNDERLINE, s, RESET) } else { s.to_owned() }
}

/// Return text with strikethrough decoration.
pub fn strike(s: &str) -> String {
    if color_enabled() { format!("{}{}{}", STRIKE, s, RESET) } else { s.to_owned() }
}

/// Return text with overline decoration.
pub fn overline(s: &str) -> String {
    if color_enabled() { format!("{}{}{}", OVERLINE, s, RESET) } else { s.to_owned() }
}

/// Return blinking text (not supported in all terminals).
pub fn blink(s: &str) -> String {
    if color_enabled() { format!("{}{}{}", BLINK, s, RESET) } else { s.to_owned() }
}

/// Return text with colors reversed.
pub fn reverse(s: &str) -> String {
    if color_enabled() { format!("{}{}{}", REVERSE, s, RESET) } else { s.to_owned() }
}

/// Return bold text.
pub fn bold(s: &str) -> String {
    if color_enabled() { format!("{}{}{}", BOLD, s, RESET) } else { s.to_owned() }
}

/// Return dim text.
pub fn dim(s: &str) -> String {
    if color_enabled() { format!("{}{}{}", DIM, s, RESET) } else { s.to_owned() }
}

/// Return italic text.
pub fn italic(s: &str) -> String {
    if color_enabled() { format!("{}{}{}", ITALIC, s, RESET) } else { s.to_owned() }
}

/// Apply a 256-color foreground (0–255).
pub fn color256(n: u8, s: &str) -> String {
    if color_enabled() { format!("\x1b[38;5;{}m{}{}", n, s, RESET) } else { s.to_owned() }
}

/// Apply a 256-color background (0–255).
pub fn bg_color256(n: u8, s: &str) -> String {
    if color_enabled() { format!("\x1b[48;5;{}m{}{}", n, s, RESET) } else { s.to_owned() }
}

/// Apply an RGB foreground color.
pub fn truecolor(r: u8, g: u8, b: u8, s: &str) -> String {
    if color_enabled() { format!("\x1b[38;2;{};{};{}m{}{}", r, g, b, s, RESET) } else { s.to_owned() }
}

/// Apply an RGB background color.
pub fn bg_truecolor(r: u8, g: u8, b: u8, s: &str) -> String {
    if color_enabled() { format!("\x1b[48;2;{};{};{}m{}{}", r, g, b, s, RESET) } else { s.to_owned() }
}

// ── Style builder ─────────────────────────────────────────────────────────────

/// Composable ANSI text styler. Chains attributes and colors.
///
/// # Example
/// ```no_run
/// use tsuki_ux::Style;
///
/// let s = Style::new().bold().underline().fg_256(208);
/// println!("{}", s.paint("warning"));
///
/// // Inline:
/// println!("{}", Style::new().strike().fg_rgb(200, 80, 80).paint("deprecated"));
/// ```
#[derive(Default)]
pub struct Style {
    codes: Vec<String>,
}

impl Style {
    pub fn new() -> Self { Self::default() }

    fn add(mut self, code: impl Into<String>) -> Self {
        self.codes.push(code.into());
        self
    }

    // ── Text attributes ───────────────────────────────────────────────────────

    pub fn bold(self)      -> Self { self.add(BOLD) }
    pub fn dim(self)       -> Self { self.add(DIM) }
    pub fn italic(self)    -> Self { self.add(ITALIC) }
    pub fn underline(self) -> Self { self.add(UNDERLINE) }
    pub fn blink(self)     -> Self { self.add(BLINK) }
    pub fn reverse(self)   -> Self { self.add(REVERSE) }
    pub fn strike(self)    -> Self { self.add(STRIKE) }
    pub fn overline(self)  -> Self { self.add(OVERLINE) }

    // ── Foreground colors ─────────────────────────────────────────────────────

    /// Apply a pre-built Color as foreground.
    pub fn fg(self, c: Color) -> Self { self.add(c.open) }

    /// Apply a raw ANSI code string.
    pub fn fg_code(self, code: &str) -> Self { self.add(code.to_owned()) }

    /// 256-color foreground (0–255).
    pub fn fg_256(self, n: u8) -> Self { self.add(format!("\x1b[38;5;{}m", n)) }

    /// Truecolor RGB foreground.
    pub fn fg_rgb(self, r: u8, g: u8, b: u8) -> Self {
        self.add(format!("\x1b[38;2;{};{};{}m", r, g, b))
    }

    // ── Background colors ─────────────────────────────────────────────────────

    /// 256-color background (0–255).
    pub fn bg_256(self, n: u8) -> Self { self.add(format!("\x1b[48;5;{}m", n)) }

    /// Truecolor RGB background.
    pub fn bg_rgb(self, r: u8, g: u8, b: u8) -> Self {
        self.add(format!("\x1b[48;2;{};{};{}m", r, g, b))
    }

    // ── Output ────────────────────────────────────────────────────────────────

    /// Wrap text in all accumulated ANSI codes.
    pub fn paint(&self, text: &str) -> String {
        if !color_enabled() || self.codes.is_empty() {
            return text.to_owned();
        }
        format!("{}{}{}", self.codes.join(""), text, RESET)
    }

    /// Print styled text followed by a newline.
    pub fn println(&self, text: &str) {
        println!("{}", self.paint(text));
    }
}

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