// Package tsukiux provides terminal UX primitives faithful to the Tsuki project.
// Zero external dependencies — pure stdlib ANSI.
package tsukiux

import (
	"fmt"
	"os"
	"strings"
	"time"
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
	ansiReset     = "\033[0m"
	ansiBold      = "\033[1m"
	ansiDim       = "\033[2m"
	ansiItalic    = "\033[3m"
	ansiUnderline = "\033[4m"
	ansiBlink     = "\033[5m"
	ansiReverse   = "\033[7m"
	ansiStrike    = "\033[9m"
	ansiOverline  = "\033[53m"

	cSuccess   = "\033[1;92m"
	cError     = "\033[1;91m"
	cWarn      = "\033[1;93m"
	cInfo      = "\033[96m"
	cStep      = "\033[36m"
	cTitle     = "\033[1;97m"
	cMuted     = "\033[90m"
	cHighlight = "\033[1;95m"
	cAccent    = "\033[1;96m"

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
	SymArrow  = "→"
	SymDash   = "–"
	SymDot    = "·"
	SymStar   = "★"
	SymPlus   = "✚"
	SymMinus  = "⊖"
	SymCheck  = "✓"
	SymCross  = "✗"
	SymLock   = "🔒"
	SymKey    = "🔑"
	SymFlash  = "⚡"
	SymRocket = "🚀"

	BoxTL  = "╭"
	BoxTR  = "╮"
	BoxBL  = "╰"
	BoxBR  = "╯"
	BoxH   = "─"
	BoxV   = "│"
	BoxTLs = "┌"
	BoxTRs = "┐"
	BoxBLs = "└"
	BoxBRs = "┘"
)

// SpinnerFrames is the default braille spinner animation.
var SpinnerFrames = []string{"⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"}

// SpinnerFramesDots is an alternative dots spinner.
var SpinnerFramesDots = []string{"⣾", "⣽", "⣻", "⢿", "⡿", "⣟", "⣯", "⣷"}

// SpinnerFramesLine is a minimal ASCII spinner.
var SpinnerFramesLine = []string{"-", "\\", "|", "/"}

// SpinnerFramesArrow is an animated arrow-bar spinner.
var SpinnerFramesArrow = []string{"▹▹▹▹▹", "▸▹▹▹▹", "▹▸▹▹▹", "▹▹▸▹▹", "▹▹▹▸▹", "▹▹▹▹▸"}

// SpinnerFramesMoon cycles through moon phases.
var SpinnerFramesMoon = []string{"🌑", "🌒", "🌓", "🌔", "🌕", "🌖", "🌗", "🌘"}

// SpinnerFramesClock cycles through clock faces.
var SpinnerFramesClock = []string{"🕛", "🕐", "🕑", "🕒", "🕓", "🕔", "🕕", "🕖", "🕗", "🕘", "🕙", "🕚"}

// SpinnerFramesBounce is a ball bouncing left-to-right inside brackets.
var SpinnerFramesBounce = []string{
	"[●    ]", "[●    ]", "[ ●   ]", "[  ●  ]", "[   ● ]", "[    ●]",
	"[    ●]", "[   ● ]", "[  ●  ]", "[ ●   ]",
}

// SpinnerFramesPulse is a growing/shrinking block character.
var SpinnerFramesPulse = []string{"▏", "▎", "▍", "▌", "▋", "▊", "▉", "█", "▉", "▊", "▋", "▌", "▍", "▎"}

// SpinnerFramesSnake is a braille snake filling and draining a bar.
var SpinnerFramesSnake = []string{
	"⣀⣀⣀⣀⣀", "⣄⣀⣀⣀⣀", "⣤⣀⣀⣀⣀", "⣦⣄⣀⣀⣀",
	"⣶⣤⣄⣀⣀", "⣷⣦⣤⣄⣀", "⣿⣶⣦⣤⣄", "⣿⣿⣶⣦⣤",
	"⣿⣿⣿⣶⣦", "⣿⣿⣿⣿⣶", "⣿⣿⣿⣿⣿", "⣿⣿⣿⣿⣶",
}

