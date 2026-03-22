//! tsuki-ux Rust demo
//!
//! Normal mode:       cargo run --example demo
//! Presentation mode: cargo run --example demo -- --presentation
//!
//! Presentation mode is designed to be recorded as a GIF.
//! Recommended recorder: vhs (https://github.com/charmbracelet/vhs)
//!
//!   Output demo.gif
//!   Set FontSize 14
//!   Set Width 900
//!   Set Height 600
//!   Type "cargo run --example demo -- --presentation"
//!   Enter
//!   Sleep 60s

use std::thread;
use std::time::Duration;

use tsuki_ux::{
    success, fail, warn, info, step, note, artifact, header, section, section_end,
    rule, separator, blank, badge_line, key_value, check_list, indent, highlight, accent,
    Timer,
    Align, TableColumn, table, DiffKind, DiffLine, diff_view,
    progress_bar, progress_bar_thin, progress_bar_braille, progress_bar_dots,
    progress_bar_slim, progress_bar_gradient, progress_bar_arrow,
    progress_bar_steps, progress_bar_squares,
    bold, dim, italic, underline, strike, overline, blink, reverse,
    color256, truecolor,
    Style, C_SUCCESS, C_INFO, C_MUTED,
    spinner_frames, spinner_frames_arrow, spinner_frames_moon, spinner_frames_bounce,
    spinner_frames_pulse, spinner_frames_snake, spinner_frames_grow, spinner_frames_toggle,
    LiveBlock, Spinner,
    box_panel, config_table, ConfigEntry, ConfigValue, traceback, Frame, CodeLine,
    ansi, DIM, RESET,
};

fn pause(ms: u64) { thread::sleep(Duration::from_millis(ms)); }

fn clear_screen() { print!("\x1b[2J\x1b[H"); }

fn pres_title(title: &str) {
    clear_screen();
    let w: usize = 60;
    let bar = "─".repeat(w - 2);
    let label = format!("  🌙 tsuki-ux  ·  {}", title);
    // 🌙 is 1 char but 2 terminal columns wide — subtract 1 extra
    let label_chars = label.chars().count();
    let pad = w.saturating_sub(label_chars + 1 + 1); // +1 for emoji width
    println!();
    println!("  \x1b[2m╭{}╮\x1b[0m", bar);
    println!("  \x1b[2m│\x1b[0m\x1b[1;97m{}{}\x1b[2m│\x1b[0m", label, " ".repeat(pad));
    println!("  \x1b[2m╰{}╯\x1b[0m", bar);
    println!();
    pause(500);
}

// ── Full demo ─────────────────────────────────────────────────────────────────

