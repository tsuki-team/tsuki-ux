###### _<div align="right"><sub>// terminal output. any language.</sub></div>_

<div align="center">

```
  ████████╗███████╗██╗   ██╗██╗  ██╗██╗      ██╗   ██╗██╗  ██╗
  ╚══██╔══╝██╔════╝██║   ██║██║ ██╔╝██║      ██║   ██║╚██╗██╔╝
     ██║   ███████╗██║   ██║█████╔╝ ██║      ██║   ██║ ╚███╔╝
     ██║   ╚════██║██║   ██║██╔═██╗ ██║      ██║   ██║ ██╔██╗
     ██║   ███████║╚██████╔╝██║  ██╗██║      ╚██████╔╝██╔╝ ██╗
     ╚═╝   ╚══════╝ ╚═════╝ ╚═╝  ╚═╝╚═╝       ╚═════╝ ╚═╝  ╚═╝
```

[![Python](https://img.shields.io/badge/Python-3.9+-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Go](https://img.shields.io/badge/Go-1.21+-00ADD8?style=for-the-badge&logo=go&logoColor=white)](https://go.dev)
[![Rust](https://img.shields.io/badge/Rust-1.70+-orange?style=for-the-badge&logo=rust&logoColor=white)](https://rust-lang.org)
[![License](https://img.shields.io/badge/License-MIT-CCA9DD?style=for-the-badge)](./LICENSE)

<br>

<a href="#output-primitives"><kbd> <br> Primitivas <br> </kbd></a>&ensp;
<a href="#liveblock"><kbd> <br> LiveBlock <br> </kbd></a>&ensp;
<a href="#box--panel"><kbd> <br> Box / Panel <br> </kbd></a>&ensp;
<a href="#spinner"><kbd> <br> Spinner <br> </kbd></a>&ensp;
<a href="#python"><kbd> <br> Python <br> </kbd></a>&ensp;
<a href="#go"><kbd> <br> Go <br> </kbd></a>&ensp;
<a href="#rust"><kbd> <br> Rust <br> </kbd></a>

</div>

<br>

**tsuki-ux** es la librería de output de terminal extraída del proyecto Tsuki.  
Porta fielmente el sistema de UI de `cli/internal/ui/ui.go` y `tools/build.py` a Python, Go y Rust:
spinners braille, LiveBlocks colapsables estilo Docker, cajas redondeadas, primitivas semánticas y detección automática de TTY/Unicode/color.

---

## Output Primitives

```
  ✔  compilación terminada
  ✖  error: archivo no encontrado
  ⚠  advertencia: versión antigua
  ●  info: usando caché
  ▶  Compilando firmware…
```

| Función | Símbolo | Color |
|---------|---------|-------|
| `success(msg)` | `✔` | verde |
| `fail(msg)` | `✖` | rojo |
| `warn(msg)` | `⚠` | amarillo |
| `info(msg)` | `●` | azul |
| `step(msg)` | `▶` | cian/bold |
| `note(msg)` | dim | gris |

---

## LiveBlock

Docker-style: el bloque se muestra animado durante la ejecución y **colapsa en una sola línea** al terminar con éxito, o **se expande** mostrando toda la salida en caso de error.

```
  ⠹  cargo build --release                     ← animado mientras corre

  ✔  cargo build --release  [3.2s]             ← colapsado en éxito

  ✖  cargo build --release                     ← expandido en error
  │  error[E0382]: use of moved value
  │  --> src/main.rs:42:5
  ╰─ exit 1
```

---

## Box / Panel

```
╭── tsuki config ─────────────────────────────────────────────────────────╮
│  board      =  "arduino-nano"                                           │
│  port       =  "/dev/ttyUSB0"                                           │
│  baud_rate  =  115200                    # velocidad serie              │
╰─────────────────────────────────────────────────────────────────────────╯
```

---

## Spinner

Braille independiente del LiveBlock, para tareas sin salida de líneas:

```
  ⠋  Detectando puerto serie…   →   ✔  Puerto detectado: /dev/ttyUSB0
```

---

<a id="python"></a>
## Python

```bash
pip install tsuki-ux
# o desde fuente:
cd python && pip install -e .
```

```python
from tsuki_ux import success, fail, warn, info, step, note
from tsuki_ux import LiveBlock, Spinner, box, section, run

step("Compilando firmware")

with LiveBlock("cargo build --release") as b:
    b.line("Compilando main.rs...")
    b.line("Enlazando...")

success("Firmware listo")
```

→ [`python/README.md`](python/README.md)

---

<a id="go"></a>
## Go

```bash
go get github.com/tsuki/tsuki-ux/go/tsukiux
```

```go
import "github.com/tsuki/tsuki-ux/go/tsukiux"

ui.Step("Compilando firmware")

b := ui.NewLiveBlock("cargo build --release")
b.Start()
b.Line("Compilando main.rs...")
b.Finish(true, "")

ui.Success("Firmware listo")
```

→ [`go/README.md`](go/README.md)

---

<a id="rust"></a>
## Rust

```toml
[dependencies]
tsuki-ux = "0.1"
```

```rust
use tsuki_ux::{step, success, LiveBlock};

step("Compilando firmware");

let mut b = LiveBlock::new("cargo build --release");
b.start();
b.line("Compilando main.rs...");
b.finish(true, None);

success("Firmware listo");
```

→ [`rust/README.md`](rust/README.md)

---

## Comportamiento adaptativo

| Entorno | Comportamiento |
|---------|---------------|
| TTY + Unicode + color | Experiencia completa: spinner animado, colores, símbolos braille y box-drawing |
| TTY sin color (`NO_COLOR`, `TERM=dumb`) | Símbolos y estructura, sin ANSI |
| Pipe / CI / no-TTY | Sin animaciones, output línea a línea para captura de logs |
| Windows (consola antigua) | Fallback ASCII (`+`, `x`, `!`, `-`) |
| Windows (Terminal moderno / UTF-8) | Experiencia completa |

---

## License

MIT