// SpinnerFramesToggle is a single dot scanning across five positions.
var SpinnerFramesToggle = []string{"▪▫▫▫▫", "▫▪▫▫▫", "▫▫▪▫▫", "▫▫▫▪▫", "▫▫▫▫▪", "▫▫▫▪▫", "▫▫▪▫▫", "▫▪▫▫▫"}

// SpinnerFramesGrow is an expanding/contracting filled bar.
var SpinnerFramesGrow = []string{
	"▰▱▱▱▱▱▱▱", "▰▰▱▱▱▱▱▱", "▰▰▰▱▱▱▱▱", "▰▰▰▰▱▱▱▱",
	"▰▰▰▰▰▱▱▱", "▰▰▰▰▰▰▱▱", "▰▰▰▰▰▰▰▱", "▰▰▰▰▰▰▰▰",
	"▱▰▰▰▰▰▰▰", "▱▱▰▰▰▰▰▰", "▱▱▱▰▰▰▰▰", "▱▱▱▱▰▰▰▰",
}

// ── Internal utilities ────────────────────────────────────────────────────────

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

func visibleLen(s string) int {
	return len([]rune(StripANSI(s)))
}

func formatElapsed(d time.Duration) string {
	if d < time.Second {
		return fmt.Sprintf("%dms", d.Milliseconds())
	}
	return fmt.Sprintf("%.1fs", d.Seconds())
}

// ── Status primitives ─────────────────────────────────────────────────────────

// Success prints:  ✔  msg
func Success(msg string) {
	fmt.Printf("  %s  %s\n", paint(cSuccess, SymOK), msg)
}

// Successf prints a formatted success message.
func Successf(format string, args ...interface{}) { Success(fmt.Sprintf(format, args...)) }

// Fail prints:  ✖  msg  (stderr)
func Fail(msg string) {
	fmt.Fprintf(os.Stderr, "  %s  %s\n", paint(cError, SymFail), msg)
}

// Failf prints a formatted failure message to stderr.
func Failf(format string, args ...interface{}) { Fail(fmt.Sprintf(format, args...)) }

// Warn prints:  ⚠  msg
func Warn(msg string) {
	fmt.Printf("  %s  %s\n", paint(cWarn, SymWarn), msg)
}

// Warnf prints a formatted warning.
func Warnf(format string, args ...interface{}) { Warn(fmt.Sprintf(format, args...)) }

// Info prints:  ●  msg
func Info(msg string) {
	fmt.Printf("  %s  %s\n", paint(cInfo, SymInfo), msg)
}

// Infof prints a formatted info message.
func Infof(format string, args ...interface{}) { Info(fmt.Sprintf(format, args...)) }

// Step prints a main step header preceded by a blank line.
func Step(msg string) {
	fmt.Printf("\n  %s  %s%s%s\n", paint(cStep, SymStep), a(ansiBold), msg, a(ansiReset))
}

// Stepf prints a formatted step header.
func Stepf(format string, args ...interface{}) { Step(fmt.Sprintf(format, args...)) }

// Note prints a dim auxiliary note.
func Note(msg string) {
	fmt.Printf("  %s%s  %s%s\n", a(ansiDim), SymInfo, msg, a(ansiReset))
}

// Notef prints a formatted note.
func Notef(format string, args ...interface{}) { Note(fmt.Sprintf(format, args...)) }

// Artifact prints a build artifact entry.
func Artifact(name, size string) {
	if size != "" {
		fmt.Printf("   %s  %s  %s(%s)%s\n", paint(cStep, SymBullet), name, a(ansiDim), size, a(ansiReset))
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
	fmt.Printf("%s%s%s%s%s\n", a(ansiDim), BoxTL, bar, BoxTR, a(ansiReset))
	content := "  🌙 " + title
	pad := h - visibleLen(content) - 1
	if pad < 0 {
		pad = 0
	}
	fmt.Printf("%s%s%s%s%s%s%s\n",
		a(ansiDim), BoxV, a(ansiReset),
		paint(cTitle, content),
		strings.Repeat(" ", pad),
		a(ansiDim), BoxV)
	fmt.Printf("%s%s%s%s%s\n", a(ansiDim), BoxBL, bar, BoxBR, a(ansiReset))
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
		a(ansiDim), BoxTL, BoxH, a(ansiReset),
		paint(cTitle, inner),
		a(ansiDim), hline(pad), BoxTR, a(ansiReset))
}

