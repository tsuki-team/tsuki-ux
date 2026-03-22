// tsuki-ux Go demo
//
// Normal mode:       go run go/examples/demo.go
// Presentation mode: go run go/examples/demo.go --presentation
//
// Presentation mode is designed to be recorded as a GIF.
// Recommended recorder: vhs (https://github.com/charmbracelet/vhs)
//
//   Output demo.gif
//   Set FontSize 14
//   Set Width 900
//   Set Height 600
//   Type "go run go/examples/demo.go --presentation"
//   Enter
//   Sleep 60s
package main

import (
	"fmt"
	"os"
	"os/exec"
	"strings"
	"time"

	ui "github.com/tsuki-team/tsuki-ux/go/tsukiux"
)

// ── Presentation helpers ──────────────────────────────────────────────────────

func clearScreen() { fmt.Print("\033[2J\033[H") }
func pause(d time.Duration) { time.Sleep(d) }

func presTitle(title string) {
	clearScreen()
	fmt.Println()
	w := 60
	bar := strings.Repeat("─", w-2)
	fmt.Printf("  \033[2m╭%s╮\033[0m\n", bar)
	label := "  🌙 tsuki-ux  ·  " + title
	// 🌙 is 1 rune but occupies 2 terminal columns — add 1 to compensate
	pad := w - len([]rune(label)) - 1 - 1
	if pad < 0 { pad = 0 }
	fmt.Printf("  \033[2m│\033[0m\033[1;97m%s%s\033[2m│\033[0m\n", label, strings.Repeat(" ", pad))
	fmt.Printf("  \033[2m╰%s╯\033[0m\n", bar)
	fmt.Println()
	pause(500 * time.Millisecond)
}

// ── Full demo ─────────────────────────────────────────────────────────────────

