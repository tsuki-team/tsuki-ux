# tsuki-ux — Documentación

Terminal UX primitives para Python, Go y Rust, extraídas del proyecto Tsuki.
Sin dependencias externas — ANSI puro sobre stdlib.

---

## Índice

- [Instalación](#instalación)
- [Primitivas de output](#primitivas-de-output)
- [LiveBlock](#liveblock)
- [Spinner](#spinner)
- [Box / Panel](#box--panel)
- [Config table](#config-table)
- [Traceback](#traceback)
- [Progress bars](#progress-bars)
- [Color y estilos](#color-y-estilos)
- [Símbolos](#símbolos)
- [Comportamiento adaptativo](#comportamiento-adaptativo)
- [API Reference — Python](#api-reference--python)
- [API Reference — Go](#api-reference--go)
- [API Reference — Rust](#api-reference--rust)
- [Release workflow](#release-workflow)

---

## Instalación

### Python

```bash
pip install tsuki-ux
```

Desde fuente:

```bash
cd python && pip install -e .
```

Requiere Python 3.9+. Sin dependencias en runtime.

### Go

```bash
go get github.com/tsuki-team/tsuki-ux/go/tsukiux
```

Requiere Go 1.21+.

### Rust

```toml
[dependencies]
tsuki-ux = "1.0"
```

Requiere Rust 1.70+. Sin crates externos.

---

## Primitivas de output

Las primitivas son las funciones más básicas: imprimen una línea con un símbolo semántico y color.

```
  ✔  compilación terminada       ← success / green
  ✖  error: archivo no encontrado ← fail / red  (stderr)
  ⚠  advertencia: versión antigua ← warn / yellow
  ●  info: usando caché           ← info / cyan
  ▶  Compilando firmware…         ← step / bold cyan
     timestamp: 2026-03-21        ← note / dim
```

| Función    | Símbolo | Color       | Stream |
|------------|---------|-------------|--------|
| `success`  | `✔`     | verde bold  | stdout |
| `fail`     | `✖`     | rojo bold   | stderr |
| `warn`     | `⚠`     | amarillo bold | stdout |
| `info`     | `●`     | cian        | stdout |
| `step`     | `▶`     | cian bold   | stdout |
| `note`     | —       | dim gris    | stdout |
| `artifact` | `◆`     | accent      | stdout |

**Python:**

```python
from tsuki_ux import success, fail, warn, info, step, note, artifact

step("Compilando firmware")
info("Usando caché de compilación")
warn("avr-gcc no encontrado en PATH, usando bundled")
success("Firmware compilado")
fail("No se pudo conectar al puerto")
note("elapsed: 3.2s")
artifact("tsuki_build/firmware.hex")
```

Todas las primitivas tienen variante `f` que acepta `format + args`:

```python
successf("Compilado en %.1fs", elapsed)
failf("Puerto %s ocupado", port)
```

**Go:**

```go
import "github.com/tsuki-team/tsuki-ux/go/tsukiux"

tsukiux.Step("Compilando firmware")
tsukiux.Info("Usando caché")
tsukiux.Warn("avr-gcc no encontrado")
tsukiux.Success("Firmware compilado")
tsukiux.Fail("No se pudo conectar")
tsukiux.Note("elapsed: 3.2s")
```

**Rust:**

```rust
use tsuki_ux::{step, info, warn, success, fail, note};

step("Compilando firmware");
info("Usando caché");
warn("avr-gcc no encontrado");
success("Firmware compilado");
fail("No se pudo conectar");
note("elapsed: 3.2s");
```

---

## LiveBlock

LiveBlock es el componente Docker-style para mostrar la salida de un comando en tiempo real. Mientras corre muestra un spinner animado; al terminar **colapsa en una línea** si tuvo éxito, o **se expande** con toda la salida si falló.

```
  ⠹  cargo build --release                     ← animado mientras corre

  ✔  cargo build --release  [3.2s]             ← colapsado en éxito

  ✖  cargo build --release                     ← expandido en error
  │  error[E0382]: use of moved value
  │    --> src/main.rs:42:5
  ╰─ exit 1
```

En entornos no-TTY (CI, pipes) imprime cada línea directamente sin animación.

### Python — context manager

```python
from tsuki_ux import LiveBlock

with LiveBlock("cargo build --release") as b:
    b.line("Compiling main.rs...")
    b.line("Compiling lib.rs...")
    b.line("Linking...")
# ✔  cargo build --release  [1.4s]
```

Si se lanza una excepción dentro del `with`, el bloque se expande mostrando el error.

### Python — manual

```python
b = LiveBlock("npm install")
b.start()
for pkg in packages:
    b.line(f"added {pkg}")
b.finish(ok=True)
# or:
b.finish(ok=False, summary="exit 1")
```

### Go

```go
b := tsukiux.NewLiveBlock("cargo build --release")
b.Start()
b.Line("Compiling main.rs...")
b.Line("Linking...")
b.Finish(true, "")           // ✔ collapses
b.Finish(false, "exit 1")    // ✖ expands
```

### Rust

```rust
use tsuki_ux::LiveBlock;

let mut b = LiveBlock::new("cargo build --release");
b.start();
b.line("Compiling main.rs...");
b.line("Linking...");
b.finish(true, None);            // ✔ collapses
b.finish(false, Some("exit 1")); // ✖ expands
```

---

## Spinner

Spinner braille independiente del LiveBlock. Útil para operaciones de una sola tarea sin líneas de output intermedias.

```
  ⠋  Detectando puerto serie…   →   ✔  Puerto detectado: /dev/ttyUSB0
```

### Python

```python
from tsuki_ux import Spinner
import time

s = Spinner("Detectando puerto…")
s.start()
time.sleep(1.5)
s.stop(ok=True, msg="Puerto: /dev/ttyUSB0")
# ✔  Puerto: /dev/ttyUSB0
```

Conjuntos de frames disponibles: `SPINNER_FRAMES` (braille), `SPINNER_FRAMES_DOTS`, `SPINNER_FRAMES_LINE`, `SPINNER_FRAMES_ARROW`, `SPINNER_FRAMES_MOON`, `SPINNER_FRAMES_CLOCK`, `SPINNER_FRAMES_BOUNCE`, `SPINNER_FRAMES_PULSE`, `SPINNER_FRAMES_SNAKE`, `SPINNER_FRAMES_PIXEL`, `SPINNER_FRAMES_TOGGLE`, `SPINNER_FRAMES_GROW`.

```python
s = Spinner("Cargando…", frames=SPINNER_FRAMES_MOON)
```

### Go

```go
s := tsukiux.NewSpinner("Detectando puerto…")
s.Start()
time.Sleep(1500 * time.Millisecond)
s.Stop(true, "Puerto: /dev/ttyUSB0")
```

### Rust

```rust
use tsuki_ux::Spinner;
use std::time::Duration;

let mut s = Spinner::new("Detectando puerto…");
s.start();
std::thread::sleep(Duration::from_millis(1500));
s.stop(true, Some("Puerto: /dev/ttyUSB0"));
```

---

## Box / Panel

Dibuja un panel con bordes redondeados y título opcional.

```
╭── tsuki config ─────────────────────────────────────────────╮
│  Archivo de configuración del proyecto                       │
│  board: arduino-nano                                         │
╰─────────────────────────────────────────────────────────────╯
```

### Python

```python
from tsuki_ux import box

box("Archivo de configuración del proyecto\nboard: arduino-nano",
    title="tsuki config")
```

### Go

```go
tsukiux.Box("tsuki config", "Archivo de configuración\nboard: arduino-nano")
```

### Rust

```rust
use tsuki_ux::box_panel;

box_panel("Archivo de configuración\nboard: arduino-nano", Some("tsuki config"));
```

---

## Config table

Muestra pares clave=valor con tipos coloreados, alineación automática y comentarios.

```
╭── tsuki.json ────────────────────────────────────────────────╮
│  board      =  "arduino-nano"                                │
│  port       =  "/dev/ttyUSB0"                                │
│  baud_rate  =  115200                  # velocidad serie     │
│  verbose    =  false                                         │
╰─────────────────────────────────────────────────────────────╯
```

### Python

```python
from tsuki_ux import config_table, ConfigEntry

config_table("tsuki.json", [
    ConfigEntry("board",     "arduino-nano"),
    ConfigEntry("port",      "/dev/ttyUSB0"),
    ConfigEntry("baud_rate", 115200, comment="velocidad serie"),
    ConfigEntry("verbose",   False),
])
```

`ConfigEntry(key, value, comment=None)` — `value` puede ser `str`, `int`, `float`, `bool` o `None`.

### Go

```go
tsukiux.PrintConfig("tsuki.json", []tsukiux.ConfigEntry{
    {Key: "board",     Value: "arduino-nano"},
    {Key: "port",      Value: "/dev/ttyUSB0"},
    {Key: "baud_rate", Value: 115200, Comment: "velocidad serie"},
    {Key: "verbose",   Value: false},
}, false) // raw=false → styled
```

### Rust

```rust
use tsuki_ux::{config_table, ConfigEntry, ConfigValue};

config_table("tsuki.json", &[
    ConfigEntry { key: "board".into(),     value: ConfigValue::Str("arduino-nano".into()), comment: None },
    ConfigEntry { key: "port".into(),      value: ConfigValue::Str("/dev/ttyUSB0".into()), comment: None },
    ConfigEntry { key: "baud_rate".into(), value: ConfigValue::Int(115200), comment: Some("velocidad serie".into()) },
    ConfigEntry { key: "verbose".into(),   value: ConfigValue::Bool(false), comment: None },
]);
```

---

## Traceback

Panel de error estilo debug con localización de archivo, número de línea, fragmento de código y variables locales.

```
╭── RuntimeError ──────────────────────────────────────────────╮
│  buffer overflow                                              │
│                                                              │
│  File "main.go", line 42, in read_sensor                     │
│    41 │  buf := make([]byte, 4)                              │
│  → 42 │  n, _ = port.Read(buf)                              │
│                                                              │
│  Locals: buf=[0 0 0 0]  n=8                                  │
╰─────────────────────────────────────────────────────────────╯
```

### Python

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

### Go

```go
tsukiux.Traceback("RuntimeError", "buffer overflow", []tsukiux.Frame{
    {
        File: "main.go", Line: 42, Func: "read_sensor",
        Code: []tsukiux.CodeLine{
            {Number: 41, Text: "buf := make([]byte, 4)"},
            {Number: 42, Text: "n, _ = port.Read(buf)", IsPointer: true},
        },
        Locals: map[string]string{"buf": "[0 0 0 0]", "n": "8"},
    },
})
```

### Rust

```rust
use tsuki_ux::{traceback, Frame, CodeLine};

traceback("RuntimeError", "buffer overflow", &[
    Frame {
        file: "main.go".into(),
        line: 42,
        func: "read_sensor".into(),
        code: vec![
            CodeLine { number: 41, text: "buf := make([]byte, 4)".into(), is_pointer: false },
            CodeLine { number: 42, text: "n, _ = port.Read(buf)".into(),  is_pointer: true  },
        ],
        locals: vec![("buf".into(), "[0 0 0 0]".into()), ("n".into(), "8".into())],
    }
]);
```

---

## Progress bars

Nueve estilos de barra de progreso, todos con la misma firma: `progress_bar(value, total, width)`.

| Función                  | Estilo         |
|--------------------------|----------------|
| `progress_bar`           | `█░` relleno   |
| `progress_bar_thin`      | `▓░` fino      |
| `progress_bar_braille`   | `⣿⣀` braille   |
| `progress_bar_dots`      | `●○` puntos    |
| `progress_bar_slim`      | `─╌` línea     |
| `progress_bar_gradient`  | gradiente color |
| `progress_bar_arrow`     | `━>` flecha    |
| `progress_bar_steps`     | `[====>   ]`   |
| `progress_bar_squares`   | `▪▫` cuadrados |

### Python

```python
from tsuki_ux import progress_bar, progress_bar_braille

for i in range(101):
    bar = progress_bar(i, 100, width=40)
    print(f"\r  {bar}  {i}%", end="", flush=True)
print()
```

### Go

```go
bar := tsukiux.ProgressBar(i, 100, 40)
fmt.Printf("\r  %s  %d%%", bar, i)
```

### Rust

```rust
use tsuki_ux::progress_bar;

let bar = progress_bar(i, 100, 40);
print!("\r  {}  {}%", bar, i);
```

---

## Color y estilos

### Constantes semánticas

| Constante      | Uso                         |
|----------------|-----------------------------|
| `C_SUCCESS`    | Éxito (verde bold)          |
| `C_ERROR`      | Error (rojo bold)           |
| `C_WARN`       | Advertencia (amarillo bold) |
| `C_INFO`       | Info (cian)                 |
| `C_STEP`       | Paso activo (cian dim)      |
| `C_TITLE`      | Títulos (blanco bold)       |
| `C_MUTED`      | Texto secundario (gris dim) |
| `C_HIGHLIGHT`  | Énfasis (magenta bold)      |
| `C_ACCENT`     | Acento (cian bold)          |

### Helpers de estilo

```python
# Python
from tsuki_ux import bold, dim, italic, underline, strike

print(bold("importante"))
print(dim("secundario"))
print(italic("nota"))
print(underline("enlace"))
```

```go
// Go
import "github.com/tsuki-team/tsuki-ux/go/tsukiux"

tsukiux.ColorSuccess.Println("operación completada")
label := tsukiux.ColorError.Sprint("error")
```

```rust
// Rust
use tsuki_ux::{bold, dim, underline, C_SUCCESS, ansi};

println!("{}", bold("importante"));
println!("{}{}{}", C_SUCCESS, "✔ hecho", tsuki_ux::RESET);
```

### 256 colores y truecolor

```python
# Python
from tsuki_ux import color256, truecolor, bg_truecolor

print(color256(214, "naranja"))
print(truecolor(255, 100, 0, "color exacto"))
```

```rust
// Rust
use tsuki_ux::{color256, truecolor};

println!("{}", color256(214, "naranja"));
println!("{}", truecolor(255, 100, 0, "color exacto"));
```

### strip_ansi

Elimina todos los códigos ANSI de una cadena:

```python
from tsuki_ux import strip_ansi

clean = strip_ansi("\033[1;92m✔ done\033[0m")  # → "✔ done"
```

---

## Símbolos

Los símbolos hacen fallback automático a ASCII cuando el terminal no soporta Unicode.

| Constante    | Unicode | ASCII |
|--------------|---------|-------|
| `SYM_OK`     | `✔`     | `+`   |
| `SYM_FAIL`   | `✖`     | `x`   |
| `SYM_WARN`   | `⚠`     | `!`   |
| `SYM_INFO`   | `●`     | `*`   |
| `SYM_STEP`   | `▶`     | `>`   |
| `SYM_BULLET` | `•`     | `-`   |
| `SYM_PIPE`   | `│`     | `|`   |
| `SYM_ELL`    | `⠿`     | `~`   |
| `SYM_ARROW`  | `→`     | `->`  |
| `BOX_TL`     | `╭`     | `+`   |
| `BOX_TR`     | `╮`     | `+`   |
| `BOX_BL`     | `╰`     | `+`   |
| `BOX_BR`     | `╯`     | `+`   |
| `BOX_H`      | `─`     | `-`   |
| `BOX_V`      | `│`     | `|`   |

---

## Comportamiento adaptativo

La librería detecta el entorno automáticamente. No hace falta configuración manual.

| Entorno | Comportamiento |
|---------|----------------|
| TTY + Unicode + color | Experiencia completa: spinner animado, colores, símbolos braille y box-drawing |
| TTY + `NO_COLOR` o `TERM=dumb` | Símbolos y estructura, sin ANSI |
| Pipe / CI / no-TTY | Sin animaciones, output línea a línea para captura de logs |
| Windows (consola antigua) | Fallback ASCII (`+`, `x`, `!`, `-`) |
| Windows Terminal / UTF-8 | Experiencia completa |

Variables de entorno respetadas:

- `NO_COLOR` — deshabilita colores (respeta el estándar no-color.org)
- `FORCE_COLOR` — fuerza colores incluso en no-TTY (útil en CI)
- `TERM=dumb` — deshabilita colores y símbolos Unicode

---

## API Reference — Python

### Módulo `tsuki_ux`

#### Status primitives

```python
success(msg: str) -> None
successf(fmt: str, *args) -> None
fail(msg: str) -> None
failf(fmt: str, *args) -> None
warn(msg: str) -> None
warnf(fmt: str, *args) -> None
info(msg: str) -> None
infof(fmt: str, *args) -> None
step(msg: str) -> None
stepf(fmt: str, *args) -> None
note(msg: str) -> None
notef(fmt: str, *args) -> None
artifact(path: str) -> None
```

#### Layout

```python
header(title: str) -> None
section(title: str) -> None
section_end() -> None
rule(char: str = "─") -> None
separator() -> None
blank() -> None
```

#### Inline content

```python
badge(label: str, color: str = C_ACCENT) -> str
badge_line(label: str, color: str = C_ACCENT) -> None
key_value(key: str, value: Any, comment: str = "") -> None
key_valuef(key: str, fmt: str, *args) -> None
list_items(items: list[str]) -> None
numbered_list(items: list[str]) -> None
check_list(items: list[tuple[bool, str]]) -> None
indent(text: str, level: int = 1) -> None
highlight(text: str) -> str
accent(text: str) -> str
term_w() -> int
```

#### Timer

```python
class Timer:
    def start(self) -> None
    def stop(self) -> float          # returns elapsed seconds
    def elapsed(self) -> float
    def __str__(self) -> str         # "3.2s"
```

#### Progress bars

```python
progress_bar(value, total, width=40) -> str
progress_bar_thin(value, total, width=40) -> str
progress_bar_braille(value, total, width=40) -> str
progress_bar_dots(value, total, width=40) -> str
progress_bar_slim(value, total, width=40) -> str
progress_bar_gradient(value, total, width=40) -> str
progress_bar_arrow(value, total, width=40) -> str
progress_bar_steps(value, total, width=40) -> str
progress_bar_squares(value, total, width=40) -> str
```

#### LiveBlock

```python
class LiveBlock:
    def __init__(self, label: str) -> None
    def start(self) -> None
    def line(self, text: str) -> None
    def finish(self, ok: bool = True, summary: str = "") -> None
    def __enter__(self) -> LiveBlock
    def __exit__(self, exc_type, exc_val, exc_tb) -> bool
```

#### Spinner

```python
class Spinner:
    def __init__(self, label: str, frames: list[str] = SPINNER_FRAMES) -> None
    def start(self) -> None
    def update(self, label: str) -> None
    def stop(self, ok: bool = True, msg: str = "") -> None
```

#### Box y panels

```python
box(content: str, title: str = "") -> None

class ConfigEntry:
    key: str
    value: Any
    comment: str = ""

config_table(title: str, entries: list[ConfigEntry]) -> None

class CodeLine:
    number: int
    text: str
    is_pointer: bool = False

class Frame:
    file: str
    line: int
    func: str
    code: list[CodeLine]
    locals: dict[str, str] = {}

traceback_box(err_type: str, err_msg: str, frames: list[Frame]) -> None
```

#### run()

Ejecuta un comando en un LiveBlock:

```python
run(
    cmd: list[str],
    *,
    cwd: str | Path | None = None,
    label: str | None = None,   # defaults to cmd[0]
    env: dict | None = None,
) -> None
```

Lanza `subprocess.CalledProcessError` si el comando falla (y el LiveBlock se expande con la salida).

#### Color y estilos

```python
# Constantes semánticas (str con código ANSI)
C_SUCCESS, C_ERROR, C_WARN, C_INFO, C_STEP, C_DIM
C_HIGHLIGHT, C_ACCENT, C_MUTED

# Atributos
BOLD, DIM, ITALIC, UNDERLINE, BLINK, REVERSE, STRIKE, OVERLINE, RESET

# Helpers
bold(s: str) -> str
dim(s: str) -> str
italic(s: str) -> str
underline(s: str) -> str
strike(s: str) -> str
overline(s: str) -> str
blink(s: str) -> str
reverse(s: str) -> str
color256(n: int, s: str) -> str
bg_color256(n: int, s: str) -> str
truecolor(r: int, g: int, b: int, s: str) -> str
bg_truecolor(r: int, g: int, b: int, s: str) -> str
strip_ansi(s: str) -> str

class Style:
    """Combina múltiples atributos."""
    def __init__(self, *codes: str) -> None
    def __call__(self, s: str) -> str
```

---

## API Reference — Go

Paquete: `github.com/tsuki-team/tsuki-ux/go/tsukiux`

### Status

```go
func Success(msg string)
func Fail(msg string)
func Warn(msg string)
func Info(msg string)
func Step(msg string)
func Note(msg string)
func Artifact(path string)
```

### Layout

```go
func Header(title string)
func Section(title string)
func SectionEnd()
func Rule()
func Separator()
func Blank()
```

### Inline

```go
func Badge(label string) string
func KeyValue(key string, value interface{}, comment string)
func List(items []string)
func NumberedList(items []string)
func CheckList(items []CheckItem)
func Indent(text string, level int)
func Highlight(s string) string
func Accent(s string) string
func TermWidth() int
```

### LiveBlock

```go
type LiveBlock struct { /* ... */ }

func NewLiveBlock(label string) *LiveBlock
func (b *LiveBlock) Start()
func (b *LiveBlock) Line(text string)
func (b *LiveBlock) Finish(ok bool, summary string)
```

### Spinner

```go
type Spinner struct { /* ... */ }

func NewSpinner(label string) *Spinner
func (s *Spinner) Start()
func (s *Spinner) Update(label string)
func (s *Spinner) Stop(ok bool, msg string)
```

### Box y panels

```go
func Box(title, content string)

type ConfigEntry struct {
    Key     string
    Value   interface{}
    Comment string
}
func PrintConfig(title string, entries []ConfigEntry, raw bool)

type Frame struct {
    File   string
    Line   int
    Func   string
    Code   []CodeLine
    Locals map[string]string
}
type CodeLine struct {
    Number    int
    Text      string
    IsPointer bool
}
func Traceback(errType, errMsg string, frames []Frame)
```

### Color

```go
type ColorPrinter struct { Code string }

func (c ColorPrinter) Sprint(s string) string
func (c ColorPrinter) Sprintf(format string, args ...interface{}) string
func (c ColorPrinter) Println(s string)
func (c ColorPrinter) Fprintf(w io.Writer, format string, args ...interface{})

// Instancias predefinidas
var (
    ColorSuccess   ColorPrinter
    ColorError     ColorPrinter
    ColorWarn      ColorPrinter
    ColorInfo      ColorPrinter
    ColorStep      ColorPrinter
    ColorMuted     ColorPrinter
    ColorHighlight ColorPrinter
    ColorAccent    ColorPrinter
)

func IsTTY() bool
func StripANSI(s string) string
```

### Progress bars

```go
func ProgressBar(value, total, width int) string
func ProgressBarThin(value, total, width int) string
func ProgressBarBraille(value, total, width int) string
// ... idem para los 9 estilos
```

---

## API Reference — Rust

Crate: `tsuki_ux`

### Status

```rust
pub fn success(msg: &str)
pub fn fail(msg: &str)
pub fn warn(msg: &str)
pub fn info(msg: &str)
pub fn step(msg: &str)
pub fn note(msg: &str)
pub fn artifact(path: &str)
```

### Layout

```rust
pub fn header(title: &str)
pub fn section(title: &str)
pub fn section_end()
pub fn rule()
pub fn separator()
pub fn blank()
```

### LiveBlock

```rust
pub struct LiveBlock { /* ... */ }

impl LiveBlock {
    pub fn new(label: &str) -> Self
    pub fn start(&mut self)
    pub fn line(&mut self, text: &str)
    pub fn finish(&mut self, ok: bool, summary: Option<&str>)
}
```

### Spinner

```rust
pub struct Spinner { /* ... */ }

impl Spinner {
    pub fn new(label: &str) -> Self
    pub fn with_frames(label: &str, frames: &'static [&'static str]) -> Self
    pub fn start(&mut self)
    pub fn update(&mut self, label: &str)
    pub fn stop(&mut self, ok: bool, msg: Option<&str>)
}
```

### Box y panels

```rust
pub fn box_panel(content: &str, title: Option<&str>)

pub struct ConfigEntry {
    pub key: String,
    pub value: ConfigValue,
    pub comment: Option<String>,
}
pub enum ConfigValue { Str(String), Int(i64), Float(f64), Bool(bool), Null }
pub fn config_table(title: &str, entries: &[ConfigEntry])

pub struct Frame {
    pub file: String,
    pub line: usize,
    pub func: String,
    pub code: Vec<CodeLine>,
    pub locals: Vec<(String, String)>,
}
pub struct CodeLine { pub number: usize, pub text: String, pub is_pointer: bool }
pub fn traceback(err_type: &str, err_msg: &str, frames: &[Frame])
```

### Color

```rust
// Constantes de color semántico
pub const C_SUCCESS: &str;
pub const C_ERROR: &str;
pub const C_WARN: &str;
pub const C_INFO: &str;
pub const C_STEP: &str;
pub const C_TITLE: &str;
pub const C_MUTED: &str;
pub const C_HIGHLIGHT: &str;
pub const C_ACCENT: &str;
pub const RESET: &str;
pub const BOLD: &str;
pub const DIM: &str;
// ...

pub fn is_tty() -> bool
pub fn color_enabled() -> bool
pub fn strip_ansi(s: &str) -> String
pub fn bold(s: &str) -> String
pub fn dim(s: &str) -> String
pub fn italic(s: &str) -> String
pub fn underline(s: &str) -> String
pub fn color256(n: u8, s: &str) -> String
pub fn truecolor(r: u8, g: u8, b: u8, s: &str) -> String

pub struct Style(/* ... */);
impl Style {
    pub fn new() -> Self
    pub fn bold(self) -> Self
    pub fn dim(self) -> Self
    pub fn fg(self, code: &str) -> Self
    pub fn apply(&self, s: &str) -> String
}
```

### Progress bars

```rust
pub fn progress_bar(value: usize, total: usize, width: usize) -> String
pub fn progress_bar_thin(value: usize, total: usize, width: usize) -> String
pub fn progress_bar_braille(value: usize, total: usize, width: usize) -> String
// ... idem para los 9 estilos
```

---

## Release workflow

El proceso de publicación está automatizado con `tools/release.py`. Publica simultáneamente a GitHub Releases, PyPI y crates.io.

### Prerequisitos

1. Crea un `.env` en la raíz del repo con tus tokens:

```
GITHUB_TOKEN=ghp_...
PYPI_API_TOKEN=pypi-...
CARGO_TOKEN=...
```

2. Asegúrate de tener instalados: `python3`, `twine` (`pip install twine build`), `cargo`, `git`.

### Comandos

```bash
# Publicar todo con bump de patch (x.y.Z+1)
python tools/release.py

# Bump explícito
python tools/release.py --bump minor
python tools/release.py --version 2.0.0

# Preview sin ejecutar nada
python tools/release.py --dry-run

# Un solo destino
python tools/release.py --only pypi
python tools/release.py --only cargo
python tools/release.py --only github

# Saltar tests
python tools/release.py --skip-tests
```

### Qué hace

1. Lee `.env` y valida que los tokens estén presentes.
2. Detecta la versión actual via `git describe`.
3. Calcula la nueva versión según el bump.
4. Pregunta confirmación interactiva (saltable con `--dry-run`).
5. Actualiza `python/pyproject.toml` y `rust/Cargo.toml`.
6. Crea commit `chore: release vX.Y.Z` y tag anotado.
7. Push del commit y del tag a `origin`.
8. Ejecuta los tests de los tres packages.
9. Crea GitHub Release con changelog auto-generado desde git log.
10. Publica a PyPI via `twine`.
11. Publica a crates.io via `cargo publish`.

### Versionado

Se usa [semver](https://semver.org/). La versión se sincroniza entre `pyproject.toml` y `Cargo.toml` en cada release. El módulo Go no gestiona versión en archivo (`go.mod` usa el tag de git directamente).