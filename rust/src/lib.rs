//! **tsuki-ux** — Terminal UX primitives faithful to the Tsuki project.
//!
//! Port of `cli/internal/ui/ui.go` and `tools/build.py` to Rust.
//! Zero external dependencies.
//!
//! # Quick start
//! ```no_run
//! use tsuki_ux::{step, success, LiveBlock, Spinner};
//!
//! step("Compilando firmware");
//!
//! let mut b = LiveBlock::new("cargo build --release");
//! b.start();
//! b.line("Compiling tsuki-flash v4.0.0");
//! b.finish(true, None);
//!
//! success("Firmware listo");
//! ```

pub mod color;
pub mod symbols;
pub mod primitives;
pub mod live;
pub mod spinner;
pub mod box_panel;

pub use color::{Color, strip_ansi, color_enabled, is_tty};
pub use symbols::*;
pub use primitives::{
    success, fail, warn, info, step, note,
    artifact, header, section, section_end,
    progress_bar, term_w,
};
pub use live::LiveBlock;
pub use spinner::Spinner;
pub use box_panel::{box_panel, config_table, ConfigEntry, ConfigValue, traceback, Frame, CodeLine};