func runFull() {
	ui.Header("tsuki-ux demo")

	ui.Step("Status primitives")
	ui.Success("compilación terminada")
	ui.Successf("firmware listo: %s", "tsuki-flash v4.0.0")
	ui.Fail("error: archivo no encontrado")
	ui.Warn("versión antigua detectada")
	ui.Info("usando caché local")
	ui.Note("timestamp: 2026-03-21T10:00:00Z")

	ui.Step("Layout")
	ui.Rule("plataformas soportadas")
	ui.Section("Platform: linux-amd64")
	ui.Artifact("tsuki-linux-amd64.tar.gz", "4.2 MB")
	ui.Artifact("tsuki-flash-linux-amd64", "2.1 MB")
	ui.SectionEnd()

	ui.Step("Inline content")
	ui.BadgeLine("GO", "info", "transpilando firmware")
	ui.BadgeLine("OK", "success", "compilación exitosa")
	ui.BadgeLine("ERR", "error", "puerto serie ocupado")
	ui.BadgeLine("⚡", "highlight", "tsuki-flash activo")
	ui.Blank()
	ui.KeyValue("board", "arduino-nano")
	ui.KeyValuef("baud", "%d", 115200)
	ui.Blank()
	ui.CheckList(
		[]string{"go.mod configurado", "paquetes instalados", "board detectada", "puerto disponible"},
		[]bool{true, true, true, false},
	)
	ui.Blank()
	ui.Indent("avrdude: AVR device initialized\navrdude: verifying flash memory")

	ui.Step("Text decoration & color")
	fmt.Printf("  %s  %s  %s\n", ui.Bold("Negrita"), ui.Dim("Tenue"), ui.Italic("Cursiva"))
	fmt.Printf("  %s  %s  %s\n", ui.Underline("Subrayado"), ui.Strike("Tachado"), ui.Overline("Sobrelineado"))
	fmt.Printf("  %s\n", ui.Reverse("Invertido"))
	ui.Blank()
	fmt.Print("  256-color: ")
	for _, n := range []uint8{196, 214, 226, 46, 51, 57, 201} { fmt.Print(ui.Color256(n, "█") + "  ") }
	fmt.Println()
	fmt.Print("  truecolor: ")
	for _, rgb := range [][3]uint8{{255,80,80},{255,165,0},{255,255,80},{80,255,80},{80,200,255},{160,80,255}} {
		fmt.Print(ui.TrueColor(rgb[0], rgb[1], rgb[2], "█") + "  ")
	}
	fmt.Println()
	ui.Blank()
	fmt.Printf("  %s\n", ui.NewStyle().Bold().Underline().Fg(ui.ColorSuccess).Paint("bold + underline + success"))
	fmt.Printf("  %s\n", ui.NewStyle().Strike().TrueColor(200, 80, 80).Paint("strike + truecolor"))
	fmt.Printf("  %s\n", ui.NewStyle().Italic().Rgb256(208).BgRgb256(234).Paint("italic + 256-color bg"))
	fmt.Printf("  %s\n", ui.NewStyle().Bold().Reverse().Fg(ui.ColorInfo).Paint("bold + reverse + info"))

	ui.Step("Progress bars")
	for _, b := range []struct{ n string; f func(int) }{
		{"Block    [████████░░░░]", func(i int) { ui.ProgressBar("compilando", i, 40, 40) }},
		{"Braille  ⣿⣿⣿⣿⣦⣀⣀⣀",     func(i int) { ui.ProgressBarBraille("compilando", i, 40, 20) }},
		{"Gradient [████▓▒░   ]",   func(i int) { ui.ProgressBarGradient("compilando", i, 40, 40) }},
		{"Slim     ▰▰▰▰▰▰▱▱▱▱",     func(i int) { ui.ProgressBarSlim("compilando", i, 40, 30) }},
		{"Arrow    [=======>--]",    func(i int) { ui.ProgressBarArrow("compilando", i, 40, 40) }},
		{"Dots     ●●●●●●●○○○",     func(i int) { ui.ProgressBarDots("compilando", i, 40, 30) }},
		{"Squares  ▪▪▪▪▪▫▫▫▫▫",    func(i int) { ui.ProgressBarSquares("compilando", i, 40, 30) }},
		{"Steps    [■■■□□□□□]",     func(i int) { ui.ProgressBarSteps("compilando", i/5, 8) }},
	} {
		ui.Note(b.n)
		for i := 0; i <= 40; i += 8 {
			fmt.Print("\033[1A\033[K")
			b.f(i)
			time.Sleep(50 * time.Millisecond)
		}
	}

	ui.Step("Spinners")
	for _, sp := range []struct{ l string; f []string }{
		{"Braille", ui.SpinnerFrames}, {"Arrow", ui.SpinnerFramesArrow},
		{"Moon", ui.SpinnerFramesMoon}, {"Bounce", ui.SpinnerFramesBounce},
		{"Pulse", ui.SpinnerFramesPulse}, {"Snake", ui.SpinnerFramesSnake},
		{"Grow", ui.SpinnerFramesGrow}, {"Toggle", ui.SpinnerFramesToggle},
	} {
		s := ui.NewSpinnerWithFrames(sp.l, sp.f)
		s.Start(); time.Sleep(700 * time.Millisecond); s.Stop(true, "")
	}

	ui.Step("LiveBlock — éxito")
	b := ui.NewLiveBlock("cargo build --release --target avr-atmega328p")
	b.Start()
	for _, l := range []string{
		"   Compiling proc-macro2 v1.0.94", "   Compiling tsuki-flash v4.0.0",
		"    Finished release [optimized] in 3.24s",
	} { b.Line(l); time.Sleep(180 * time.Millisecond) }
	b.Finish(true, "")

	ui.Step("LiveBlock — fallo")
	b2 := ui.NewLiveBlock("avrdude -p atmega328p -P /dev/ttyUSB0")
	b2.Start()
	b2.Line("avrdude: ser_open(): can't open \"/dev/ttyUSB0\"")
	b2.Line("No such file or directory")
	time.Sleep(400 * time.Millisecond)
	b2.Finish(false, "exit 1")

	ui.Step("Table")
	ui.Table("boards detectadas", []ui.TableColumn{
		{Header: "Board"}, {Header: "MCU"}, {Header: "Puerto"}, {Header: "Baud", Align: "right"},
	}, [][]string{
		{"arduino-nano", "ATmega328P", "/dev/ttyUSB0", "115200"},
		{"arduino-uno", "ATmega328P", "/dev/ttyUSB1", "115200"},
		{"esp32-devkit", "ESP32", "/dev/ttyUSB2", "921600"},
	})

	ui.Step("Config table")
	ui.PrintConfig("tsuki.json", []ui.ConfigEntry{
		{Key: "board", Value: "arduino-nano"},
		{Key: "baud_rate", Value: 115200, Comment: "velocidad serie"},
		{Key: "flash_mode", Value: "tsuki-flash"},
		{Key: "verbose", Value: false},
	}, false)

	ui.Step("DiffView")
	ui.DiffView("src/main.go", 8, []ui.DiffLine{
		{Kind: ui.DiffContext, Text: `import "arduino"`},
		{Kind: ui.DiffRemoved, Text: `var LED_PIN int = 12`},
		{Kind: ui.DiffAdded, Text: `var LED_PIN int = 13`},
		{Kind: ui.DiffContext, Text: `func setup() {`},
		{Kind: ui.DiffRemoved, Text: `    arduino.PinMode(LED_PIN, arduino.INPUT)`},
		{Kind: ui.DiffAdded, Text: `    arduino.PinMode(LED_PIN, arduino.OUTPUT)`},
		{Kind: ui.DiffContext, Text: `}`},
	})

	ui.Blank()
	ui.Success("Demo completo")
}

