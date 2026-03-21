# tsuki-ux · Rust

Terminal UX library faithful to the Tsuki project.  
Port of `cli/internal/ui/ui.go` and `tools/build.py`. No external crates.

## Install

```toml
[dependencies]
tsuki-ux = "0.1"
```

## API

### Status primitives

```rust
use tsuki_ux::{step, success, fail, warn, info, note};

step("Compilando firmware");      //   ▶  Compilando firmware
success("Hecho");                 //   ✔  Hecho
fail("Algo salió mal");           //   ✖  Algo salió mal  (stderr)
warn("Versión antigua");          //   ⚠  Versión antigua
info("Usando caché");             //   ●  Usando caché
note("timestamp: 2026-03-21");   //   ●  timestamp…  (dim)
```

### LiveBlock

```rust
use tsuki_ux::LiveBlock;

let mut b = LiveBlock::new("cargo build --release");
b.start();
b.line("Compiling main.rs...");
b.line("Linking...");
b.finish(true, None);           // ✔ collapses
b.finish(false, Some("exit 1")); // ✖ expands with all lines
```

### Spinner

```rust
use tsuki_ux::Spinner;
use std::time::Duration;

let mut s = Spinner::new("Detectando puerto…");
s.start();
std::thread::sleep(Duration::from_millis(1500));
s.stop(true, Some("Puerto: /dev/ttyUSB0"));
```

### Box / Panel

```rust
use tsuki_ux::{box_panel, config_table, ConfigEntry, ConfigValue};

box_panel("board = \"nano\"\nbaud = 115200", Some("tsuki config"));

config_table("tsuki.json", &[
    ConfigEntry { key: "board".into(),     value: ConfigValue::Str("arduino-nano".into()), comment: None },
    ConfigEntry { key: "baud_rate".into(), value: ConfigValue::Int(115200), comment: Some("velocidad serie".into()) },
    ConfigEntry { key: "verbose".into(),   value: ConfigValue::Bool(false), comment: None },
]);
```

### Run the demo

```bash
cargo run --example demo
```
