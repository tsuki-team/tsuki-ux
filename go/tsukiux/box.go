package tsukiux

import (
	"fmt"
	"os"
	"strings"
)

// ── Generic box ───────────────────────────────────────────────────────────────

// Box draws a bordered panel with an optional title.
//
//	╭── Title ──────────────────────────────────╮
//	│  content...                               │
//	╰───────────────────────────────────────────╯
func Box(title, content string) {
	w := TermWidth()
	inner := w - 2

	if title != "" {
		ts := " " + title + " "
		dashes := inner - len(ts) - 2
		left := dashes / 2
		right := dashes - left
		fmt.Printf("%s%s%s\n",
			paint(cTBBorder, BoxTL+hline(left)),
			paint(cTitle, ts),
			paint(cTBBorder, hline(right)+BoxTR))
	} else {
		fmt.Printf("%s\n", paint(cTBBorder, BoxTL+hline(inner)+BoxTR))
	}

	for _, line := range strings.Split(content, "\n") {
		pad := inner - len(StripANSI(line)) - 1
		if pad < 0 {
			pad = 0
		}
		fmt.Printf("%s %s%s %s\n",
			paint(cTBBorder, BoxV),
			line, strings.Repeat(" ", pad),
			paint(cTBBorder, BoxV))
	}

	fmt.Printf("%s\n", paint(cTBBorder, BoxBL+hline(inner)+BoxBR))
}

// ── Config table ──────────────────────────────────────────────────────────────

// ConfigEntry is one key/value row in a config display.
type ConfigEntry struct {
	Key     string
	Value   interface{}
	Comment string
}

// PrintConfig renders a styled config table, or plain key=value if raw=true.
//
//	╭── title ─────────────────────────────────────────────────╮
//	│  board      =  "arduino-nano"                            │
//	│  baud_rate  =  115200            # velocidad serie       │
//	╰──────────────────────────────────────────────────────────╯
func PrintConfig(title string, entries []ConfigEntry, raw bool) {
	if raw {
		for _, e := range entries {
			fmt.Printf("%s = %v\n", e.Key, e.Value)
		}
		return
	}

	keyWidth := 0
	for _, e := range entries {
		if len(e.Key) > keyWidth {
			keyWidth = len(e.Key)
		}
	}

	type row struct{ rich, plain string }
	rows := make([]row, 0, len(entries))
	for _, e := range entries {
		keyStr := paint(cKey, fmt.Sprintf("%-*s", keyWidth, e.Key))
		sep := a(dim) + "  =  " + a(reset)
		valStr := fmtConfigValue(e.Value)
		rich := keyStr + sep + valStr
		plain := fmt.Sprintf("%-*s  =  %v", keyWidth, e.Key, e.Value)
		if e.Comment != "" {
			c := "  # " + e.Comment
			rich += paint(cComment, c)
			plain += c
		}
		rows = append(rows, row{rich, plain})
	}

	w := TermWidth()
	inner := w - 2
	minInner := len(title) + 6
	for _, r := range rows {
		if n := len(r.plain) + 2; n > minInner {
			minInner = n
		}
	}
	if minInner > inner {
		inner = minInner
	}

	ts := " " + title + " "
	padR := inner - len(ts) - 2
	if padR < 0 {
		padR = 0
	}
	fmt.Printf("%s%s%s\n",
		paint(cTBBorder, BoxTL+BoxH+BoxH),
		paint(cTitle, ts),
		paint(cTBBorder, hline(padR)+BoxTR))

	for _, r := range rows {
		pad := inner - len(r.plain) - 1
		if pad < 0 {
			pad = 0
		}
		fmt.Printf("%s %s%s %s\n",
			paint(cTBBorder, BoxV),
			r.rich, strings.Repeat(" ", pad),
			paint(cTBBorder, BoxV))
	}

	fmt.Printf("%s\n", paint(cTBBorder, BoxBL+hline(inner)+BoxBR))
}

func fmtConfigValue(v interface{}) string {
	switch val := v.(type) {
	case string:
		return paint(cString, `"`+val+`"`)
	case bool:
		return paint(cBool, fmt.Sprintf("%v", val))
	case int, int64, float64:
		return paint(cNumber, fmt.Sprintf("%v", val))
	case []interface{}:
		if len(val) == 0 {
			return paint(cNull, "[]")
		}
		parts := make([]string, len(val))
		for i, item := range val {
			parts[i] = fmtConfigValue(item)
		}
		return "[" + strings.Join(parts, ", ") + "]"
	case nil:
		return paint(cNull, "null")
	default:
		return paint(cValue, fmt.Sprintf("%v", val))
	}
}

// ── Rich traceback ─────────────────────────────────────────────────────────────

// Frame represents one stack frame in a traceback.
type Frame struct {
	File   string
	Line   int
	Func   string
	Code   []CodeLine
	Locals map[string]string
}

// CodeLine is one source line in a frame.
type CodeLine struct {
	Number    int
	Text      string
	IsPointer bool
}

// Traceback renders a rich-style traceback to stderr.
func Traceback(errType, errMsg string, frames []Frame) {
	w := TermWidth()
	inner := w - 2

	emit := func(text string) {
		pad := inner - len(StripANSI(text)) - 1
		if pad < 0 {
			pad = 0
		}
		fmt.Fprintf(os.Stderr, "%s %s%s %s\n",
			paint(cTBBorder, BoxV),
			text, strings.Repeat(" ", pad),
			paint(cTBBorder, BoxV))
	}
	empty := func() {
		fmt.Fprintf(os.Stderr, "%s%s%s\n",
			paint(cTBBorder, BoxV),
			strings.Repeat(" ", inner),
			paint(cTBBorder, BoxV))
	}

	hdr := " Traceback (most recent call last) "
	right := inner - len(hdr) - 3
	if right < 0 {
		right = 0
	}
	fmt.Fprintf(os.Stderr, "%s%s%s\n",
		paint(cTBBorder, BoxTL+hline(3)),
		paint(cTBTitle, hdr),
		paint(cTBBorder, hline(right)+BoxTR))

	for _, frame := range frames {
		loc := paint(cTBFile, frame.File) +
			":" + paint(cTBLineNum, fmt.Sprintf("%d", frame.Line)) +
			" in " + paint(cTBFunc, frame.Func)
		emit(loc)
		empty()

		sep := paint(cTBBorder, " "+BoxV+" ")
		for _, cl := range frame.Code {
			num := fmt.Sprintf("%4d", cl.Number)
			if cl.IsPointer {
				emit(paint(cTBHigh, " "+SymPtr+" "+num) + sep + paint(cTBHigh, cl.Text))
			} else {
				emit("   " + paint(cMuted, num) + sep + paint(cTBCode, cl.Text))
			}
		}

		if len(frame.Locals) > 0 {
			empty()
			locTitle := paint(cTBLocals, " locals ") +
				paint(cTBBorder, hline(inner-12))
			emit(locTitle)
			for k, v := range frame.Locals {
				emit(paint(cTBBorder, BoxV+"  ") +
					paint(cKey, k) + " = " + paint(cValue, v))
			}
		}
		empty()
	}

	fmt.Fprintf(os.Stderr, "%s\n", paint(cTBBorder, BoxBL+hline(inner)+BoxBR))
	fmt.Fprintf(os.Stderr, "%s: %s\n", paint(cTBErrType, errType), paint(cTBErrMsg, errMsg))
}