// ── Presentation mode ─────────────────────────────────────────────────────────

func runPresentation() {
	// 1 — Status primitives
	presTitle("status primitives")
	for _, fn := range []func(){
		func() { ui.Success("compilación terminada") },
		func() { ui.Successf("firmware listo: %s", "tsuki-flash v4.0.0") },
		func() { ui.Fail("error: archivo no encontrado") },
		func() { ui.Warn("versión antigua detectada") },
		func() { ui.Info("usando caché local") },
		func() { ui.Note("timestamp: 2026-03-21T10:00:00Z") },
	} {
		fn()
		pause(220 * time.Millisecond)
	}
	pause(1000 * time.Millisecond)

	// 2 — Inline content
	presTitle("inline content")
	ui.BadgeLine("GO", "info", "transpilando firmware")
	pause(200 * time.Millisecond)
	ui.BadgeLine("OK", "success", "compilación exitosa")
	pause(200 * time.Millisecond)
	ui.BadgeLine("ERR", "error", "puerto serie ocupado")
	pause(200 * time.Millisecond)
	ui.BadgeLine("⚡", "highlight", "tsuki-flash activo")
	pause(400 * time.Millisecond)
	ui.Blank()
	ui.KeyValue("board", "arduino-nano")
	ui.KeyValue("port", "/dev/ttyUSB0")
	ui.KeyValuef("baud", "%d", 115200)
	pause(500 * time.Millisecond)
	ui.Blank()
	ui.CheckList(
		[]string{"go.mod configurado", "paquetes instalados", "board detectada", "puerto disponible"},
		[]bool{true, true, true, false},
	)
	pause(1200 * time.Millisecond)

	// 3 — Text styles
	presTitle("text decoration & color")
	styledLines := []string{
		fmt.Sprintf("  %s  %s  %s", ui.Bold("Negrita"), ui.Dim("Tenue"), ui.Italic("Cursiva")),
		fmt.Sprintf("  %s  %s  %s", ui.Underline("Subrayado"), ui.Strike("Tachado"), ui.Overline("Sobrelineado")),
		fmt.Sprintf("  %s", ui.Reverse("Invertido")),
	}
	for _, s := range styledLines {
		fmt.Println(s)
		pause(350 * time.Millisecond)
	}
	ui.Blank()
	fmt.Print("  256-color: ")
	for _, n := range []uint8{196, 214, 226, 46, 51, 57, 201} {
		fmt.Print(ui.Color256(n, "█") + "  ")
		pause(80 * time.Millisecond)
	}
	fmt.Println()
	pause(200 * time.Millisecond)
	fmt.Print("  truecolor: ")
	for _, rgb := range [][3]uint8{{255,80,80},{255,165,0},{255,255,80},{80,255,80},{80,200,255},{160,80,255}} {
		fmt.Print(ui.TrueColor(rgb[0], rgb[1], rgb[2], "█") + "  ")
		pause(80 * time.Millisecond)
	}
	fmt.Println()
	pause(400 * time.Millisecond)
	ui.Blank()
	for _, s := range []string{
		ui.NewStyle().Bold().Underline().Fg(ui.ColorSuccess).Paint("bold + underline + success"),
		ui.NewStyle().Strike().TrueColor(200, 80, 80).Paint("strike + truecolor"),
		ui.NewStyle().Italic().Rgb256(208).BgRgb256(234).Paint("italic + 256-color bg"),
		ui.NewStyle().Bold().Reverse().Fg(ui.ColorInfo).Paint("bold + reverse + info"),
	} {
		fmt.Printf("  %s\n", s)
		pause(250 * time.Millisecond)
	}
	pause(1200 * time.Millisecond)

	// 4 — Progress bars (animated, one per frame)
	presTitle("progress bars")
	for _, b := range []struct{ n string; f func(int) }{
		{"Block    [████████░░░░]", func(i int) { ui.ProgressBar("compilando", i, 40, 40) }},
		{"Braille  ⣿⣿⣿⣿⣦⣀⣀⣀",     func(i int) { ui.ProgressBarBraille("compilando", i, 40, 20) }},
		{"Gradient [████▓▒░   ]",   func(i int) { ui.ProgressBarGradient("compilando", i, 40, 40) }},
		{"Slim     ▰▰▰▰▰▰▱▱▱▱",     func(i int) { ui.ProgressBarSlim("compilando", i, 40, 30) }},
		{"Arrow    [=======>--]",    func(i int) { ui.ProgressBarArrow("compilando", i, 40, 40) }},
		{"Dots     ●●●●●●●○○○",     func(i int) { ui.ProgressBarDots("compilando", i, 40, 30) }},
	} {
		ui.Note(b.n)
		for i := 0; i <= 40; i++ {
			fmt.Print("\033[1A\033[K")
			b.f(i)
			time.Sleep(35 * time.Millisecond)
		}
		pause(400 * time.Millisecond)
	}

	// 5 — Spinners
	presTitle("spinners")
	for _, sp := range []struct{ l string; f []string }{
		{"Braille  ⠋⠙⠹⠸⠼⠴",   ui.SpinnerFrames},
		{"Arrow    ▸▹▹▹▹",      ui.SpinnerFramesArrow},
		{"Moon     🌑🌒🌓🌔",   ui.SpinnerFramesMoon},
		{"Bounce   [●    ]",     ui.SpinnerFramesBounce},
		{"Pulse    ▏▎▍▌▋▊▉█",  ui.SpinnerFramesPulse},
		{"Snake    ⣿⣿⣿⣿⣿",     ui.SpinnerFramesSnake},
		{"Grow     ▰▰▰▰▱▱▱▱",  ui.SpinnerFramesGrow},
	} {
		s := ui.NewSpinnerWithFrames(sp.l, sp.f)
		s.Start()
		time.Sleep(1200 * time.Millisecond)
		s.Stop(true, "")
		pause(120 * time.Millisecond)
	}
	pause(600 * time.Millisecond)

	// 6 — LiveBlock
	presTitle("live block")
	pause(300 * time.Millisecond)
	b := ui.NewLiveBlock("cargo build --release --target avr-atmega328p")
	b.Start()
	for _, l := range []string{
		"   Compiling proc-macro2 v1.0.94",
		"   Compiling quote v1.0.40",
		"   Compiling syn v2.0.100",
		"   Compiling tsuki-flash v4.0.0",
		"    Finished release [optimized] target(s) in 3.24s",
	} {
		b.Line(l)
		time.Sleep(280 * time.Millisecond)
	}
	b.Finish(true, "")
	pause(500 * time.Millisecond)
	b2 := ui.NewLiveBlock("avrdude -p atmega328p -c arduino -P /dev/ttyUSB0")
	b2.Start()
	b2.Line("avrdude: ser_open(): can't open device \"/dev/ttyUSB0\"")
	b2.Line("avrdude: serial port open: No such file or directory")
	time.Sleep(900 * time.Millisecond)
	b2.Finish(false, "exit 1")
	pause(1000 * time.Millisecond)

	// 7 — Config + Diff
	presTitle("config table  &  diff view")
	pause(300 * time.Millisecond)
	ui.PrintConfig("tsuki.json", []ui.ConfigEntry{
		{Key: "board", Value: "arduino-nano"},
		{Key: "port", Value: "/dev/ttyUSB0"},
		{Key: "baud_rate", Value: 115200, Comment: "velocidad serie"},
		{Key: "flash_mode", Value: "tsuki-flash"},
		{Key: "verbose", Value: false},
	}, false)
	pause(700 * time.Millisecond)
	fmt.Println()
	ui.DiffView("src/main.go", 8, []ui.DiffLine{
		{Kind: ui.DiffContext, Text: `import "arduino"`},
		{Kind: ui.DiffRemoved, Text: `var LED_PIN int = 12`},
		{Kind: ui.DiffAdded, Text: `var LED_PIN int = 13`},
		{Kind: ui.DiffContext, Text: `func setup() {`},
		{Kind: ui.DiffRemoved, Text: `    arduino.PinMode(LED_PIN, arduino.INPUT)`},
		{Kind: ui.DiffAdded, Text: `    arduino.PinMode(LED_PIN, arduino.OUTPUT)`},
		{Kind: ui.DiffContext, Text: `}`},
	})
	pause(1500 * time.Millisecond)

	// fin
	presTitle("fin")
	ui.Success("tsuki-ux  ·  github.com/tsuki-team/tsuki-ux")
	pause(2500 * time.Millisecond)
}

