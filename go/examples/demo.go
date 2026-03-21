// tsuki-ux Go demo — all primitives in action.
// Run: go run examples/demo.go
package main

import (
	"fmt"
	"time"

	ui "github.com/tsuki/tsuki-ux/go/tsukiux"
)

func main() {
	// ── Header ────────────────────────────────────────────────────────────────
	ui.Header("tsuki-ux demo")

	// ── Status primitives ─────────────────────────────────────────────────────
	ui.Step("Output primitives")
	ui.Success("compilación terminada")
	ui.Fail("error: archivo no encontrado")
	ui.Warn("versión antigua detectada")
	ui.Info("usando caché local")
	ui.Note("timestamp: 2026-03-21T10:00:00Z")

	// ── Section ───────────────────────────────────────────────────────────────
	ui.Section("Platform: linux-amd64")
	ui.Artifact("tsuki-linux-amd64.tar.gz", "4.2 MB")
	ui.Artifact("tsuki-flash-linux-amd64", "2.1 MB")
	ui.SectionEnd()

	// ── Progress bar ──────────────────────────────────────────────────────────
	ui.Step("Progress bar")
	for i := 0; i <= 40; i += 8 {
		fmt.Print("\033[1A\033[K")
		ui.ProgressBar("compiling", i, 40, 40)
		time.Sleep(100 * time.Millisecond)
	}

	// ── LiveBlock — success ───────────────────────────────────────────────────
	ui.Step("LiveBlock — éxito (colapsa)")
	b := ui.NewLiveBlock("cargo build --release --target avr-atmega328p")
	b.Start()
	lines := []string{
		"   Compiling proc-macro2 v1.0.94",
		"   Compiling quote v1.0.40",
		"   Compiling syn v2.0.100",
		"   Compiling tsuki-flash v4.0.0",
		"    Finished release [optimized] target(s) in 3.24s",
	}
	for _, l := range lines {
		b.Line(l)
		time.Sleep(180 * time.Millisecond)
	}
	b.Finish(true, "")

	// ── LiveBlock — failure ───────────────────────────────────────────────────
	ui.Step("LiveBlock — fallo (expande)")
	b2 := ui.NewLiveBlock("avrdude -p atmega328p -c arduino -P /dev/ttyUSB0")
	b2.Start()
	b2.Line("avrdude: ser_open(): can't open device \"/dev/ttyUSB0\"")
	b2.Line("avrdude: serial port open: No such file or directory")
	time.Sleep(400 * time.Millisecond)
	b2.Finish(false, "exit 1")

	// ── Box / config table ────────────────────────────────────────────────────
	ui.Step("Config table")
	ui.PrintConfig("tsuki.json", []ui.ConfigEntry{
		{Key: "board", Value: "arduino-nano"},
		{Key: "port", Value: "/dev/ttyUSB0"},
		{Key: "baud_rate", Value: 115200, Comment: "velocidad serie"},
		{Key: "flash_mode", Value: "tsuki-flash"},
		{Key: "verbose", Value: false},
	}, false)

	// ── Traceback ─────────────────────────────────────────────────────────────
	ui.Step("Rich traceback")
	ui.Traceback("ZeroDivisionError", "division by zero", []ui.Frame{
		{
			File: "main.go",
			Line: 21,
			Func: "divide_all",
			Code: []ui.CodeLine{
				{Number: 19, Text: "for n, d in divides:"},
				{Number: 20, Text: "    result = divide_by(n, d)"},
				{Number: 21, Text: "    result = divide_by(n, d)", IsPointer: true},
				{Number: 22, Text: "    print(fmt.Sprintf(\"%d / %d = %d\", n, d, result))"},
			},
			Locals: map[string]string{
				"divides": "[(1000, 200), ...]",
				"divisor": "0",
			},
		},
	})

	fmt.Println()
	ui.Success("Demo completo")
}
