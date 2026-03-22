//! Core output functions. Full port of tsukiux.go (Go implementation).
//!
//! Adds everything present in Go that was missing from Rust:
//! rule, separator, blank, badge, key_value, list variants,
//! indent, highlight, accent, Timer, Table, DiffView,
//! and all progress bar variants.

use crate::color::{
    strip_ansi, ansi,
    C_SUCCESS, C_ERROR, C_WARN, C_INFO, C_STEP, C_TITLE,
    C_MUTED, C_HIGHLIGHT, C_ACCENT, C_KEY, C_VALUE,
    C_TB_BORDER, C_TB_FILE,
    BOLD, DIM, RESET,
};
use crate::symbols::*;
use std::time::Instant;

// ── Terminal width ────────────────────────────────────────────────────────────

/// Current terminal width, defaulting to 100.
pub fn term_w() -> usize {
    if let Ok(cols) = std::env::var("COLUMNS") {
        if let Ok(n) = cols.parse::<usize>() {
            if n > 0 { return n; }
        }
    }
    #[cfg(unix)]
    if let Some(w) = unix_term_w() { return w; }
    100
}

#[cfg(unix)]
fn unix_term_w() -> Option<usize> {
    let mut ws: [u16; 4] = [0; 4];
    extern "C" { fn ioctl(fd: i32, request: u64, ...) -> i32; }
    #[cfg(target_os = "linux")]   const TIOCGWINSZ: u64 = 0x5413;
    #[cfg(target_os = "macos")]   const TIOCGWINSZ: u64 = 0x40087468;
    #[cfg(not(any(target_os = "linux", target_os = "macos")))]
    const TIOCGWINSZ: u64 = 0x5413;
    let ret = unsafe { ioctl(1, TIOCGWINSZ, ws.as_mut_ptr()) };
    if ret == 0 && ws[1] > 0 { Some(ws[1] as usize) } else { None }
}

fn hline(n: usize) -> String { box_h().repeat(n) }

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
pub fn header(title: &str) {
    let w = term_w();
    let h = w.saturating_sub(2);
    let bar = hline(h);
    println!();
    println!("{}{}{}{}{}", ansi(DIM), box_tl(), bar, box_tr(), ansi(RESET));
    let content = format!("  🌙 {}", title);
    let pad = h.saturating_sub(strip_ansi(&content).chars().count() + 1);
    println!("{}{}{}{}{}{}{}", ansi(DIM), box_v(), ansi(RESET), C_TITLE.paint(&content), " ".repeat(pad), ansi(DIM), box_v());
    println!("{}{}{}{}{}", ansi(DIM), box_bl(), bar, box_br(), ansi(RESET));
}

/// Section header.
pub fn section(title: &str) {
    let w = term_w().min(72);
    let inner = format!(" {} ", title);
    let pad = w.saturating_sub(inner.chars().count() + 4);
    println!();
    println!("{}{}{}{}{}{}{}{}{}", ansi(DIM), box_tl(), box_h(), ansi(RESET), C_TITLE.paint(&inner), ansi(DIM), hline(pad), box_tr(), ansi(RESET));
}

/// Closing border of a section.
pub fn section_end() {
    let w = term_w().min(72);
    println!("{}{}{}{}", ansi(DIM), box_bl(), hline(w.saturating_sub(2)), box_br());
}

// ── Layout helpers ────────────────────────────────────────────────────────────

/// Full-width horizontal rule with an optional centered label.
///
/// ```text
/// ──────────────── label ────────────────
/// ```
pub fn rule(label: &str) {
    let w = term_w();
    if label.is_empty() {
        println!("{}{}{}", ansi(DIM), hline(w), ansi(RESET));
        return;
    }
    let inner = format!(" {} ", label);
    let sides = w.saturating_sub(inner.len());
    let left  = sides / 2;
    let right = sides - left;
    println!("{}{}{}{}{}{}", ansi(DIM), hline(left), ansi(RESET), C_MUTED.paint(&inner), ansi(DIM), hline(right));
}

/// Blank line, dim rule, blank line.
pub fn separator() {
    println!();
    rule("");
    println!();
}

/// Print an empty line.
pub fn blank() { println!(); }

