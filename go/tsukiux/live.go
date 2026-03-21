package tsukiux

import (
	"fmt"
	"os"
	"strings"
	"sync"
	"time"
)

// LiveLines is the number of content rows in the rolling window.
const LiveLines = 6

// LiveBlock is a Docker-style collapsible command-output block.
//
// Success (collapsed):
//   ✔  cargo build --release  [3.2s]
//
// Failure (expanded):
//   ✖  cargo build --release
//   │  error: use of moved value
//   ╰─ exit 1
type LiveBlock struct {
	label   string
	lines   []string
	start   time.Time
	isTTY   bool
	stopped chan struct{}
	mu      sync.Mutex
	painted int
}

// NewLiveBlock creates a new block with the given header label.
func NewLiveBlock(label string) *LiveBlock {
	fi, err := os.Stdout.Stat()
	isTTY := err == nil && (fi.Mode()&os.ModeCharDevice) != 0
	return &LiveBlock{
		label:   label,
		start:   time.Now(),
		isTTY:   isTTY,
		stopped: make(chan struct{}),
	}
}

// Start prints the spinner header and begins animation.
func (b *LiveBlock) Start() {
	if !b.isTTY {
		fmt.Printf("  %s%s%s  %s\n", a(dim), SymEll, a(reset), b.label)
		return
	}
	// Hide cursor + first frame, no trailing \n.
	fmt.Printf("\033[?25l  %s  %s\033[K", paint(cInfo, SpinnerFrames[0]), b.label)
	go b.spin()
}

func (b *LiveBlock) spin() {
	i := 0
	ticker := time.NewTicker(100 * time.Millisecond)
	defer ticker.Stop()
	for {
		select {
		case <-b.stopped:
			return
		case <-ticker.C:
			frame := SpinnerFrames[i%len(SpinnerFrames)]
			i++
			b.mu.Lock()
			b.redraw(frame)
			b.mu.Unlock()
		}
	}
}

func (b *LiveBlock) redraw(frame string) {
	w := TermWidth()
	var buf strings.Builder

	buf.WriteString("\r")
	if b.painted > 0 {
		fmt.Fprintf(&buf, "\033[%dA", b.painted)
	}
	buf.WriteString("\033[J")

	start := len(b.lines) - LiveLines
	if start < 0 {
		start = 0
	}
	visible := b.lines[start:]
	colW := w - 8
	for _, s := range visible {
		if len([]rune(s)) > colW {
			s = string([]rune(s)[:colW])
		}
		fmt.Fprintf(&buf, "  %s  %s%s%s\n",
			paint(cMuted, SymPipe), a(dim), s, a(reset))
	}
	fmt.Fprintf(&buf, "  %s  %s\033[K", paint(cInfo, frame), b.label)

	fmt.Fprint(os.Stdout, buf.String())
	b.painted = len(visible)
}

// Line buffers a content line.
// TTY: picked up by the spinner on the next tick.
// Non-TTY: printed immediately for log capture.
func (b *LiveBlock) Line(s string) {
	b.mu.Lock()
	b.lines = append(b.lines, s)
	b.mu.Unlock()

	if !b.isTTY && s != "" {
		w := TermWidth()
		fmt.Printf("  %s  %s\n", paint(cMuted, SymPipe), truncate(s, w-8))
	}
}

// Finish collapses (ok=true) or expands (ok=false) the block.
func (b *LiveBlock) Finish(ok bool, summary string) {
	elapsed := time.Since(b.start)

	if b.isTTY {
		close(b.stopped)
		time.Sleep(120 * time.Millisecond)

		b.mu.Lock()
		defer b.mu.Unlock()

		var buf strings.Builder
		buf.WriteString("\r")
		if b.painted > 0 {
			fmt.Fprintf(&buf, "\033[%dA", b.painted)
		}
		buf.WriteString("\033[J")

		if ok {
			fmt.Fprintf(&buf, "  %s  %s  %s[%s]%s\n",
				paint(cSuccess, SymOK),
				b.label,
				a(dim), formatElapsed(elapsed), a(reset))
		} else {
			fmt.Fprintf(&buf, "  %s  %s\n", paint(cError, SymFail), b.label)
			w := TermWidth()
			for _, l := range b.lines {
				if l != "" {
					fmt.Fprintf(&buf, "  %s  %s\n",
						paint(cMuted, SymPipe), truncate(l, w-8))
				}
			}
			msg := summary
			if msg == "" {
				msg = "failed"
			}
			fmt.Fprintf(&buf, "  %s%s %s%s\n", a(dim), BoxBL+BoxH, msg, a(reset))
		}
		buf.WriteString("\033[?25h")
		fmt.Fprint(os.Stdout, buf.String())
	} else {
		if ok {
			fmt.Printf("  %s  %s  %s[%s]%s\n",
				paint(cSuccess, SymOK),
				b.label,
				a(dim), formatElapsed(elapsed), a(reset))
		} else {
			fmt.Printf("  %s  %s\n", paint(cError, SymFail), b.label)
			w := TermWidth()
			for _, l := range b.lines {
				if l != "" {
					fmt.Printf("  %s  %s\n",
						paint(cMuted, SymPipe), truncate(l, w-8))
				}
			}
			msg := summary
			if msg == "" {
				msg = "failed"
			}
			fmt.Printf("  %s%s %s%s\n", a(dim), BoxBL+BoxH, msg, a(reset))
		}
	}
}

func formatElapsed(d time.Duration) string {
	if d < time.Second {
		return fmt.Sprintf("%dms", d.Milliseconds())
	}
	return fmt.Sprintf("%.1fs", d.Seconds())
}