func hasFlag(flag string) bool {
	for _, a := range os.Args[1:] {
		if a == flag {
			return true
		}
	}
	return false
}

// startRecording tries asciinema first, then falls back to the `script` command.
// Returns a cleanup function that stops the recording and prints the output path.
// If no recorder is found, returns nil and prints a warning.
func startRecording(outFile string) func() {
	// Try asciinema
	if path, err := exec.LookPath("asciinema"); err == nil {
		cmd := exec.Command(path, "rec", "--overwrite", outFile)
		cmd.Stdin = os.Stdin
		cmd.Stdout = os.Stdout
		cmd.Stderr = os.Stderr
		if err := cmd.Start(); err == nil {
			return func() {
				cmd.Process.Signal(os.Interrupt)
				cmd.Wait()
				fmt.Printf("\n  \033[90mRecording saved to: %s\033[0m\n", outFile)
			}
		}
	}

	// Try vhs (https://github.com/charmbracelet/vhs) via a .tape file
	if _, err := exec.LookPath("vhs"); err == nil {
		tape := strings.TrimSuffix(outFile, ".cast") + ".tape"
		// Write a minimal .tape that runs this binary in presentation mode
		selfPath, _ := os.Executable()
		tapeContent := fmt.Sprintf(`Output %s
Set FontSize 14
Set Width 100
Set Height 40
Set Theme "Catppuccin Mocha"
Type "%s --presentation"
Enter
Sleep 90s
`, strings.TrimSuffix(outFile, ".cast")+".gif", selfPath)
		os.WriteFile(tape, []byte(tapeContent), 0644)
		fmt.Printf("  \033[90mvhs tape written to: %s\033[0m\n", tape)
		fmt.Printf("  \033[90mRun: vhs %s\033[0m\n\n", tape)
	} else {
		fmt.Fprintf(os.Stderr,
			"  \033[1;93m⚠\033[0m  No recorder found.\n"+
				"     Install asciinema: https://asciinema.org/docs/installation\n"+
				"     Or vhs:            https://github.com/charmbracelet/vhs\n\n",
		)
	}
	return nil
}

func main() {
	isPresentation := hasFlag("--presentation")
	isRecord := hasFlag("--record")

	if isRecord && !isPresentation {
		// --record implies --presentation
		isPresentation = true
	}

	if isRecord {
		outFile := "demo.cast"
		for i, a := range os.Args[1:] {
			if a == "--out" && i+2 < len(os.Args) {
				outFile = os.Args[i+2]
			}
		}
		if stop := startRecording(outFile); stop != nil {
			defer stop()
		}
	}

	if isPresentation {
		runPresentation()
	} else {
		runFull()
	}
}