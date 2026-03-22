# Contributing to tsuki-ux

## Estructura del repo

```
tsuki-ux/
├── go/
│   └── tsukiux/          # Paquete Go
│       ├── tsukiux.go    # Primitivas, color, spinner frames, símbolos
│       ├── box.go        # Box, config table, traceback
│       ├── live.go       # LiveBlock
│       ├── prompt.go     # Inputs interactivos (select, confirm, input)
│       ├── color.go      # ColorPrinter
│       ├── rawmode_*.go  # Raw terminal mode por plataforma
│       ├── termwidth_*.go
│       └── windows.go
├── python/
│   └── tsuki_ux/         # Paquete Python
│       ├── __init__.py
│       ├── _primitives.py
│       ├── _box.py
│       ├── _live.py
│       ├── _spinner.py
│       ├── _color.py
│       ├── _symbols.py
│       └── _run.py
├── rust/
│   └── src/              # Crate Rust
│       ├── lib.rs
│       ├── primitives.rs
│       ├── box_panel.rs
│       ├── live.rs
│       ├── spinner.rs
│       ├── color.rs
│       └── symbols.rs
├── tools/
│   ├── release.py        # Script de publicación
│   ├── package.py        # Utilidad de empaquetado zip
│   └── README.md
└── go.mod
```

## Principios de diseño

**Paridad entre lenguajes.** Cada función debe existir en los tres lenguajes con la misma semántica. Los nombres siguen la convención idiomática de cada lenguaje (`snake_case` en Python/Rust, `PascalCase` en Go), pero el comportamiento visual es idéntico.

**Cero dependencias externas.** La librería solo usa stdlib + ANSI. No se aceptan PRs que añadan dependencias en runtime.

**Detección automática del entorno.** La lógica de detección (TTY, Unicode, color) está centralizada en cada implementación y nunca requiere configuración manual del usuario.

**Fallback graceful.** Cada componente debe funcionar correctamente en modo no-TTY (pipes, CI), en terminales sin Unicode y en Windows con consola antigua.

## Añadir una nueva primitiva

1. Implementar en Go en `go/tsukiux/tsukiux.go`.
2. Implementar en Python en `python/tsuki_ux/_primitives.py` y exportar desde `__init__.py`.
3. Implementar en Rust en `rust/src/primitives.rs` y re-exportar desde `lib.rs`.
4. Añadir un ejemplo en los tres `examples/demo.*`.
5. Documentar en `docs/DOCUMENTATION.md`.

## Tests

```bash
# Go
cd go && go test ./...

# Python
cd python && python -m pytest

# Rust
cd rust && cargo test
```

## Correr los demos

```bash
# Python
python python/examples/demo.py

# Go
cd go && go run examples/demo.go

# Rust
cd rust && cargo run --example demo
```

## Code style

- **Go**: `gofmt`. Sin imports innecesarios.
- **Python**: PEP 8. Type hints en funciones públicas. Docstrings en clases.
- **Rust**: `rustfmt`. `#[must_use]` en funciones que retornan `String`. Sin `unwrap()` en código de librería — usa `unwrap_or_default()` o maneja el error.

## Commit style

```
feat: añadir progress_bar_gradient
fix: corregir fallback ASCII en Windows Terminal legacy
docs: actualizar API Reference de Rust
chore: release v1.1.0
```