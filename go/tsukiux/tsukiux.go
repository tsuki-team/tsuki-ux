// Package tsukiux provides terminal UX primitives faithful to the Tsuki project.
// Port of cli/internal/ui/ui.go and tools/build.py.
// Zero external dependencies — pure stdlib ANSI.
package tsukiux

import (
	"fmt"
	"os"
	"strings"
)

// ── TTY / color detection ─────────────────────────────────────────────────────

// IsTTY returns true when stdout is a real terminal.
func IsTTY() bool {
	fi, err := os.Stdout.Stat()
	return err == nil && (fi.Mode()&os.ModeCharDevice) != 0
}

func colorEnabled() bool {
	if os.Getenv("FORCE_COLOR") != "" {
		return true
	}
	if !IsTTY() {
		return false
	}
	if os.Getenv("NO_COLOR") != "" {
		return false
	}
	if os.Getenv("TERM") == "dumb" {
		return false
	}
	return true
}

// paint wraps s in an ANSI escape + reset, or returns s unchanged.
func paint(code, s string) string {
	if colorEnabled() {
		return code + s + "\033[0m"
	}
	return s
}

// a returns an ANSI code string only when color is enabled.
func a(code string) string {
	if colorEnabled() {
		return code
	}
	return ""
}

// ── Palette ───────────────────────────────────────────────────────────────────

const (
	reset   = "\033[0m"
	bold    = "\033[1m"
	dim     = "\033[2m"
	italic  = "\033[3m"

	cSuccess = "\033[1;92m"
	cError   = "\033[1;91m"
	cWarn    = "\033[1;93m"
	cInfo    = "\033[96m"
	cStep    = "\033[36m"
	cTitle   = "\033[1;97m"
	cMuted   = "\033[90m"

	cKey     = "\033[96m"
	cValue   = "\033[93m"
	cString  = "\033[92m"
	cNumber  = "\033[94m"
	cBool    = "\033[95m"
	cNull    = "\033[90m"
	cComment = "\033[2;3m"

	cTBBorder  = "\033[31m"
	cTBTitle   = "\033[1;91m"
	cTBFile    = "\033[96m"
	cTBLineNum = "\033[93m"
	cTBFunc    = "\033[92m"
	cTBCode    = "\033[97m"
	cTBHigh    = "\033[1;91m"
	cTBLocals  = "\033[93m"
	cTBErrType = "\033[1;91m"
	cTBErrMsg  = "\033[97m"
)

// ── Symbols ───────────────────────────────────────────────────────────────────

const (
	SymOK     = "✔"
	SymFail   = "✖"
	SymWarn   = "⚠"
	SymInfo   = "●"
	SymStep   = "▶"
	SymBullet = "•"
	SymPipe   = "│"
	SymEll    = "…"
	SymPtr    = "❱"

	BoxTL = "╭"
	BoxTR = "╮"
	BoxBL = "╰"
	BoxBR = "╯"
	BoxH  = "─"
	BoxV  = "│"
)

var SpinnerFrames = []string{"⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"}

// ── Utilities ─────────────────────────────────────────────────────────────────

// TermWidth returns the terminal width (default 100).
func TermWidth() int {
	return 100
}

func hline(n int) string {
	if n <= 0 {
		return ""
	}
	return strings.Repeat(BoxH, n)
}

// StripANSI removes ANSI escape sequences for length calculations.
func StripANSI(s string) string {
	var b strings.Builder
	inEsc := false
	for _, r := range s {
		if r == '\x1b' {
			inEsc = true
			continue
		}
		if inEsc {
			if r == 'm' {
				inEsc = false
			}
			continue
		}
		b.WriteRune(r)
	}
	return b.String()
}

func truncate(s string, max int) string {
	if max <= 3 || len([]rune(s)) <= max {
		return s
	}
	return string([]rune(s)[:max-1]) + SymEll
}

// ── Status primitives ─────────────────────────────────────────────────────────

// Success prints:  ✔  msg
func Success(msg string) {
	fmt.Printf("  %s  %s\n", paint(cSuccess, SymOK), msg)
}

// Fail prints:  ✖  msg  (stderr)
func Fail(msg string) {
	fmt.Fprintf(os.Stderr, "  %s  %s\n", paint(cError, SymFail), msg)
}

// Warn prints:  ⚠  msg
func Warn(msg string) {
	fmt.Printf("  %s  %s\n", paint(cWarn, SymWarn), msg)
}

// Info prints:  ●  msg
func Info(msg string) {
	fmt.Printf("  %s  %s\n", paint(cInfo, SymInfo), msg)
}

// Step prints a main step header preceded by a blank line.
func Step(msg string) {
	fmt.Printf("\n  %s  %s%s%s\n", paint(cStep, SymStep), a(bold), msg, a(reset))
}

// Note prints a dim auxiliary note.
func Note(msg string) {
	fmt.Printf("  %s%s  %s%s\n", a(dim), SymInfo, msg, a(reset))
}

// Artifact prints a build artifact entry.
func Artifact(name, size string) {
	if size != "" {
		fmt.Printf("   %s  %s  %s(%s)%s\n", paint(cStep, SymBullet), name, a(dim), size, a(reset))
	} else {
		fmt.Printf("   %s  %s\n", paint(cStep, SymBullet), name)
	}
}

// Header prints a full-width rounded header box.
func Header(title string) {
	w := TermWidth()
	h := w - 2
	bar := hline(h)
	fmt.Println()
	fmt.Printf("%s%s%s%s%s\n", a(dim), BoxTL, bar, BoxTR, a(reset))
	content := "  🌙 " + title
	pad := h - len(StripANSI(content)) - 1
	if pad < 0 {
		pad = 0
	}
	fmt.Printf("%s%s%s%s%s%s%s\n",
		a(dim), BoxV, a(reset),
		paint(cTitle, content),
		strings.Repeat(" ", pad),
		a(dim), BoxV)
	fmt.Printf("%s%s%s%s%s\n", a(dim), BoxBL, bar, BoxBR, a(reset))
}

// Section prints a platform-block header.
func Section(title string) {
	w := TermWidth()
	if w > 72 {
		w = 72
	}
	inner := " " + title + " "
	pad := w - len([]rune(inner)) - 4
	if pad < 0 {
		pad = 0
	}
	fmt.Printf("\n%s%s%s%s%s%s%s%s%s\n",
		a(dim), BoxTL, BoxH, a(reset),
		paint(cTitle, inner),
		a(dim), hline(pad), BoxTR, a(reset))
}

// SectionEnd prints the closing border of a section.
func SectionEnd() {
	w := TermWidth()
	if w > 72 {
		w = 72
	}
	fmt.Printf("%s%s%s%s%s\n", a(dim), BoxBL, hline(w-2), BoxBR, a(reset))
}

// ProgressBar renders an inline progress bar.
func ProgressBar(label string, done, total, width int) {
	pct := float64(done) / float64(total)
	filled := int(float64(width)*pct + 0.5)
	bar := paint(cSuccess, strings.Repeat("█", filled)) +
		paint(cMuted, strings.Repeat("░", width-filled))
	fmt.Printf("  %s  [%s]  %d%%\n", label, bar, int(pct*100))
}