// SectionEnd prints the closing border of a section.
func SectionEnd() {
	w := TermWidth()
	if w > 72 {
		w = 72
	}
	fmt.Printf("%s%s%s%s%s\n", a(ansiDim), BoxBL, hline(w-2), BoxBR, a(ansiReset))
}

// ProgressBar renders an inline progress bar.
func ProgressBar(label string, done, total, width int) {
	if total == 0 {
		total = 1
	}
	pct := float64(done) / float64(total)
	filled := int(float64(width)*pct + 0.5)
	if filled > width {
		filled = width
	}
	bar := paint(cSuccess, strings.Repeat("█", filled)) +
		paint(cMuted, strings.Repeat("░", width-filled))
	fmt.Printf("  %s  [%s]  %d%%\n", label, bar, int(pct*100))
}

// ── Layout helpers ────────────────────────────────────────────────────────────

// Rule prints a full-width horizontal rule with an optional centered label.
func Rule(label string) {
	w := TermWidth()
	if label == "" {
		fmt.Printf("%s%s%s\n", a(ansiDim), hline(w), a(ansiReset))
		return
	}
	inner := " " + label + " "
	sides := w - len(inner)
	left := sides / 2
	right := sides - left
	if left < 0 {
		left = 0
	}
	if right < 0 {
		right = 0
	}
	fmt.Printf("%s%s%s%s%s%s\n",
		a(ansiDim), hline(left), a(ansiReset),
		paint(cMuted, inner),
		a(ansiDim), hline(right)+a(ansiReset))
}

// Separator prints a blank line, a dim rule, and another blank line.
func Separator() {
	fmt.Println()
	Rule("")
	fmt.Println()
}

// Blank prints an empty line.
func Blank() { fmt.Println() }

// ── Text styling ──────────────────────────────────────────────────────────────

// Style is a composable ANSI text styler.
//
//	s := tsukiux.NewStyle().Bold().Underline().Fg(tsukiux.ColorError)
//	fmt.Println(s.Paint("error message"))
type Style struct {
	codes []string
}

// NewStyle returns an empty style.
func NewStyle() *Style { return &Style{} }

func (s *Style) add(code string) *Style { s.codes = append(s.codes, code); return s }

func (s *Style) Bold() *Style      { return s.add(ansiBold) }
func (s *Style) Dim() *Style       { return s.add(ansiDim) }
func (s *Style) Italic() *Style    { return s.add(ansiItalic) }
func (s *Style) Underline() *Style { return s.add(ansiUnderline) }
func (s *Style) Strike() *Style    { return s.add(ansiStrike) }
func (s *Style) Overline() *Style  { return s.add(ansiOverline) }
func (s *Style) Blink() *Style     { return s.add(ansiBlink) }
func (s *Style) Reverse() *Style   { return s.add(ansiReverse) }

// Fg applies a ColorPrinter's code as the foreground color.
func (s *Style) Fg(c ColorPrinter) *Style { return s.add(c.Code) }

// FgCode applies a raw ANSI foreground code.
func (s *Style) FgCode(code string) *Style { return s.add(code) }

// Rgb256 applies a 256-color foreground (0–255).
func (s *Style) Rgb256(n uint8) *Style { return s.add(fmt.Sprintf("\033[38;5;%dm", n)) }

// TrueColor applies an RGB foreground (0–255 each channel).
func (s *Style) TrueColor(r, g, b uint8) *Style {
	return s.add(fmt.Sprintf("\033[38;2;%d;%d;%dm", r, g, b))
}

