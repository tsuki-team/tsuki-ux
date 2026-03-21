//! Bordered panels, config tables, and rich tracebacks.
//! Port of ui.go's Box(), PrintConfig() and Traceback().

use crate::color::{
    strip_ansi, ansi,
    C_TITLE, C_KEY, C_VALUE, C_STRING, C_NUMBER, C_BOOL, C_NULL, C_COMMENT, C_MUTED,
    C_TB_BORDER, C_TB_TITLE, C_TB_FILE, C_TB_LINE_C, C_TB_FUNC,
    C_TB_CODE, C_TB_HIGH, C_TB_LOCALS, C_TB_ERRTYPE, C_TB_ERRMSG,
    DIM, RESET,
};
use crate::symbols::{box_tl, box_tr, box_bl, box_br, box_h, box_v, sym_ptr};
use crate::primitives::term_w;

fn hline(n: usize) -> String { box_h().repeat(n) }

fn visible_len(s: &str) -> usize { strip_ansi(s).chars().count() }

// ── Generic box ───────────────────────────────────────────────────────────────

/// Draw a bordered panel.
///
/// ```text
/// ╭── Title ──────────────────────────────────╮
/// │  content line 1                           │
/// ╰───────────────────────────────────────────╯
/// ```
pub fn box_panel(content: &str, title: Option<&str>) {
    let w     = term_w();
    let inner = w.saturating_sub(2);

    // top border
    if let Some(t) = title {
        let ts     = format!(" {} ", t);
        let dashes = inner.saturating_sub(ts.chars().count() + 2);
        let left   = dashes / 2;
        let right  = dashes - left;
        println!(
            "{}{}{}",
            C_TB_BORDER.paint(&format!("{}{}", box_tl(), hline(left))),
            C_TITLE.paint(&ts),
            C_TB_BORDER.paint(&format!("{}{}", hline(right), box_tr())),
        );
    } else {
        println!("{}", C_TB_BORDER.paint(&format!("{}{}{}", box_tl(), hline(inner), box_tr())));
    }

    // content lines
    for line in content.split('\n') {
        let vis = visible_len(line);
        let pad = inner.saturating_sub(vis + 1);
        println!(
            "{} {}{} {}",
            C_TB_BORDER.paint(box_v()),
            line, " ".repeat(pad),
            C_TB_BORDER.paint(box_v()),
        );
    }

    // bottom border
    println!("{}", C_TB_BORDER.paint(&format!("{}{}{}", box_bl(), hline(inner), box_br())));
}

// ── Config table ──────────────────────────────────────────────────────────────

/// Config value for typed rendering.
pub enum ConfigValue {
    Str(String),
    Int(i64),
    Float(f64),
    Bool(bool),
    Null,
    List(Vec<ConfigValue>),
}

impl ConfigValue {
    fn rich(&self) -> String {
        match self {
            Self::Str(s)   => C_STRING.paint(&format!("\"{}\"", s)),
            Self::Int(n)   => C_NUMBER.paint(&n.to_string()),
            Self::Float(f) => C_NUMBER.paint(&format!("{}", f)),
            Self::Bool(b)  => C_BOOL.paint(&b.to_string()),
            Self::Null     => C_NULL.paint("null"),
            Self::List(v)  => {
                if v.is_empty() { return C_NULL.paint("[]"); }
                format!("[{}]", v.iter().map(|x| x.rich()).collect::<Vec<_>>().join(", "))
            }
        }
    }
    fn plain(&self) -> String {
        match self {
            Self::Str(s)   => format!("\"{}\"", s),
            Self::Int(n)   => n.to_string(),
            Self::Float(f) => f.to_string(),
            Self::Bool(b)  => b.to_string(),
            Self::Null     => "null".into(),
            Self::List(v)  => format!("[{}]", v.iter().map(|x| x.plain()).collect::<Vec<_>>().join(", ")),
        }
    }
}

/// One key/value row in a config table.
pub struct ConfigEntry {
    pub key:     String,
    pub value:   ConfigValue,
    pub comment: Option<String>,
}