// ── Inline content helpers ────────────────────────────────────────────────────

/// Return a color-coded inline tag string: `[ label ]`
///
/// `style`: `"success"` | `"error"` | `"warn"` | `"info"` | `"muted"` | `"highlight"` | `"accent"`
pub fn badge(label: &str, style: &str) -> String {
    let text = format!("[ {} ]", label);
    match style {
        "success"   => C_SUCCESS.paint(&text),
        "error"     => C_ERROR.paint(&text),
        "warn"      => C_WARN.paint(&text),
        "muted"     => C_MUTED.paint(&text),
        "highlight" => C_HIGHLIGHT.paint(&text),
        "accent"    => C_ACCENT.paint(&text),
        _           => C_INFO.paint(&text),
    }
}

/// Print a badge followed by a message on the same line.
pub fn badge_line(label: &str, style: &str, msg: &str) {
    println!("  {}  {}", badge(label, style), msg);
}

/// Print a single aligned key → value line.
pub fn key_value(key: &str, value: &str) {
    println!("  {}  {}  {}", C_KEY.paint(key), C_MUTED.paint(sym_arrow()), C_VALUE.paint(value));
}

/// Print a bulleted list.
pub fn list(items: &[&str]) {
    for item in items {
        println!("  {}  {}", C_MUTED.paint(sym_bullet()), item);
    }
}

/// Print a numbered list.
pub fn numbered_list(items: &[&str]) {
    for (i, item) in items.iter().enumerate() {
        println!("  {}{}.{}  {}", ansi(DIM), i + 1, ansi(RESET), item);
    }
}

/// Print a list where each item can be checked or unchecked.
pub fn check_list(items: &[&str], checked: &[bool]) {
    for (i, item) in items.iter().enumerate() {
        let sym = if checked.get(i).copied().unwrap_or(false) {
            C_SUCCESS.paint(sym_check())
        } else {
            C_MUTED.paint(sym_cross())
        };
        println!("  {}  {}", sym, item);
    }
}

/// Print each line with a left pipe indent.
pub fn indent(text: &str) {
    for line in text.lines() {
        println!("  {}  {}{}{}", C_MUTED.paint(sym_pipe()), ansi(DIM), line, ansi(RESET));
    }
}

/// Print msg with high-visibility magenta emphasis.
pub fn highlight(msg: &str) {
    println!("  {}{}{}", C_HIGHLIGHT.open(), msg, ansi(RESET));
}

/// Print msg in bold cyan — secondary emphasis.
pub fn accent(msg: &str) {
    println!("  {}{}{}", C_ACCENT.open(), msg, ansi(RESET));
}

// ── Timer ─────────────────────────────────────────────────────────────────────

/// Wall-clock timer to embed in step output.
///
/// ```no_run
/// use tsuki_ux::{Timer, success};
///
/// let t = Timer::new();
/// // ... do work ...
/// success(&format!("done  {}", t.elapsed_dim()));
/// ```
pub struct Timer {
    start: Instant,
}

impl Timer {
    pub fn new() -> Self { Self { start: Instant::now() } }

    fn fmt(&self) -> String {
        let d = self.start.elapsed();
        if d.as_millis() < 1000 {
            format!("{}ms", d.as_millis())
        } else {
            format!("{:.1}s", d.as_secs_f64())
        }
    }

    /// Human-readable elapsed time.
    pub fn elapsed(&self) -> String { self.fmt() }

    /// Elapsed time formatted as a dim string ready to embed in output.
    pub fn elapsed_dim(&self) -> String {
        format!("{}[{}]{}", ansi(DIM), self.fmt(), ansi(RESET))
    }
}

impl Default for Timer {
    fn default() -> Self { Self::new() }
}

// ── Table ─────────────────────────────────────────────────────────────────────

/// Column alignment.
pub enum Align { Left, Right, Center }

/// One column definition for [`table`].
pub struct TableColumn<'a> {
    pub header: &'a str,
    pub align:  Align,
}

