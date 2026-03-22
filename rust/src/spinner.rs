//! Standalone `Spinner`. Port of ui.go's `Spinner` type.
//!
//! Supports custom frame sets via [`Spinner::with_frames`].

use std::io::Write;
use std::sync::{
    atomic::{AtomicBool, Ordering},
    Arc, Mutex,
};
use std::thread;
use std::time::{Duration, Instant};

use crate::color::{ansi, C_INFO, C_SUCCESS, C_ERROR, DIM, RESET};
use crate::symbols::{spinner_frames, sym_ok, sym_fail, sym_ell};

const INTERVAL: Duration = Duration::from_millis(80);

/// Animated spinner — TTY-safe, non-blocking, supports custom frame sets.
///
/// # Examples
///
/// ```no_run
/// use tsuki_ux::{Spinner, spinner_frames_moon};
///
/// // Default braille frames
/// let mut s = Spinner::new("Detectando puerto…");
/// s.start();
/// std::thread::sleep(std::time::Duration::from_secs(1));
/// s.stop(true, Some("Puerto: /dev/ttyUSB0"));
///
/// // Custom frames
/// let mut s = Spinner::with_frames("Compilando…", spinner_frames_moon());
/// s.start();
/// std::thread::sleep(std::time::Duration::from_secs(1));
/// s.stop(true, None);
/// ```
pub struct Spinner {
    msg:    Arc<Mutex<String>>,
    frames: &'static [&'static str],
    tty:    bool,
    stop:   Arc<AtomicBool>,
    handle: Option<thread::JoinHandle<()>>,
    start:  Instant,
}

impl Spinner {
    /// Create a spinner with the default braille frames.
    pub fn new(msg: &str) -> Self {
        Self::with_frames(msg, spinner_frames())
    }

    /// Create a spinner with custom animation frames.
    ///
    /// Use one of the `spinner_frames_*()` functions from [`crate::symbols`],
    /// or supply your own `&'static [&'static str]`.
    pub fn with_frames(msg: &str, frames: &'static [&'static str]) -> Self {
        Self {
            msg:    Arc::new(Mutex::new(msg.to_owned())),
            frames,
            tty:    crate::color::is_tty(),
            stop:   Arc::new(AtomicBool::new(false)),
            handle: None,
            start:  Instant::now(),
        }
    }

    /// Start animation (non-blocking).
    pub fn start(&mut self) {
        if !self.tty {
            println!("  {}{}{}  {}", ansi(DIM), sym_ell(), ansi(RESET),
                     self.msg.lock().unwrap());
            return;
        }
        print!("\x1b[?25l  {}  {}", C_INFO.paint(self.frames[0]),
               self.msg.lock().unwrap());
        std::io::stdout().flush().ok();

        let stop   = Arc::clone(&self.stop);
        let msg    = Arc::clone(&self.msg);
        let frames = self.frames;

        self.handle = Some(thread::spawn(move || {
            let mut i = 1usize;
            while !stop.load(Ordering::Relaxed) {
                thread::sleep(INTERVAL);
                let frame   = frames[i % frames.len()];
                let current = msg.lock().unwrap().clone();
                print!("\r  {}  {}", C_INFO.paint(frame), current);
                std::io::stdout().flush().ok();
                i += 1;
            }
        }));
    }

    /// Change the spinner label mid-animation.
    pub fn update_label(&self, label: &str) {
        if let Ok(mut m) = self.msg.lock() {
            *m = label.to_owned();
        }
    }

    /// Stop and print the final status line.
    ///
    /// ```text
    /// ok=true  →  ✔  label  [1.2s]
    /// ok=false →  ✖  label  reason
    /// ```
    pub fn stop(mut self, ok: bool, msg: Option<&str>) {
        self.stop.store(true, Ordering::Relaxed);
        if let Some(h) = self.handle.take() {
            let _ = h.join();
        }

        let elapsed = {
            let d = self.start.elapsed();
            if d.as_millis() < 1000 {
                format!("{}ms", d.as_millis())
            } else {
                format!("{:.1}s", d.as_secs_f64())
            }
        };

        if self.tty {
            print!("\r\x1b[K\x1b[?25h");
        }

        let label = self.msg.lock().unwrap().clone();
        if ok {
            let suffix = msg.map(|m| format!("  {}", m)).unwrap_or_default();
            println!("  {}  {}  {}[{}]{}{}",
                C_SUCCESS.paint(sym_ok()), label,
                ansi(DIM), elapsed, ansi(RESET),
                suffix);
        } else {
            let reason = msg.unwrap_or("failed");
            println!("  {}  {}  {}{}{}",
                C_ERROR.paint(sym_fail()), label,
                ansi(DIM), reason, ansi(RESET));
        }
        std::io::stdout().flush().ok();
    }

    /// Stop silently (success, no output).
    pub fn stop_silent(mut self) {
        self.stop.store(true, Ordering::Relaxed);
        if let Some(h) = self.handle.take() {
            let _ = h.join();
        }
        if self.tty {
            print!("\r\x1b[K\x1b[?25h");
            std::io::stdout().flush().ok();
        }
    }
}