fn run_full() {
    header("tsuki-ux demo");

    step("Status primitives");
    success("compilación terminada");
    fail("error: archivo no encontrado");
    warn("versión antigua detectada");
    info("usando caché local");
    note("timestamp: 2026-03-21T10:00:00Z");

    step("Layout");
    rule("plataformas soportadas");
    section("Platform: linux-amd64");
    artifact("tsuki-linux-amd64.tar.gz", Some("4.2 MB"));
    artifact("tsuki-flash-linux-amd64", Some("2.1 MB"));
    section_end();

    step("Inline content");
    badge_line("GO",  "info",      "transpilando firmware");
    badge_line("OK",  "success",   "compilación exitosa");
    badge_line("ERR", "error",     "puerto serie ocupado");
    badge_line("⚡",  "highlight", "tsuki-flash activo");
    blank();
    key_value("board", "arduino-nano");
    key_value("baud",  "115200");
    blank();
    check_list(
        &["go.mod configurado", "paquetes instalados", "board detectada", "puerto disponible"],
        &[true, true, true, false],
    );
    blank();
    indent("avrdude: AVR device initialized\navrdude: verifying flash memory");

    step("Text decoration & color");
    println!("  {}  {}  {}", bold("Negrita"), dim("Tenue"), italic("Cursiva"));
    println!("  {}  {}  {}", underline("Subrayado"), strike("Tachado"), overline("Sobrelineado"));
    println!("  {}  {}", reverse("Invertido"), blink("Parpadeo"));
    blank();
    print!("  256-color: ");
    for n in [196u8, 214, 226, 46, 51, 57, 201] { print!("{}  ", color256(n, "█")); }
    println!();
    print!("  truecolor: ");
    for (r,g,b) in [(255u8,80,80),(255,165,0),(255,255,80),(80,255,80),(80,200,255),(160,80,255)] {
        print!("{}  ", truecolor(r,g,b,"█"));
    }
    println!();
    blank();
    println!("  {}", Style::new().bold().underline().fg(C_SUCCESS).paint("bold + underline + success"));
    println!("  {}", Style::new().strike().fg_rgb(200, 80, 80).paint("strike + truecolor"));
    println!("  {}", Style::new().italic().fg_256(208).bg_256(234).paint("italic + 256-color bg"));
    println!("  {}", Style::new().bold().reverse().fg(C_INFO).paint("bold + reverse + info"));

    step("Progress bars");
    macro_rules! bar {
        ($name:expr, $fn:expr) => {{
            note($name);
            for i in (0..=40usize).step_by(8) {
                print!("\x1b[1A\x1b[K"); $fn(i); pause(50);
            }
        }};
    }
    bar!("Block    [████████░░░░]", |i| progress_bar("compilando", i, 40, 40));
    bar!("Braille  ⣿⣿⣿⣿⣦⣀⣀⣀",     |i| progress_bar_braille("compilando", i, 40, 20));
    bar!("Gradient [████▓▒░   ]",   |i| progress_bar_gradient("compilando", i, 40, 40));
    bar!("Slim     ▰▰▰▰▰▰▱▱▱▱",     |i| progress_bar_slim("compilando", i, 40, 30));
    bar!("Arrow    [=======>--]",    |i| progress_bar_arrow("compilando", i, 40, 40));
    bar!("Dots     ●●●●●●●○○○",     |i| progress_bar_dots("compilando", i, 40, 30));
    bar!("Squares  ▪▪▪▪▪▫▫▫▫▫",    |i| progress_bar_squares("compilando", i, 40, 30));
    bar!("Steps    [■■■□□□□□]",     |i| progress_bar_steps("compilando", i/5, 8));

    step("Spinners");
    let effects: &[(&str, &[&str])] = &[
        ("Braille", spinner_frames()),        ("Arrow",  spinner_frames_arrow()),
        ("Moon",    spinner_frames_moon()),    ("Bounce", spinner_frames_bounce()),
        ("Pulse",   spinner_frames_pulse()),   ("Snake",  spinner_frames_snake()),
        ("Grow",    spinner_frames_grow()),    ("Toggle", spinner_frames_toggle()),
    ];
    for (label, frames) in effects {
        let mut s = Spinner::with_frames(label, frames);
        s.start(); pause(700); s.stop(true, None);
    }

    step("LiveBlock — éxito");
    let mut b = LiveBlock::new("cargo build --release --target avr-atmega328p");
    b.start();
    for l in &["   Compiling proc-macro2 v1.0.94", "   Compiling tsuki-flash v4.0.0",
               "    Finished release [optimized] in 3.24s"] {
        b.line(l); pause(180);
    }
    b.finish(true, None);

    step("LiveBlock — fallo");
    let mut b = LiveBlock::new("avrdude -p atmega328p -P /dev/ttyUSB0");
    b.start();
    b.line("avrdude: can't open \"/dev/ttyUSB0\""); pause(400);
    b.finish(false, Some("exit 1"));

    step("Table");
    table("boards detectadas", &[
        TableColumn { header: "Board",  align: Align::Left },
        TableColumn { header: "MCU",    align: Align::Left },
        TableColumn { header: "Puerto", align: Align::Left },
        TableColumn { header: "Baud",   align: Align::Right },
    ], &[
        vec!["arduino-nano",  "ATmega328P", "/dev/ttyUSB0", "115200"],
        vec!["arduino-uno",   "ATmega328P", "/dev/ttyUSB1", "115200"],
        vec!["esp32-devkit",  "ESP32",      "/dev/ttyUSB2", "921600"],
    ]);

    step("Config table");
    config_table("tsuki.json", &[
        ConfigEntry { key: "board".into(),      value: ConfigValue::Str("arduino-nano".into()), comment: None },
        ConfigEntry { key: "baud_rate".into(),  value: ConfigValue::Int(115200), comment: Some("velocidad serie".into()) },
        ConfigEntry { key: "flash_mode".into(), value: ConfigValue::Str("tsuki-flash".into()), comment: None },
        ConfigEntry { key: "verbose".into(),    value: ConfigValue::Bool(false), comment: None },
    ]);

    step("DiffView");
    diff_view("src/main.go", 8, &[
        DiffLine { kind: DiffKind::Context, text: r#"import "arduino""#.into() },
        DiffLine { kind: DiffKind::Removed, text: "var LED_PIN int = 12".into() },
        DiffLine { kind: DiffKind::Added,   text: "var LED_PIN int = 13".into() },
        DiffLine { kind: DiffKind::Context, text: "func setup() {".into() },
        DiffLine { kind: DiffKind::Removed, text: "    arduino.PinMode(LED_PIN, arduino.INPUT)".into() },
        DiffLine { kind: DiffKind::Added,   text: "    arduino.PinMode(LED_PIN, arduino.OUTPUT)".into() },
        DiffLine { kind: DiffKind::Context, text: "}".into() },
    ]);

    step("Traceback");
    traceback("RuntimeError", "buffer overflow", &[Frame {
        file: "main.go".into(), line: 42, func: "read_sensor".into(),
        code: vec![
            CodeLine { number: 41, text: "buf := make([]byte, 4)".into(), is_pointer: false },
            CodeLine { number: 42, text: "n, _ = port.Read(buf)".into(),  is_pointer: true  },
        ],
        locals: vec![("buf".into(), "[0 0 0 0]".into()), ("n".into(), "8".into())],
    }]);

    println!();
    success("Demo completo");
}

// ── Presentation mode ─────────────────────────────────────────────────────────

fn run_presentation() {
    use std::io::Write;

    // 1 — Status
    pres_title("status primitives");
    for (f, ms) in &[
        (success as fn(&str), 220u64),
    ] { let _ = (f, ms); } // type anchor
    let items: &[(&str, fn(&str))] = &[
        ("compilación terminada",           success),
        ("error: archivo no encontrado",    fail),
        ("versión antigua detectada",       warn),
        ("usando caché local",              info),
    ];
    // Manual dispatch to avoid closure capture issues
    success("compilación terminada");   pause(220);
    fail("error: archivo no encontrado"); pause(220);
    warn("versión antigua detectada");  pause(220);
    info("usando caché local");         pause(220);
    note("timestamp: 2026-03-21T10:00:00Z"); pause(220);
    pause(1000);

    // 2 — Inline content
    pres_title("inline content");
    badge_line("GO",  "info",      "transpilando firmware");   pause(200);
    badge_line("OK",  "success",   "compilación exitosa");     pause(200);
    badge_line("ERR", "error",     "puerto serie ocupado");    pause(200);
    badge_line("⚡",  "highlight", "tsuki-flash activo");      pause(400);
    blank();
    key_value("board", "arduino-nano");
    key_value("port",  "/dev/ttyUSB0");
    key_value("baud",  "115200");
    pause(500);
    blank();
    check_list(
        &["go.mod configurado", "paquetes instalados", "board detectada", "puerto disponible"],
        &[true, true, true, false],
    );
    pause(1200);

    // 3 — Text styles
    pres_title("text decoration & color");
    let lines = [
        format!("  {}  {}  {}", bold("Negrita"), dim("Tenue"), italic("Cursiva")),
        format!("  {}  {}  {}", underline("Subrayado"), strike("Tachado"), overline("Sobrelineado")),
        format!("  {}", reverse("Invertido")),
    ];
    for s in &lines { println!("{}", s); pause(350); }
    blank();
    print!("  256-color: ");
    std::io::stdout().flush().ok();
    for n in [196u8, 214, 226, 46, 51, 57, 201] {
        print!("{}  ", color256(n, "█")); std::io::stdout().flush().ok(); pause(80);
    }
    println!();
    pause(200);
    print!("  truecolor: ");
    std::io::stdout().flush().ok();
    for (r,g,b) in [(255u8,80,80),(255,165,0),(255,255,80),(80,255,80),(80,200,255),(160,80,255)] {
        print!("{}  ", truecolor(r,g,b,"█")); std::io::stdout().flush().ok(); pause(80);
    }
    println!();
    pause(400);
    blank();
    let styled = [
        Style::new().bold().underline().fg(C_SUCCESS).paint("bold + underline + success"),
        Style::new().strike().fg_rgb(200,80,80).paint("strike + truecolor"),
        Style::new().italic().fg_256(208).bg_256(234).paint("italic + 256-color bg"),
        Style::new().bold().reverse().fg(C_INFO).paint("bold + reverse + info"),
    ];
    for s in &styled { println!("  {}", s); pause(250); }
    pause(1200);

    // 4 — Progress bars (fully animated)
    pres_title("progress bars");
    macro_rules! bar_anim {
        ($name:expr, $fn:expr) => {{
            note($name);
            for i in 0..=40usize {
                print!("\x1b[1A\x1b[K"); $fn(i); pause(35);
            }
            pause(400);
        }};
    }
    bar_anim!("Block    [████████░░░░]", |i| progress_bar("compilando", i, 40, 40));
    bar_anim!("Braille  ⣿⣿⣿⣿⣦⣀⣀⣀",     |i| progress_bar_braille("compilando", i, 40, 20));
    bar_anim!("Gradient [████▓▒░   ]",   |i| progress_bar_gradient("compilando", i, 40, 40));
    bar_anim!("Slim     ▰▰▰▰▰▰▱▱▱▱",     |i| progress_bar_slim("compilando", i, 40, 30));
    bar_anim!("Arrow    [=======>--]",    |i| progress_bar_arrow("compilando", i, 40, 40));
    bar_anim!("Dots     ●●●●●●●○○○",     |i| progress_bar_dots("compilando", i, 40, 30));

    // 5 — Spinners
    pres_title("spinners");
    let spinner_effects: &[(&str, &[&str])] = &[
        ("Braille  ⠋⠙⠹⠸⠼⠴",   spinner_frames()),
        ("Arrow    ▸▹▹▹▹",      spinner_frames_arrow()),
        ("Moon     🌑🌒🌓🌔",   spinner_frames_moon()),
        ("Bounce   [●    ]",     spinner_frames_bounce()),
        ("Pulse    ▏▎▍▌▋▊▉█",  spinner_frames_pulse()),
        ("Snake    ⣿⣿⣿⣿⣿",     spinner_frames_snake()),
        ("Grow     ▰▰▰▰▱▱▱▱",  spinner_frames_grow()),
    ];
    for (label, frames) in spinner_effects {
        let mut s = Spinner::with_frames(label, frames);
        s.start(); pause(1200); s.stop(true, None);
        pause(120);
    }
    pause(600);

    // 6 — LiveBlock
    pres_title("live block");
    pause(300);
    let mut b = LiveBlock::new("cargo build --release --target avr-atmega328p");
    b.start();
    for l in &[
        "   Compiling proc-macro2 v1.0.94",
        "   Compiling quote v1.0.40",
        "   Compiling syn v2.0.100",
        "   Compiling tsuki-flash v4.0.0",
        "    Finished release [optimized] target(s) in 3.24s",
    ] { b.line(l); pause(280); }
    b.finish(true, None);
    pause(500);
    let mut b = LiveBlock::new("avrdude -p atmega328p -c arduino -P /dev/ttyUSB0");
    b.start();
    b.line("avrdude: ser_open(): can't open device \"/dev/ttyUSB0\"");
    b.line("avrdude: serial port open: No such file or directory");
    pause(900);
    b.finish(false, Some("exit 1"));
    pause(1000);

    // 7 — Config + Box
    pres_title("config table  &  box");
    pause(300);
    config_table("tsuki.json", &[
        ConfigEntry { key: "board".into(),      value: ConfigValue::Str("arduino-nano".into()), comment: None },
        ConfigEntry { key: "port".into(),        value: ConfigValue::Str("/dev/ttyUSB0".into()), comment: None },
        ConfigEntry { key: "baud_rate".into(),   value: ConfigValue::Int(115200), comment: Some("velocidad serie".into()) },
        ConfigEntry { key: "flash_mode".into(),  value: ConfigValue::Str("tsuki-flash".into()), comment: None },
        ConfigEntry { key: "verbose".into(),     value: ConfigValue::Bool(false), comment: None },
    ]);
    pause(700);
    println!();
    box_panel("board   = \"nano\"\nbaud    = 115200\nbackend = tsuki-flash", Some("tsuki config"));
    pause(1500);

    // fin
    pres_title("fin");
    success("tsuki-ux  ·  github.com/tsuki-team/tsuki-ux");
    pause(2500);
}

// ── Recording helpers ─────────────────────────────────────────────────────────

fn which(bin: &str) -> bool {
    std::process::Command::new("which")
        .arg(bin)
        .stdout(std::process::Stdio::null())
        .stderr(std::process::Stdio::null())
        .status()
        .map(|s| s.success())
        .unwrap_or(false)
}

fn write_vhs_tape(tape: &str, gif: &str, self_path: &str) {
    let content = format!(
        "Output {gif}\nSet FontSize 14\nSet Width 100\nSet Height 40\n\
         Set Theme \"Catppuccin Mocha\"\nType \"{self_path} --presentation\"\n\
         Enter\nSleep 90s\n"
    );
    std::fs::write(tape, content).ok();
    println!("\n  \x1b[90mvhs tape written → {tape}\x1b[0m");
    println!("  \x1b[90mRun: vhs {tape}\x1b[0m\n");
}

/// Start recording and return the child process handle (if one was spawned).
/// Priority: asciinema → vhs tape → script (Unix fallback).
fn start_recording(out_file: &str) -> Option<std::process::Child> {
    let self_path = std::env::current_exe()
        .ok()
        .and_then(|p| p.to_str().map(|s| s.to_owned()))
        .unwrap_or_else(|| "demo".into());

    // 1 — asciinema
    if which("asciinema") {
        let child = std::process::Command::new("asciinema")
            .args(["rec", "--overwrite", out_file])
            .spawn()
            .ok();
        if child.is_some() {
            println!("\n  \x1b[90mRecording with asciinema → {out_file}\x1b[0m\n");
            return child;
        }
    }

    // 2 — vhs (writes tape, does not block)
    if which("vhs") {
        let stem = out_file.trim_end_matches(".cast");
        let tape = format!("{stem}.tape");
        let gif  = format!("{stem}.gif");
        write_vhs_tape(&tape, &gif, &self_path);
        return None;
    }

    // 3 — script (Unix)
    if which("script") {
        let child = std::process::Command::new("script")
            .args(["-q", "-c",
                   &format!("{self_path} --presentation"), out_file])
            .spawn()
            .ok();
        if child.is_some() {
            println!("\n  \x1b[90mRecording with script → {out_file}\x1b[0m\n");
            return child;
        }
    }

    eprintln!(
        "  \x1b[1;93m⚠\x1b[0m  No recorder found.\n\
         \x1b[90m     Install asciinema: https://asciinema.org/docs/installation\n\
              Or vhs:            https://github.com/charmbracelet/vhs\x1b[0m\n"
    );
    None
}

fn stop_recording(mut child: std::process::Child, out_file: &str) {
    // Send SIGINT to gracefully stop asciinema/script
    #[cfg(unix)]
    {
        use std::os::unix::process::CommandExt;
        unsafe { libc_kill(child.id() as i32, 2); } // SIGINT = 2
    }
    let _ = child.wait();
    println!("\n  \x1b[90mRecording saved → {out_file}\x1b[0m\n");
}

#[cfg(unix)]
extern "C" { fn kill(pid: i32, sig: i32) -> i32; }
#[cfg(unix)]
fn libc_kill(pid: i32, sig: i32) { unsafe { kill(pid, sig); } }
#[cfg(not(unix))]
fn libc_kill(_pid: i32, _sig: i32) {}

fn main() {
    let args: Vec<String> = std::env::args().collect();
    let is_presentation = args.iter().any(|a| a == "--presentation");
    let is_record       = args.iter().any(|a| a == "--record");

    let out_file = args.windows(2)
        .find(|w| w[0] == "--out")
        .map(|w| w[1].as_str())
        .unwrap_or("demo.cast")
        .to_owned();

    let rec_handle = if is_record || (!is_presentation && false) {
        // give the recorder a moment to attach before output starts
        let h = start_recording(&out_file);
        std::thread::sleep(Duration::from_millis(400));
        h
    } else {
        None
    };

    if is_presentation || is_record {
        run_presentation();
    } else {
        run_full();
    }

    if let Some(child) = rec_handle {
        stop_recording(child, &out_file);
    }
}