/// Render a styled config table.
///
/// ```text
/// ╭── title ─────────────────────────────────────────────────╮
/// │  board      =  "arduino-nano"                            │
/// │  baud_rate  =  115200            # velocidad serie       │
/// ╰──────────────────────────────────────────────────────────╯
/// ```
pub fn config_table(title: &str, entries: &[ConfigEntry]) {
    let key_w = entries.iter().map(|e| e.key.len()).max().unwrap_or(0);

    let rows: Vec<(String, String)> = entries.iter().map(|e| {
        let key_r  = C_KEY.paint(&format!("{:<w$}", e.key, w = key_w));
        let sep_r  = format!("{}  =  {}", ansi(DIM), ansi(RESET));
        let val_r  = e.value.rich();
        let mut rich  = format!("{}{}{}", key_r, sep_r, val_r);
        let mut plain = format!("{:<w$}  =  {}", e.key, e.value.plain(), w = key_w);
        if let Some(c) = &e.comment {
            let s = format!("  # {}", c);
            rich.push_str(&C_COMMENT.paint(&s));
            plain.push_str(&s);
        }
        (rich, plain)
    }).collect();

    let w       = term_w();
    let mut inner = w.saturating_sub(2);
    let min_i   = rows.iter().map(|(_, p)| p.len() + 2).max().unwrap_or(0)
                      .max(title.len() + 6);
    if min_i > inner { inner = min_i; }

    // header
    let ts       = format!(" {} ", title);
    let pad_r    = inner.saturating_sub(ts.len() + 2);
    println!(
        "{}{}{}",
        C_TB_BORDER.paint(&format!("{}{}{}", box_tl(), hline(2), "")),
        C_TITLE.paint(&ts),
        C_TB_BORDER.paint(&format!("{}{}", hline(pad_r), box_tr())),
    );

    for (rich, plain) in &rows {
        let pad = inner.saturating_sub(plain.len() + 1);
        println!(
            "{} {}{} {}",
            C_TB_BORDER.paint(box_v()),
            rich, " ".repeat(pad),
            C_TB_BORDER.paint(box_v()),
        );
    }

    println!("{}", C_TB_BORDER.paint(&format!("{}{}{}", box_bl(), hline(inner), box_br())));
}

// ── Rich traceback ─────────────────────────────────────────────────────────────

/// One source line in a frame's context.
pub struct CodeLine {
    pub number:     usize,
    pub text:       String,
    pub is_pointer: bool,
}

/// One stack frame in a traceback.
pub struct Frame {
    pub file:   String,
    pub line:   usize,
    pub func:   String,
    pub code:   Vec<CodeLine>,
    pub locals: Vec<(String, String)>,
}

/// Render a rich-style traceback.
///
/// ```text
/// ╭─── Traceback (most recent call last) ──────────────────────╮
/// │  main.go:21 in divide_all                                  │
/// │                                                            │
/// │   20 │   result = divide_by(n, d)                         │
/// │ ❱ 21 │   result = divide_by(n, d)                         │
/// ╰────────────────────────────────────────────────────────────╯
/// ZeroDivisionError: division by zero
/// ```
pub fn traceback(err_type: &str, err_msg: &str, frames: &[Frame]) {
    let w     = term_w();
    let inner = w.saturating_sub(2);

    let emit = |text: &str| {
        let vis = visible_len(text);
        let pad = inner.saturating_sub(vis + 1);
        println!(
            "{} {}{} {}",
            C_TB_BORDER.paint(box_v()),
            text, " ".repeat(pad),
            C_TB_BORDER.paint(box_v()),
        );
    };
    let empty = || {
        println!(
            "{}{}{}",
            C_TB_BORDER.paint(box_v()),
            " ".repeat(inner),
            C_TB_BORDER.paint(box_v()),
        );
    };

    // header
    let hdr   = " Traceback (most recent call last) ";
    let right = inner.saturating_sub(hdr.len() + 3);
    println!(
        "{}{}{}",
        C_TB_BORDER.paint(&format!("{}{}", box_tl(), hline(3))),
        C_TB_TITLE.paint(hdr),
        C_TB_BORDER.paint(&format!("{}{}", hline(right), box_tr())),
    );

    for frame in frames {
        let loc = format!(
            "{}:{} in {}",
            C_TB_FILE.paint(&frame.file),
            C_TB_LINE_C.paint(&frame.line.to_string()),
            C_TB_FUNC.paint(&frame.func),
        );
        emit(&loc);
        empty();

        let sep = C_TB_BORDER.paint(&format!(" {} ", box_v()));
        for cl in &frame.code {
            let num = format!("{:4}", cl.number);
            if cl.is_pointer {
                emit(&format!(
                    "{} {}{}{}",
                    C_TB_HIGH.paint(&format!(" {} ", sym_ptr())),
                    C_TB_HIGH.paint(&num),
                    sep,
                    C_TB_HIGH.paint(&cl.text),
                ));
            } else {
                emit(&format!(
                    "   {}{}{}",
                    C_MUTED.paint(&num),
                    sep,
                    C_TB_CODE.paint(&cl.text),
                ));
            }
        }

        if !frame.locals.is_empty() {
            empty();
            let loc_hdr = format!(
                "{} {}",
                C_TB_LOCALS.paint(" locals "),
                C_TB_BORDER.paint(&hline(inner.saturating_sub(12))),
            );
            emit(&loc_hdr);
            for (k, v) in &frame.locals {
                emit(&format!(
                    "{}  {} = {}",
                    C_TB_BORDER.paint(box_v()),
                    C_KEY.paint(k),
                    C_VALUE.paint(v),
                ));
            }
        }
        empty();
    }

    println!("{}", C_TB_BORDER.paint(&format!("{}{}{}", box_bl(), hline(inner), box_br())));
    println!("{}: {}", C_TB_ERRTYPE.paint(err_type), C_TB_ERRMSG.paint(err_msg));
}
