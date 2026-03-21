# tsuki-ux · Python

Terminal UX library faithful to the Tsuki project.  
Port of `cli/internal/ui/ui.go` and `tools/build.py`.

## Install

```bash
pip install tsuki-ux
# or from source:
pip install -e .
```

## API

### Status primitives

```python
from tsuki_ux import success, fail, warn, info, step, note

step("Compilando firmware")       #   ▶  Compilando firmware
success("Hecho")                  #   ✔  Hecho
fail("Algo salió mal")            #   ✖  Algo salió mal  (stderr)
warn("Versión desactualizada")    #   ⚠  Versión desactualizada
info("Usando caché")              #   ●  Usando caché
note("timestamp: 2026-03-21")    #   ●  timestamp: 2026-03-21  (dim)
```

### LiveBlock

```python
from tsuki_ux import LiveBlock

# Context manager
with LiveBlock("cargo build --release") as b:
    b.line("Compiling main.rs...")
    b.line("Linking...")

# Manual
b = LiveBlock("npm install")
b.start()
b.line("added 312 packages")
b.finish(ok=True)
b.finish(ok=False, summary="exit 1")   # expands with all lines
```

### Spinner

```python
from tsuki_ux import Spinner
import time

s = Spinner("Detectando puerto…")
s.start()
time.sleep(1.5)
s.stop(ok=True, msg="Puerto: /dev/ttyUSB0")
```

### Box / Panel

```python
from tsuki_ux import box, config_table, ConfigEntry

box("línea 1\nlínea 2", title="Estado")

config_table("tsuki.json", [
    ConfigEntry("board",     "arduino-nano"),
    ConfigEntry("baud_rate", 115200, comment="velocidad serie"),
    ConfigEntry("verbose",   False),
])
```

### run() — subprocess inside a LiveBlock

```python
from tsuki_ux import run

run(["cargo", "build", "--release"])
run(["npm", "install"], cwd="./frontend", label="npm install")
```

### Rich traceback

```python
from tsuki_ux import traceback_box, Frame, CodeLine

traceback_box(
    err_type="RuntimeError",
    err_msg="buffer overflow",
    frames=[
        Frame(
            file="main.go", line=42, func="read_sensor",
            code=[
                CodeLine(41, "buf := make([]byte, 4)"),
                CodeLine(42, "n, _ = port.Read(buf)", is_pointer=True),
            ],
            locals={"buf": "[0 0 0 0]", "n": "8"},
        )
    ],
)
```

## Adaptive behavior

| Environment | Output |
|-------------|--------|
| TTY + color | Full animation, ANSI colors, braille spinner, box-drawing |
| `NO_COLOR` / `TERM=dumb` | Symbols + structure, no ANSI |
| Pipe / CI | No animation, line-by-line for log capture |
| Windows (old console) | ASCII fallback (`+`, `x`, `!`, `-`) |
| Windows Terminal / UTF-8 | Full experience |
