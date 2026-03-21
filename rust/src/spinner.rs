//! Standalone braille `Spinner`. Port of ui.go's `Spinner` type.

use std::io::Write;
use std::sync::{Arc, atomic::{AtomicBool, Ordering}};
use std::thread;
use std::time::Duration;

use crate::color::{ansi, C_INFO, C_SUCCESS, C_ERROR, DIM, RESET};
use crate::symbols::{spinner_frames, sym_ok, sym_fail, sym_ell};

const INTERVAL: Duration = Duration::from_millis(80); // matches ui.go's 80 ms

/// Braille spinner for tasks without streaming output.
///
/// # Example
/// ```no_run
/// use tsuki_ux::Spinner;
///
/// let mut s = Spinner::new("Detectando puerto…");
/// s.start();
/// std::thread::sleep(std::time::Duration::from_secs(2));
/// s.stop(true, Some("Puerto: /dev/ttyUSB0"));
/// ```
pub struct Spinner {
    msg:    String,
    tty:    bool,
    stop:   Arc<AtomicBool>,
    handle: Option<thread::JoinHandle<()>>,
}

impl Spinner {
    pub fn new(msg: &str) -> Self {
        Self {
            msg:    msg.to_owned(),
            tty:    crate::color::is_tty(),
            stop:   Arc::new(AtomicBool::new(false)),
            handle: None,
        }
    }

    /// Start animation (non-blocking).
    pub fn start(&mut self) {
        if !self.tty {
            println!("  {}{}{}  {}", ansi(DIM), sym_ell(), ansi(RESET), self.msg);
            return;
        }
        // Emit first frame without trailing \n.
        print!("  {}  {}", C_INFO.paint(spinner_frames()[0]), self.msg);
        std::io::stdout().flush().ok();

        let stop = Arc::clone(&self.stop);
        let msg  = self.msg.clone();
        self.handle = Some(thread::spawn(move || {
            let frames = spinner_frames();
            let mut i = 1usize;
            while !stop.load(Ordering::Relaxed) {
                thread::sleep(INTERVAL);
                let frame = frames[i % frames.len()];
                print!("\r  {}  {}", C_INFO.paint(frame), msg);
                std::io::stdout().flush().ok();
                i += 1;
            }
        }));
    }

    /// Stop and print the final status line.
    pub fn stop(mut self, ok: bool, msg: Option<&str>) {
        self.stop.store(true, Ordering::Relaxed);
        if let Some(h) = self.handle.take() { let _ = h.join(); }

        if self.tty { print!("\r\x1b[K"); }

        let final_msg = msg.unwrap_or(&self.msg);
        if ok { println!("  {}  {}", C_SUCCESS.paint(sym_ok()), final_msg); }
        else  { println!("  {}  {}", C_ERROR.paint(sym_fail()),  final_msg); }
        std::io::stdout().flush().ok();
    }
}
