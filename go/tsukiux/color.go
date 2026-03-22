package tsukiux

import (
	"fmt"
	"io"
	"os"
)

// ── ColorPrinter ──────────────────────────────────────────────────────────────

// ColorPrinter is an ANSI-aware printer bound to a color code.
// It gracefully degrades to plain text when color is disabled.
//
// Usage:
//
//	ColorInfo.Println("board detected")
//	label := ColorSuccess.Sprint("✔ done")
//	ColorError.Fprintf(os.Stderr, "error: %s", msg)
type ColorPrinter struct {
	Code string // raw ANSI escape code, e.g. "\033[1;92m"
}

// Sprint returns s wrapped in the color code, or s unchanged if color is off.
func (c ColorPrinter) Sprint(s string) string {
	if colorEnabled() {
		return c.Code + s + "\033[0m"
	}
	return s
}

// Sprintf returns a formatted string wrapped in the color code.
func (c ColorPrinter) Sprintf(format string, args ...interface{}) string {
	return c.Sprint(fmt.Sprintf(format, args...))
}

// Println prints s wrapped in the color code followed by a newline.
func (c ColorPrinter) Println(s string) {
	fmt.Println(c.Sprint(s))
}

// Printf prints a color-wrapped formatted string.
func (c ColorPrinter) Printf(format string, args ...interface{}) {
	fmt.Print(c.Sprintf(format, args...))
}

// Fprint writes the color-wrapped string to w.
func (c ColorPrinter) Fprint(w io.Writer, s string) {
	fmt.Fprint(w, c.Sprint(s))
}

// Fprintln writes the color-wrapped string followed by a newline to w.
func (c ColorPrinter) Fprintln(w io.Writer, s string) {
	fmt.Fprintln(w, c.Sprint(s))
}

// Fprintf writes a color-wrapped formatted string to w.
func (c ColorPrinter) Fprintf(w io.Writer, format string, args ...interface{}) {
	fmt.Fprint(w, c.Sprintf(format, args...))
}

// FprintfErr writes a color-wrapped formatted string to stderr.
func (c ColorPrinter) FprintfErr(format string, args ...interface{}) {
	c.Fprintf(os.Stderr, format, args...)
}

// ── Pre-built color printers ──────────────────────────────────────────────────

var (
	ColorTitle     = ColorPrinter{"\033[1;97m"}
	ColorKey       = ColorPrinter{"\033[96m"}
	ColorValue     = ColorPrinter{"\033[93m"}
	ColorString    = ColorPrinter{"\033[92m"}
	ColorNumber    = ColorPrinter{"\033[94m"}
	ColorBool      = ColorPrinter{"\033[95m"}
	ColorNull      = ColorPrinter{"\033[90m"}
	ColorMuted     = ColorPrinter{"\033[90m"}
	ColorSuccess   = ColorPrinter{"\033[1;92m"}
	ColorError     = ColorPrinter{"\033[1;91m"}
	ColorWarn      = ColorPrinter{"\033[1;93m"}
	ColorInfo      = ColorPrinter{"\033[96m"}
	ColorStep      = ColorPrinter{"\033[36m"}
	ColorHighlight = ColorPrinter{"\033[1;95m"}
	ColorAccent    = ColorPrinter{"\033[1;96m"}
	ColorDim       = ColorPrinter{"\033[2m"}
	ColorBold      = ColorPrinter{"\033[1m"}
	ColorItalic    = ColorPrinter{"\033[3m"}
)

// NewColorPrinter creates a ColorPrinter with an arbitrary ANSI code.
//
//	tsukiux.NewColorPrinter("\033[38;5;208m")  // 256-color orange
//	tsukiux.NewColorPrinter("\033[38;2;255;100;0m")  // truecolor orange
func NewColorPrinter(ansiCode string) ColorPrinter {
	return ColorPrinter{Code: ansiCode}
}