/// Render a bordered table with a header row and data rows.
///
/// ```text
/// ╭── title ─────────────────────────────────────────────────╮
/// │  Board          MCU          Port           Baud          │
/// │  ───────────    ─────────    ──────────     ──────────    │
/// │  arduino-nano   ATmega328P   /dev/ttyUSB0   115200        │
/// ╰──────────────────────────────────────────────────────────╯
/// ```
pub fn table(title: &str, cols: &[TableColumn<'_>], rows: &[Vec<&str>]) {
    let mut widths: Vec<usize> = cols.iter().map(|c| c.header.chars().count()).collect();
    for row in rows {
        for (i, cell) in row.iter().enumerate() {
            if i < widths.len() {
                let l = strip_ansi(cell).chars().count();
                if l > widths[i] { widths[i] = l; }
            }
        }
    }

    let header_len: usize = widths.iter().sum::<usize>() + widths.len().saturating_sub(1) * 3;
    let w = term_w();
    let mut inner = w.saturating_sub(2);
    let min_i = header_len + 4;
    let title_i = title.len() + 6;
    if min_i > inner { inner = min_i; }
    if title_i > inner { inner = title_i; }

    // top border
    if !title.is_empty() {
        let ts       = format!(" {} ", title);
        let pad_r    = inner.saturating_sub(ts.len() + 2);
        let top_left = C_TB_BORDER.paint(&format!("{}{}", box_tl(), hline(2)));
        let mid      = C_TITLE.paint(&ts);
        let top_right = C_TB_BORDER.paint(&format!("{}{}", hline(pad_r), box_tr()));
        println!("{}{}{}", top_left, mid, top_right);
    } else {
        println!("{}", C_TB_BORDER.paint(&format!("{}{}{}", box_tl(), hline(inner), box_tr())));
    }

    let print_row = |cells: &[String], header_style: bool| {
        let mut rich      = String::new();
        let mut plain_len = 0usize;
        for (i, w_col) in widths.iter().enumerate() {
            let cell  = cells.get(i).map(|s| s.as_str()).unwrap_or("");
            let plain = strip_ansi(cell);
            let pad   = w_col.saturating_sub(plain.chars().count());
            // bind the painted version so it lives long enough
            let painted_owned: String;
            let styled: &str = if header_style {
                painted_owned = C_TITLE.paint(cell);
                &painted_owned
            } else {
                cell
            };
            let align = cols.get(i).map(|c| match c.align {
                Align::Right  => "right",
                Align::Center => "center",
                _             => "left",
            }).unwrap_or("left");
            match align {
                "right" => {
                    rich.push_str(&" ".repeat(pad));
                    rich.push_str(styled);
                }
                "center" => {
                    let lp = pad / 2;
                    let rp = pad - lp;
                    rich.push_str(&" ".repeat(lp));
                    rich.push_str(styled);
                    rich.push_str(&" ".repeat(rp));
                }
                _ => {
                    rich.push_str(styled);
                    rich.push_str(&" ".repeat(pad));
                }
            }
            plain_len += w_col;
            if i < widths.len() - 1 { rich.push_str("   "); plain_len += 3; }
        }
        let row_pad    = inner.saturating_sub(plain_len + 1);
        let border_v   = C_TB_BORDER.paint(box_v());
        println!("{} {}{} {}", border_v, rich, " ".repeat(row_pad), border_v);
    };

    // header
    let headers: Vec<String> = cols.iter().map(|c| c.header.to_owned()).collect();
    print_row(&headers, true);
    // separator
    let sep: Vec<String> = widths.iter().map(|&w| C_MUTED.paint(&hline(w))).collect();
    print_row(&sep, false);
    // data rows
    for (ri, row) in rows.iter().enumerate() {
        let styled: Vec<String> = row.iter().enumerate().map(|(_, cell)| {
            if ri % 2 == 1 { format!("{}{}{}", ansi(DIM), cell, ansi(RESET)) }
            else { (*cell).to_owned() }
        }).collect();
        print_row(&styled, false);
    }

    println!("{}", C_TB_BORDER.paint(&format!("{}{}{}", box_bl(), hline(inner), box_br())));
}

// ── DiffView ──────────────────────────────────────────────────────────────────

/// A diff line kind.
pub enum DiffKind { Context, Added, Removed }

/// One line in a diff view.
pub struct DiffLine {
    pub kind: DiffKind,
    pub text: String,
}

/// Render a compact unified-diff-style block.
pub fn diff_view(title: &str, start_line: usize, lines: &[DiffLine]) {
    let w     = term_w();
    let inner = w.saturating_sub(2);

    // top border — bind temporaries explicitly
    let ts        = format!(" {} ", title);
    let pad_r     = inner.saturating_sub(ts.len() + 2);
    let top_left  = C_TB_BORDER.paint(&format!("{}{}", box_tl(), hline(2)));
    let mid       = C_TB_FILE.paint(&ts);
    let top_right = C_TB_BORDER.paint(&format!("{}{}", hline(pad_r), box_tr()));
    println!("{}{}{}", top_left, mid, top_right);

    let sep        = C_TB_BORDER.paint(&format!(" {} ", box_v()));
    let mut line_no = start_line;

    for dl in lines {
        let num = format!("{:4}", line_no);

        // bind every paint() result to a local so nothing is borrowed from a temp
        let (prefix, num_s, text_s) = match dl.kind {
            DiffKind::Added => {
                line_no += 1;
                (
                    C_SUCCESS.paint("  + "),
                    C_SUCCESS.paint(&num),
                    C_SUCCESS.paint(&dl.text),
                )
            }
            DiffKind::Removed => {
                (
                    C_ERROR.paint("  - "),
                    C_ERROR.paint(&num),
                    C_MUTED.paint(&dl.text),
                )
            }
            DiffKind::Context => {
                line_no += 1;
                (
                    "    ".to_owned(),
                    C_MUTED.paint(&num),
                    format!("{}{}{}", ansi(crate::color::DIM), &dl.text, ansi(RESET)),
                )
            }
        };

        let content   = format!("{}{}{}{}", prefix, num_s, sep, text_s);
        let plain_len = 4 + 4 + 3 + dl.text.chars().count();
        let pad       = inner.saturating_sub(plain_len + 1);
        let bv        = C_TB_BORDER.paint(box_v());
        println!("{}{}{} {}", bv, content, " ".repeat(pad), bv);
    }

    println!("{}", C_TB_BORDER.paint(&format!("{}{}{}", box_bl(), hline(inner), box_br())));
}

// ── Progress bar variants ─────────────────────────────────────────────────────

fn pct_filled(done: usize, total: usize, width: usize) -> usize {
    let total = total.max(1);
    let f = (done as f64 / total as f64 * width as f64 + 0.5) as usize;
    f.min(width)
}

fn pct_int(done: usize, total: usize) -> usize {
    let total = total.max(1);
    ((done as f64 / total as f64) * 100.0) as usize
}

/// Classic block bar: `  label  [████████░░░░]  75%`
pub fn progress_bar(label: &str, done: usize, total: usize, width: usize) {
    let filled = pct_filled(done, total, width);
    let bar = format!(
        "{}{}{}{}{}{}",
        C_SUCCESS.open(), "█".repeat(filled), ansi(RESET),
        ansi(DIM), "░".repeat(width.saturating_sub(filled)), ansi(RESET),
    );
    println!("  {}  [{}]  {}%", label, bar, pct_int(done, total));
}

/// Slim line bar: `  label  ──────╴          40%`
pub fn progress_bar_thin(label: &str, done: usize, total: usize, width: usize) {
    let filled = pct_filled(done, total, width);
    let tip = if filled > 0 && filled < width { "╴" } else { "" };
    let dashes = filled.saturating_sub(tip.len());
    let bar = format!(
        "{}{}{}{}{}{}",
        C_SUCCESS.open(), "─".repeat(dashes), tip, ansi(RESET),
        C_MUTED.open(), " ".repeat(width.saturating_sub(filled)),
    );
    println!("  {}  {}  {}%", label, bar, pct_int(done, total));
}

/// High-resolution braille bar: `  label  ⣿⣿⣿⣿⣦⣀⣀  60%`
pub fn progress_bar_braille(label: &str, done: usize, total: usize, width: usize) {
    let total = total.max(1);
    let eighths = ((done as f64 / total as f64) * (width * 8) as f64 + 0.5) as usize;
    let full = eighths / 8;
    let rem  = eighths % 8;
    let blocks = ["⣀","⣄","⣤","⣦","⣶","⣷","⣿"];
    let mut bar = String::new();
    for i in 0..width {
        if i < full           { bar.push_str(&C_SUCCESS.paint("⣿")); }
        else if i == full && rem > 0 { bar.push_str(&C_INFO.paint(blocks[rem - 1])); }
        else                  { bar.push_str(&C_MUTED.paint("⣀")); }
    }
    println!("  {}  {}  {}%", label, bar, pct_int(done, total));
}

/// Dot bar: `  label  ●●●●●●○○○○  67%`
pub fn progress_bar_dots(label: &str, done: usize, total: usize, width: usize) {
    let filled = pct_filled(done, total, width);
    let bar = format!(
        "{}{}{}{}{}{}",
        C_SUCCESS.open(), "●".repeat(filled), ansi(RESET),
        C_MUTED.open(), "○".repeat(width.saturating_sub(filled)), ansi(RESET),
    );
    println!("  {}  {}  {}%", label, bar, pct_int(done, total));
}

/// Slim filled/empty block bar: `  label  ▰▰▰▰▰▰▱▱▱▱  60%`
pub fn progress_bar_slim(label: &str, done: usize, total: usize, width: usize) {
    let filled = pct_filled(done, total, width);
    let bar = format!(
        "{}{}{}{}{}{}",
        C_SUCCESS.open(), "▰".repeat(filled), ansi(RESET),
        C_MUTED.open(), "▱".repeat(width.saturating_sub(filled)), ansi(RESET),
    );
    println!("  {}  {}  {}%", label, bar, pct_int(done, total));
}

/// Gradient shaded bar: `  label  [████▓▒░      ]  45%`
pub fn progress_bar_gradient(label: &str, done: usize, total: usize, width: usize) {
    let total = total.max(1);
    let units = ((done as f64 / total as f64) * (width * 4) as f64 + 0.5) as usize;
    let full = units / 4;
    let rem  = units % 4;
    let shades = [" ", "░", "▒", "▓"];
    let mut bar = String::new();
    for i in 0..width {
        if i < full      { bar.push_str(&C_SUCCESS.paint("█")); }
        else if i == full { bar.push_str(&C_INFO.paint(shades[rem])); }
        else             { bar.push_str(&C_MUTED.paint(" ")); }
    }
    println!("  {}  [{}]  {}%", label, bar, pct_int(done, total));
}

/// Classic arrow bar: `  label  [=======>    ]  56%`
pub fn progress_bar_arrow(label: &str, done: usize, total: usize, width: usize) {
    let filled = pct_filled(done, total, width);
    let body = if filled == 0 {
        C_MUTED.paint(&"-".repeat(width))
    } else if filled >= width {
        C_SUCCESS.paint(&"=".repeat(width))
    } else {
        format!(
            "{}{}{}{}",
            C_SUCCESS.paint(&format!("{}>" , "=".repeat(filled.saturating_sub(1)))),
            C_MUTED.open(),
            "-".repeat(width.saturating_sub(filled)),
            ansi(RESET),
        )
    };
    println!("  {}  [{}]  {}%", label, body, pct_int(done, total));
}

/// Step counter: `  label  [■■■□□□□□]  3/8`
pub fn progress_bar_steps(label: &str, done: usize, total: usize) {
    let done = done.min(total);
    let bar = format!(
        "{}{}{}{}{}{}",
        C_SUCCESS.open(), "■".repeat(done), ansi(RESET),
        C_MUTED.open(), "□".repeat(total.saturating_sub(done)), ansi(RESET),
    );
    println!("  {}  [{}]  {}/{}", label, bar, done, total);
}

/// Segmented square bar: `  label  ▪▪▪▪▪▫▫▫▫▫  50%`
pub fn progress_bar_squares(label: &str, done: usize, total: usize, width: usize) {
    let filled = pct_filled(done, total, width);
    let bar = format!(
        "{}{}{}{}{}{}",
        C_SUCCESS.open(), "▪".repeat(filled), ansi(RESET),
        C_MUTED.open(), "▫".repeat(width.saturating_sub(filled)), ansi(RESET),
    );
    println!("  {}  {}  {}%", label, bar, pct_int(done, total));
}