// BgRgb256 applies a 256-color background (0–255).
func (s *Style) BgRgb256(n uint8) *Style { return s.add(fmt.Sprintf("\033[48;5;%dm", n)) }

// BgTrueColor applies an RGB background.
func (s *Style) BgTrueColor(r, g, b uint8) *Style {
	return s.add(fmt.Sprintf("\033[48;2;%d;%d;%dm", r, g, b))
}

// Paint wraps text in all accumulated ANSI codes.
func (s *Style) Paint(text string) string {
	if !colorEnabled() || len(s.codes) == 0 {
		return text
	}
	return strings.Join(s.codes, "") + text + ansiReset
}

// Println prints text with this style followed by a newline.
func (s *Style) Println(text string) { fmt.Println(s.Paint(text)) }

// Printf prints a styled formatted string.
func (s *Style) Printf(format string, args ...interface{}) {
	fmt.Print(s.Paint(fmt.Sprintf(format, args...)))
}

// ── Standalone style helpers ──────────────────────────────────────────────────

// Underline returns text with underline decoration.
func Underline(text string) string { return paint(ansiUnderline, text) }

// Strike returns text with strikethrough decoration.
func Strike(text string) string { return paint(ansiStrike, text) }

// Overline returns text with overline decoration.
func Overline(text string) string { return paint(ansiOverline, text) }

// Blink returns blinking text (not supported in all terminals).
func Blink(text string) string { return paint(ansiBlink, text) }

// Reverse returns text with foreground/background colors swapped.
func Reverse(text string) string { return paint(ansiReverse, text) }

// Bold returns bold text.
func Bold(text string) string { return paint(ansiBold, text) }

// Dim returns dim/faint text.
func Dim(text string) string { return paint(ansiDim, text) }

// Italic returns italic text.
func Italic(text string) string { return paint(ansiItalic, text) }

// Color256 returns text colored with a 256-color palette index (0–255).
func Color256(n uint8, text string) string {
	return paint(fmt.Sprintf("\033[38;5;%dm", n), text)
}

// TrueColor returns text with an RGB foreground color.
func TrueColor(r, g, b uint8, text string) string {
	return paint(fmt.Sprintf("\033[38;2;%d;%d;%dm", r, g, b), text)
}

// BgColor256 returns text with a 256-color background.
func BgColor256(n uint8, text string) string {
	return paint(fmt.Sprintf("\033[48;5;%dm", n), text)
}

// BgTrueColor returns text with an RGB background color.
func BgTrueColor(r, g, b uint8, text string) string {
	return paint(fmt.Sprintf("\033[48;2;%d;%d;%dm", r, g, b), text)
}

// ── Progress bar variants ─────────────────────────────────────────────────────

// ProgressBarThin renders a slim Unicode line bar.
//
//	  label  ──────────────╴          40%
func ProgressBarThin(label string, done, total, width int) {
	if total == 0 {
		total = 1
	}
	pct := float64(done) / float64(total)
	filled := int(float64(width)*pct + 0.5)
	if filled > width {
		filled = width
	}
	bar := paint(cSuccess, strings.Repeat("─", filled)+strings.Repeat("╴", min1(width-filled, 1))) +
		paint(cMuted, strings.Repeat(" ", max0(width-filled-1)))
	fmt.Printf("  %s  %s  %d%%\n", label, bar, int(pct*100))
}

// ProgressBarBraille renders a high-resolution braille progress bar.
//
//	  label  ⣿⣿⣿⣿⣿⣿⣦⣀⣀⣀  60%
func ProgressBarBraille(label string, done, total, width int) {
	if total == 0 {
		total = 1
	}
	pct := float64(done) / float64(total)
	// each braille char represents 1/8 of a cell
	eighths := int(float64(width*8)*pct + 0.5)
	full := eighths / 8
	rem := eighths % 8

	blocks := []string{"⣀", "⣄", "⣤", "⣦", "⣶", "⣷", "⣿"}
	var bar strings.Builder
	for i := 0; i < width; i++ {
		if i < full {
			bar.WriteString(paint(cSuccess, "⣿"))
		} else if i == full && rem > 0 {
			bar.WriteString(paint(cInfo, blocks[rem-1]))
		} else {
			bar.WriteString(paint(cMuted, "⣀"))
		}
	}
	fmt.Printf("  %s  %s  %d%%\n", label, bar.String(), int(pct*100))
}

