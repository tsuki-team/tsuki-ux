//! `LiveBlock` — Docker-style collapsible command-output block.
//!
//! Port of `LiveBlock` from build.py and ui.go's `LiveBlock`.
//! Anti-flicker: single `write()` per frame, cursor hidden, rolling window.

use std::io::Write;
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::{Duration, Instant};

use crate::color::{ansi, C_SUCCESS, C_ERROR, C_INFO, C_MUTED, DIM, RESET};
use crate::symbols::{spinner_frames, sym_ok, sym_fail, sym_pipe, sym_ell, box_bl, box_h};
use crate::primitives::term_w;

const LIVE_LINES: usize = 6;
const INTERVAL:   Duration = Duration::from_millis(100);

fn truncate(s: &str, max: usize) -> String {
    let chars: Vec<char> = s.chars().collect();
    if chars.len() <= max { s.to_owned() }
    else { chars[..max.saturating_sub(1)].iter().collect::<String>() + sym_ell() }
}

fn fmt_elapsed(d: Duration) -> String {
    let ms = d.as_millis();
    if ms < 1000 { format!("{}ms", ms) } else { format!("{:.1}s", d.as_secs_f64()) }
}

struct State {
    lines:   Vec<String>,
    painted: usize,
    stopped: bool,
}

/// Docker-style collapsible command-output block.
///
/// # Example
/// ```no_run
/// use tsuki_ux::LiveBlock;
///
/// let mut b = LiveBlock::new("cargo build --release");
/// b.start();
/// b.line("Compiling main.rs...");
/// b.finish(true, None);
/// ```
pub struct LiveBlock {
    label:  String,
    state:  Arc<Mutex<State>>,
    tty:    bool,
    t0:     Option<Instant>,
    handle: Option<thread::JoinHandle<()>>,
}

impl LiveBlock {
    /// Create a new block with the given label.
    pub fn new(label: &str) -> Self {
        let tty = crate::color::is_tty();
        let w   = term_w();
        let max = w.saturating_sub(10).max(20);
        let label = if label.chars().count() <= max { label.to_owned() }
                    else { label.chars().take(max - 1).collect::<String>() + sym_ell() };
        Self {
            label,
            state:  Arc::new(Mutex::new(State { lines: vec![], painted: 0, stopped: false })),
            tty,
            t0:     None,
            handle: None,
        }
    }

    /// Begin animation and print the spinner header.
    pub fn start(&mut self) {
        self.t0 = Some(Instant::now());
        if !self.tty {
            println!("  {}{}{}  {}", ansi(DIM), sym_ell(), ansi(RESET), self.label);
            return;
        }
        // Hide cursor + emit first frame without trailing \n.
        print!("\x1b[?25l  {}  {}\x1b[K",
               C_INFO.paint(spinner_frames()[0]), self.label);
        std::io::stdout().flush().ok();

        let state = Arc::clone(&self.state);
        let label = self.label.clone();
        self.handle = Some(thread::spawn(move || {
            let frames = spinner_frames();
            let mut i  = 0usize;
            loop {
                thread::sleep(INTERVAL);
                let mut st = state.lock().unwrap();
                if st.stopped { break; }
                Self::redraw(&mut st, frames[i % frames.len()], &label);
                i += 1;
            }
        }));
    }

    fn redraw(st: &mut State, frame: &str, label: &str) {
        let w   = term_w();
        let mut buf = String::new();

        // Erase previous frame atomically.
        buf.push('\r');
        if st.painted > 0 { buf.push_str(&format!("\x1b[{}A", st.painted)); }
        buf.push_str("\x1b[J");

        // Rolling content window.
        let start   = st.lines.len().saturating_sub(LIVE_LINES);
        let visible = &st.lines[start..];
        let col_w   = w.saturating_sub(8);
        for s in visible {
            let s = if s.chars().count() > col_w { &s[..col_w] } else { s.as_str() };
            buf.push_str(&format!(
                "  {}  {}{}{}\n",
                C_MUTED.paint(sym_pipe()), ansi(DIM), s, ansi(RESET),
            ));
        }

        // Spinner line — no trailing \n so cursor stays on this row.
        buf.push_str(&format!("  {}  {}\x1b[K", C_INFO.paint(frame), label));

        print!("{}", buf);
        std::io::stdout().flush().ok();
        st.painted = visible.len();
    }

    /// Buffer a content line. TTY: shown on next tick. Non-TTY: printed immediately.
    pub fn line(&mut self, s: &str) {
        if s.is_empty() { return; }
        { self.state.lock().unwrap().lines.push(s.to_owned()); }
        if !self.tty {
            println!("  {}  {}", C_MUTED.paint(sym_pipe()),
                     truncate(s, term_w().saturating_sub(8)));
        }
    }

    /// Collapse (ok=true) or expand (ok=false) the block.
    pub fn finish(mut self, ok: bool, summary: Option<&str>) {
        let elapsed = self.t0.map(|t| t.elapsed()).unwrap_or_default();

        // Signal the spinner thread to exit and wait for it.
        { self.state.lock().unwrap().stopped = true; }
        if let Some(h) = self.handle.take() { let _ = h.join(); }

        let st = self.state.lock().unwrap();

        if self.tty {
            let mut buf = String::new();
            buf.push('\r');
            if st.painted > 0 { buf.push_str(&format!("\x1b[{}A", st.painted)); }
            buf.push_str("\x1b[J");

            if ok {
                buf.push_str(&format!(
                    "  {}  {}  {}[{}]{}\n",
                    C_SUCCESS.paint(sym_ok()), self.label,
                    ansi(DIM), fmt_elapsed(elapsed), ansi(RESET),
                ));
            } else {
                buf.push_str(&format!("  {}  {}\n", C_ERROR.paint(sym_fail()), self.label));
                let w = term_w();
                for l in &st.lines {
                    if !l.is_empty() {
                        buf.push_str(&format!(
                            "  {}  {}\n",
                            C_MUTED.paint(sym_pipe()),
                            truncate(l, w.saturating_sub(8)),
                        ));
                    }
                }
                let msg = summary.unwrap_or("failed");
                buf.push_str(&format!(
                    "  {}{} {}{}\n",
                    ansi(DIM), format!("{}{}", box_bl(), box_h()), msg, ansi(RESET),
                ));
            }
            buf.push_str("\x1b[?25h"); // restore cursor
            print!("{}", buf);
            std::io::stdout().flush().ok();
        } else {
            if ok {
                println!("  {}  {}  {}[{}]{}",
                    C_SUCCESS.paint(sym_ok()), self.label,
                    ansi(DIM), fmt_elapsed(elapsed), ansi(RESET));
            } else {
                println!("  {}  {}", C_ERROR.paint(sym_fail()), self.label);
                let w = term_w();
                for l in &st.lines {
                    if !l.is_empty() {
                        println!("  {}  {}", C_MUTED.paint(sym_pipe()),
                                 truncate(l, w.saturating_sub(8)));
                    }
                }
                println!("  {}{} {}{}",
                    ansi(DIM), format!("{}{}", box_bl(), box_h()),
                    summary.unwrap_or("failed"), ansi(RESET));
            }
        }
    }
}
