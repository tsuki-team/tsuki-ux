//! tsuki-ux Rust demo — all primitives in action.
//! Run: cargo run --example demo

use std::thread;
use std::time::Duration;

use tsuki_ux::{
    success, fail, warn, info, step, note,
    artifact, header, section, section_end, progress_bar,
    LiveBlock, Spinner,
    box_panel, config_table, ConfigEntry, ConfigValue,
    traceback, Frame, CodeLine,
};

fn main() {
    header("tsuki-ux demo");

    // ── Status primitives ─────────────────────────────────────────────────────
    step("Output primitives");
    success("compilación terminada");
    fail("error: archivo no encontrado");
    warn("versión antigua detectada");
    info("usando caché local");
    note("timestamp: 2026-03-21T10:00:00Z");

    // ── Section ───────────────────────────────────────────────────────────────
    section("Platform: linux-amd64");
    artifact("tsuki-linux-amd64.tar.gz", Some("4.2 MB"));
    artifact("tsuki-flash-linux-amd64",  Some("2.1 MB"));
    section_end();

    // ── Progress bar ──────────────────────────────────────────────────────────
    step("Progress bar");
    for i in (0..=40usize).step_by(8) {
        print!("\x1b[1A\x1b[K");
        progress_bar("compiling", i, 40, 40);
        thread::sleep(Duration::from_millis(120));
    }

    // ── Spinner ───────────────────────────────────────────────────────────────
    step("Spinner (standalone)");
    let mut s = Spinner::new("Detectando puerto serie…");
    s.start();
    thread::sleep(Duration::from_millis(1500));
    s.stop(true, Some("Puerto detectado: /dev/ttyUSB0"));

    // ── LiveBlock — success ───────────────────────────────────────────────────
    step("LiveBlock — éxito (colapsa)");
    let mut b = LiveBlock::new("cargo build --release --target avr-atmega328p");
    b.start();
    for l in &[
        "   Compiling proc-macro2 v1.0.94",
        "   Compiling quote v1.0.40",
        "   Compiling syn v2.0.100",
        "   Compiling tsuki-flash v4.0.0",
        "    Finished release [optimized] target(s) in 3.24s",
    ] {
        b.line(l);
        thread::sleep(Duration::from_millis(180));
    }
    b.finish(true, None);

    // ── LiveBlock — failure ───────────────────────────────────────────────────
    step("LiveBlock — fallo (expande)");
    let mut b = LiveBlock::new("avrdude -p atmega328p -c arduino -P /dev/ttyUSB0");
    b.start();
    b.line("avrdude: ser_open(): can't open device \"/dev/ttyUSB0\"");
    b.line("avrdude: serial port open: No such file or directory");
    thread::sleep(Duration::from_millis(400));
    b.finish(false, Some("exit 1"));

    // ── Box / panel ───────────────────────────────────────────────────────────
    step("Box / Panel");
    box_panel(
        "board      =  \"arduino-nano\"\nport       =  \"/dev/ttyUSB0\"\nbaud_rate  =  115200",
        Some("tsuki config"),
    );

    // ── Config table ──────────────────────────────────────────────────────────
    step("Config table");
    config_table("tsuki.json", &[
        ConfigEntry { key: "board".into(),      value: ConfigValue::Str("arduino-nano".into()), comment: None },
        ConfigEntry { key: "port".into(),        value: ConfigValue::Str("/dev/ttyUSB0".into()),  comment: None },
        ConfigEntry { key: "baud_rate".into(),   value: ConfigValue::Int(115200),                comment: Some("velocidad serie".into()) },
        ConfigEntry { key: "flash_mode".into(),  value: ConfigValue::Str("tsuki-flash".into()),  comment: None },
        ConfigEntry { key: "verbose".into(),     value: ConfigValue::Bool(false),                comment: None },
    ]);

    // ── Rich traceback ────────────────────────────────────────────────────────
    step("Rich traceback");
    traceback(
        "ZeroDivisionError",
        "division by zero",
        &[Frame {
            file: "main.go".into(),
            line: 21,
            func: "divide_all".into(),
            code: vec![
                CodeLine { number: 19, text: "for n, d in divides:".into(),        is_pointer: false },
                CodeLine { number: 20, text: "    result = divide_by(n, d)".into(), is_pointer: false },
                CodeLine { number: 21, text: "    result = divide_by(n, d)".into(), is_pointer: true  },
                CodeLine { number: 22, text: "    print(n, d, result)".into(),      is_pointer: false },
            ],
            locals: vec![
                ("divides".into(), "[(1000, 200), ...]".into()),
                ("divisor".into(), "0".into()),
            ],
        }],
    );

    println!();
    success("Demo completo");
}