// ProgressBarDots renders a dotted progress bar.
//
//	  label  ●●●●●●●●○○○○  67%
func ProgressBarDots(label string, done, total, width int) {
	if total == 0 {
		total = 1
	}
	pct := float64(done) / float64(total)
	filled := int(float64(width)*pct + 0.5)
	if filled > width {
		filled = width
	}
	bar := paint(cSuccess, strings.Repeat("●", filled)) +
		paint(cMuted, strings.Repeat("○", width-filled))
	fmt.Printf("  %s  %s  %d%%\n", label, bar, int(pct*100))
}

// ProgressBarSlim renders a slim filled/empty block bar.
//
//	  label  ▰▰▰▰▰▰▱▱▱▱  60%
func ProgressBarSlim(label string, done, total, width int) {
	if total == 0 {
		total = 1
	}
	pct := float64(done) / float64(total)
	filled := int(float64(width)*pct + 0.5)
	if filled > width {
		filled = width
	}
	bar := paint(cSuccess, strings.Repeat("▰", filled)) +
		paint(cMuted, strings.Repeat("▱", width-filled))
	fmt.Printf("  %s  %s  %d%%\n", label, bar, int(pct*100))
}

// ProgressBarGradient renders a gradient-shaded bar using ░▒▓█.
//
//	  label  [████▓▒░      ]  45%
func ProgressBarGradient(label string, done, total, width int) {
	if total == 0 {
		total = 1
	}
	pct := float64(done) / float64(total)
	// 4 sub-cells per position
	units := int(float64(width*4)*pct + 0.5)
	full := units / 4
	rem := units % 4
	shades := []string{" ", "░", "▒", "▓"}
	var bar strings.Builder
	for i := 0; i < width; i++ {
		if i < full {
			bar.WriteString(paint(cSuccess, "█"))
		} else if i == full {
			bar.WriteString(paint(cInfo, shades[rem]))
		} else {
			bar.WriteString(paint(cMuted, " "))
		}
	}
	fmt.Printf("  %s  [%s]  %d%%\n", label, bar.String(), int(pct*100))
}

// ProgressBarArrow renders a classic arrow-style bar.
//
//	  label  [=======>    ]  56%
func ProgressBarArrow(label string, done, total, width int) {
	if total == 0 {
		total = 1
	}
	pct := float64(done) / float64(total)
	filled := int(float64(width)*pct + 0.5)
	if filled > width {
		filled = width
	}
	var body string
	if filled == 0 {
		body = paint(cMuted, strings.Repeat("-", width))
	} else if filled == width {
		body = paint(cSuccess, strings.Repeat("=", width))
	} else {
		body = paint(cSuccess, strings.Repeat("=", filled-1)+">")+
			paint(cMuted, strings.Repeat("-", width-filled))
	}
	fmt.Printf("  %s  [%s]  %d%%\n", label, body, int(pct*100))
}

// ProgressBarSteps renders a step counter with fraction.
//
//	  label  [■■■□□□□□]  3/8
func ProgressBarSteps(label string, done, total int) {
	if total == 0 {
		total = 1
	}
	if done > total {
		done = total
	}
	bar := paint(cSuccess, strings.Repeat("■", done)) +
		paint(cMuted, strings.Repeat("□", total-done))
	fmt.Printf("  %s  [%s]  %d/%d\n", label, bar, done, total)
}

