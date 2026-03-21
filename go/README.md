# tsuki-ux · Go

Terminal UX library faithful to the Tsuki project.  
Port of `cli/internal/ui/ui.go`.

## Install

```bash
go get github.com/tsuki-team/tsuki-ux/go/tsukiux
```

## API

### Status primitives

```go
import "github.com/tsuki-team/tsuki-ux/go/tsukiux"

tsukiux.Step("Compilando firmware")     //   ▶  Compilando firmware
tsukiux.Success("Hecho")               //   ✔  Hecho
tsukiux.Fail("Algo salió mal")         //   ✖  Algo salió mal  (stderr)
tsukiux.Warn("Versión antigua")        //   ⚠  Versión antigua
tsukiux.Info("Usando caché")           //   ●  Usando caché
tsukiux.Note("timestamp: 2026-03-21") //   ●  timestamp…  (dim)
```

### LiveBlock

```go
b := tsukiux.NewLiveBlock("cargo build --release")
b.Start()
b.Line("Compiling main.rs...")
b.Line("Linking...")
b.Finish(true, "")          // ✔ collapses
b.Finish(false, "exit 1")   // ✖ expands with all lines
```

### Box / Panel

```go
tsukiux.Box("tsuki config", "board = \"nano\"\nbaud = 115200", nil)

tsukiux.PrintConfig("tsuki.json", []tsukiux.ConfigEntry{
    {Key: "board",     Value: "arduino-nano"},
    {Key: "baud_rate", Value: 115200, Comment: "velocidad serie"},
    {Key: "verbose",   Value: false},
}, false)
```

### Traceback

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
