//! **tsuki-ux** — Terminal UX primitives faithful to the Tsuki project.
//!
//! Zero external dependencies.

pub mod color;
pub mod symbols;
pub mod primitives;
pub mod live;
pub mod spinner;
pub mod box_panel;

pub use color::{
    Color, Style, strip_ansi, color_enabled, is_tty, ansi,
    // color constants
    C_SUCCESS, C_ERROR, C_WARN, C_INFO, C_STEP, C_TITLE,
    C_MUTED, C_HIGHLIGHT, C_ACCENT,
    C_KEY, C_VALUE, C_STRING, C_NUMBER, C_BOOL, C_NULL, C_COMMENT,
    C_TB_BORDER, C_TB_TITLE, C_TB_FILE, C_TB_LINE_C, C_TB_FUNC,
    C_TB_CODE, C_TB_HIGH, C_TB_LOCALS, C_TB_ERRTYPE, C_TB_ERRMSG,
    // text decoration helpers
    underline, strike, overline, blink, reverse, bold, dim, italic,
    // 256-color and truecolor helpers
    color256, bg_color256, truecolor, bg_truecolor,
    // raw codes
    RESET, BOLD, DIM, ITALIC, UNDERLINE, BLINK, REVERSE, STRIKE, OVERLINE,
};
pub use symbols::{
    unicode_enabled,
    sym_ok, sym_fail, sym_warn, sym_info, sym_step,
    sym_bullet, sym_pipe, sym_ell, sym_ptr, sym_arrow, sym_check, sym_cross,
    box_tl, box_tr, box_bl, box_br, box_h, box_v,
    // Spinner frame sets
    spinner_frames, spinner_frames_dots, spinner_frames_line,
    spinner_frames_arrow, spinner_frames_moon, spinner_frames_clock,
    spinner_frames_bounce, spinner_frames_pulse, spinner_frames_snake,
    spinner_frames_pixel, spinner_frames_toggle, spinner_frames_grow,
};
pub use primitives::{
    term_w,
    // status
    success, fail, warn, info, step, note, artifact,
    // header/section
    header, section, section_end,
    // layout
    rule, separator, blank,
    // inline content
    badge, badge_line, key_value,
    list, numbered_list, check_list,
    indent, highlight, accent,
    // timer
    Timer,
    // table + diff
    Align, TableColumn, table,
    DiffKind, DiffLine, diff_view,
    // progress bars
    progress_bar, progress_bar_thin, progress_bar_braille,
    progress_bar_dots, progress_bar_slim, progress_bar_gradient,
    progress_bar_arrow, progress_bar_steps, progress_bar_squares,
};
pub use live::LiveBlock;
pub use spinner::Spinner;
pub use box_panel::{box_panel, config_table, ConfigEntry, ConfigValue, traceback, Frame, CodeLine};