// ProgressBarSquares renders a segmented square-block bar.
//
//	  label  ▪▪▪▪▪▫▫▫▫▫  50%
func ProgressBarSquares(label string, done, total, width int) {
	if total == 0 {
		total = 1
	}
	pct := float64(done) / float64(total)
	filled := int(float64(width)*pct + 0.5)
	if filled > width {
		filled = width
	}
	bar := paint(cSuccess, strings.Repeat("▪", filled)) +
		paint(cMuted, strings.Repeat("▫", width-filled))
	fmt.Printf("  %s  %s  %d%%\n", label, bar, int(pct*100))
}

func min1(a, b int) int {
	if a < b {
		return a
	}
	return b
}

func max0(n int) int {
	if n < 0 {
		return 0
	}
	return n
}

// ── Inline content helpers ────────────────────────────────────────────────────

// Badge returns a color-coded inline tag string: [ label ]
// style: "success" | "error" | "warn" | "info" | "muted" | "highlight" | "accent"
func Badge(label, style string) string {
	return paint(badgeCode(style), "[ "+label+" ]")
}

func badgeCode(style string) string {
	switch style {
	case "success":
		return cSuccess
	case "error":
		return cError
	case "warn":
		return cWarn
	case "muted":
		return cMuted
	case "highlight":
		return cHighlight
	case "accent":
		return cAccent
	default:
		return cInfo
	}
}

// BadgeLine prints a badge followed by a message on the same line.
func BadgeLine(label, style, msg string) {
	fmt.Printf("  %s  %s\n", Badge(label, style), msg)
}

// KeyValue prints a single aligned key → value line.
func KeyValue(key string, value interface{}) {
	fmt.Printf("  %s  %s  %s\n",
		paint(cKey, key),
		paint(cMuted, SymArrow),
		paint(cValue, fmt.Sprintf("%v", value)))
}

// KeyValuef prints a key with a formatted value.
func KeyValuef(key, format string, args ...interface{}) {
	KeyValue(key, fmt.Sprintf(format, args...))
}

// List prints a bulleted list of items.
func List(items []string) {
	for _, item := range items {
		fmt.Printf("  %s  %s\n", paint(cMuted, SymBullet), item)
	}
}

// NumberedList prints a numbered list of items.
func NumberedList(items []string) {
	for i, item := range items {
		fmt.Printf("  %s%d.%s  %s\n", a(cMuted), i+1, a(ansiReset), item)
	}
}

// CheckList prints a list where each item can be checked or unchecked.
func CheckList(items []string, checked []bool) {
	for i, item := range items {
		sym := paint(cMuted, SymCross)
		if i < len(checked) && checked[i] {
			sym = paint(cSuccess, SymCheck)
		}
		fmt.Printf("  %s  %s\n", sym, item)
	}
}

// Indent prints each line with a left pipe indent (useful for quoted output).
func Indent(text string) {
	for _, line := range strings.Split(text, "\n") {
		fmt.Printf("  %s  %s%s%s\n", paint(cMuted, SymPipe), a(ansiDim), line, a(ansiReset))
	}
}

// Highlight prints msg with high-visibility magenta emphasis.
func Highlight(msg string) {
	fmt.Printf("  %s%s%s\n", a(cHighlight), msg, a(ansiReset))
}

// Accent prints msg in bold cyan — useful for secondary emphasis.
func Accent(msg string) {
	fmt.Printf("  %s%s%s\n", a(cAccent), msg, a(ansiReset))
}

// ── Timer helper ──────────────────────────────────────────────────────────────

// Timer is a simple wall-clock timer you can embed in Step output.
//
//	t := tsukiux.NewTimer()
//	// ... do work ...
//	tsukiux.Success("done  " + t.Elapsed())
type Timer struct{ start time.Time }

// NewTimer starts a new timer.
func NewTimer() *Timer { return &Timer{start: time.Now()} }

// Elapsed returns a human-readable elapsed time string.
func (t *Timer) Elapsed() string { return formatElapsed(time.Since(t.start)) }

// ElapsedDim returns the elapsed time formatted as a dim string ready to embed in output.
func (t *Timer) ElapsedDim() string {
	return fmt.Sprintf("%s[%s]%s", a(ansiDim), formatElapsed(time.Since(t.start)), a(ansiReset))
}