//! Core output functions: success, fail, warn, info, step, note, section, header.
//! Port of build.py's and ui.go's status/section/header functions.

use crate::color::{strip_ansi, ansi, C_SUCCESS, C_ERROR, C_WARN, C_INFO, C_STEP, C_TITLE, BOLD, DIM, RESET};
use crate::symbols::*;

// ── Terminal width ────────────────────────────────────────────────────────────

/// Current terminal width, defaulting to 100.
pub fn term_w() -> usize {
    // Respect COLUMNS env var (set by most shells).
    if let Ok(cols) = std::env::var("COLUMNS") {
        if let Ok(n) = cols.parse::<usize>() {
            if n > 0 { return n; }
        }
    }
    #[cfg(unix)]
    {
        if let Some(w) = unix_term_w() { return w; }
    }
    100
}

#[cfg(unix)]
fn unix_term_w() -> Option<usize> {
    // winsize struct: rows(u16), cols(u16), xpixels(u16), ypixels(u16)
    let mut ws: [u16; 4] = [0; 4];
    extern "C" {
        fn ioctl(fd: i32, request: u64, ...) -> i32;
    }
    // TIOCGWINSZ: Linux = 0x5413, macOS = 0x40087468
    #[cfg(target_os = "linux")]
    const TIOCGWINSZ: u64 = 0x5413;
    #[cfg(target_os = "macos")]
    const TIOCGWINSZ: u64 = 0x40087468;
    #[cfg(not(any(target_os = "linux", target_os = "macos")))]
    const TIOCGWINSZ: u64 = 0x5413;

    let ret = unsafe { ioctl(1, TIOCGWINSZ, ws.as_mut_ptr()) };
    if ret == 0 && ws[1] > 0 { Some(ws[1] as usize) } else { None }
}

fn hline(n: usize) -> String {
    box_h().repeat(n)
}

// ── Status primitives ─────────────────────────────────────────────────────────

/// `  ✔  msg`  (green bold)
pub fn success(msg: &str) {
    println!("  {}  {}", C_SUCCESS.paint(sym_ok()), msg);
}

/// `  ✖  msg`  (red bold, stderr)
pub fn fail(msg: &str) {
    eprintln!("  {}  {}", C_ERROR.paint(sym_fail()), msg);
}

/// `  ⚠  msg`  (yellow bold)
pub fn warn(msg: &str) {
    println!("  {}  {}", C_WARN.paint(sym_warn()), msg);
}

/// `  ●  msg`  (cyan)
pub fn info(msg: &str) {
    println!("  {}  {}", C_INFO.paint(sym_info()), msg);
}

/// `  ▶  msg`  — main step header with preceding blank line.
pub fn step(msg: &str) {
    println!();
    println!("  {}  {}{}{}", C_STEP.paint(sym_step()), ansi(BOLD), msg, ansi(RESET));
}

/// Dim auxiliary note.
pub fn note(msg: &str) {
    println!("  {}{}  {}{}", ansi(DIM), sym_info(), msg, ansi(RESET));
}

/// `   •  name  (size)` — build artifact entry.
pub fn artifact(name: &str, size: Option<&str>) {
    let size_part = size
        .map(|s| format!("  {}({}){}", ansi(DIM), s, ansi(RESET)))
        .unwrap_or_default();
    println!("   {}  {}{}", C_STEP.paint(sym_bullet()), name, size_part);
}

/// Full-width rounded header box.
///
/// ```text
/// ╭──────────────────────────────────────────────────────────╮
/// │  🌙 title                                                │
/// ╰──────────────────────────────────────────────────────────╯
/// ```
pub fn header(title: &str) {
    let w = term_w();
    let h = w.saturating_sub(2);
    let bar = hline(h);
    println!();
    println!("{}{}{}{}{}", ansi(DIM), box_tl(), bar, box_tr(), ansi(RESET));
    let content = format!("  🌙 {}", title);
    let visible = strip_ansi(&content).chars().count();
    let pad = h.saturating_sub(visible + 1);
    println!(
        "{}{}{}{}{}{}{}",
        ansi(DIM), box_v(), ansi(RESET),
        C_TITLE.paint(&content),
        " ".repeat(pad),
        ansi(DIM), box_v()
    );
    println!("{}{}{}{}{}", ansi(DIM), box_bl(), bar, box_br(), ansi(RESET));
}

/// Section header (platform block).
///
/// ```text
/// ╭─ Platform: linux-amd64 ────────────────────────────────╮
/// ```
pub fn section(title: &str) {
    let w = term_w().min(72);
    let inner = format!(" {} ", title);
    let pad = w.saturating_sub(inner.chars().count() + 4);
    println!();
    println!(
        "{}{}{}{}{}{}{}{}{}",
        ansi(DIM), box_tl(), box_h(), ansi(RESET),
        C_TITLE.paint(&inner),
        ansi(DIM), hline(pad), box_tr(), ansi(RESET),
    );
}

/// Closing border of a section.
pub fn section_end() {
    let w = term_w().min(72);
    println!("{}{}{}{}", ansi(DIM), box_bl(), hline(w.saturating_sub(2)), box_br());
}

/// Inline progress bar.
///
/// ```text
///   label  [████████░░░░]  75%
/// ```
pub fn progress_bar(label: &str, done: usize, total: usize, width: usize) {
    let pct = if total == 0 { 0.0 } else { done as f64 / total as f64 };
    let filled = (width as f64 * pct).round() as usize;
    let bar = format!(
        "{}{}{}{}{}{}",
        ansi(C_SUCCESS.open()), "█".repeat(filled), ansi(RESET),
        ansi(DIM), "░".repeat(width.saturating_sub(filled)), ansi(RESET),
    );
    println!("  {}  [{}]  {}%", label, bar, (pct * 100.0) as usize);
}
