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

// ── LiveBlock ─────────────────────────────────────────────────────────────────

// LiveBlock is a Docker-style collapsible command-output block.
//
// Success (collapsed):
//
//	✔  cargo build --release  [3.2s]
//
// Failure (expanded):
//
//	✖  cargo build --release
//	│  error: use of moved value
//	╰─ exit 1
type LiveBlock struct {
	label   string
	lines   []string
	start   time.Time
	isTTY   bool
	stopped chan struct{}
	done    bool
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
		fmt.Printf("  %s%s%s  %s\n", a(ansiDim), SymEll, a(ansiReset), b.label)
		return
	}
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
			paint(cMuted, SymPipe), a(ansiDim), s, a(ansiReset))
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

// Lines feeds multiple lines at once.
func (b *LiveBlock) Lines(lines []string) {
	for _, l := range lines {
		b.Line(l)
	}
}

// UpdateLabel changes the label shown next to the spinner mid-run.
func (b *LiveBlock) UpdateLabel(label string) {
	b.mu.Lock()
	b.label = label
	b.mu.Unlock()
}

// Finish collapses (ok=true) or expands (ok=false) the block.
func (b *LiveBlock) Finish(ok bool, summary string) {
	elapsed := time.Since(b.start)

	if b.isTTY {
		b.mu.Lock()
		if b.done {
			b.mu.Unlock()
			return
		}
		b.done = true
		b.mu.Unlock()

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
				a(ansiDim), formatElapsed(elapsed), a(ansiReset))
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
			fmt.Fprintf(&buf, "  %s%s %s%s\n", a(ansiDim), BoxBL+BoxH, msg, a(ansiReset))
		}
		buf.WriteString("\033[?25h")
		fmt.Fprint(os.Stdout, buf.String())
	} else {
		if ok {
			fmt.Printf("  %s  %s  %s[%s]%s\n",
				paint(cSuccess, SymOK),
				b.label,
				a(ansiDim), formatElapsed(elapsed), a(ansiReset))
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
			fmt.Printf("  %s%s %s%s\n", a(ansiDim), BoxBL+BoxH, msg, a(ansiReset))
		}
	}
}

// ── Spinner ───────────────────────────────────────────────────────────────────

// Spinner is a lightweight standalone spinner — no output lines, just an
// animated label that collapses to a single success/fail line when stopped.
//
// Use LiveBlock when you need to stream command output alongside the spinner.
// Use Spinner for simple "waiting…" states.
type Spinner struct {
	label   string
	frames  []string
	isTTY   bool
	stopped chan struct{}
	done    bool
	mu      sync.Mutex
	start   time.Time
}

// NewSpinner creates a spinner with the default braille frames.
func NewSpinner(label string) *Spinner {
	return NewSpinnerWithFrames(label, SpinnerFrames)
}

// NewSpinnerWithFrames creates a spinner with custom animation frames.
func NewSpinnerWithFrames(label string, frames []string) *Spinner {
	fi, err := os.Stdout.Stat()
	isTTY := err == nil && (fi.Mode()&os.ModeCharDevice) != 0
	return &Spinner{
		label:   label,
		frames:  frames,
		isTTY:   isTTY,
		stopped: make(chan struct{}),
		start:   time.Now(),
	}
}

// Start begins the spinner animation.
func (s *Spinner) Start() {
	if !s.isTTY {
		fmt.Printf("  %s%s%s  %s\n", a(ansiDim), SymEll, a(ansiReset), s.label)
		return
	}
	fmt.Printf("\033[?25l  %s  %s\033[K", paint(cInfo, s.frames[0]), s.label)
	go s.spin()
}

func (s *Spinner) spin() {
	i := 1
	ticker := time.NewTicker(100 * time.Millisecond)
	defer ticker.Stop()
	for {
		select {
		case <-s.stopped:
			return
		case <-ticker.C:
			frame := s.frames[i%len(s.frames)]
			i++
			s.mu.Lock()
			fmt.Printf("\r  %s  %s\033[K", paint(cInfo, frame), s.label)
			s.mu.Unlock()
		}
	}
}

// Stop finalizes the spinner.
//
//	ok=true  →  ✔  label  [1.2s]
//	ok=false →  ✖  label  reason
func (s *Spinner) Stop(ok bool, msg string) {
	elapsed := time.Since(s.start)

	if s.isTTY {
		s.mu.Lock()
		if s.done {
			s.mu.Unlock()
			return
		}
		s.done = true
		s.mu.Unlock()

		close(s.stopped)
		time.Sleep(80 * time.Millisecond)

		s.mu.Lock()
		defer s.mu.Unlock()
		if ok {
			suffix := ""
			if msg != "" {
				suffix = "  " + paint(cMuted, msg)
			}
			fmt.Printf("\r\033[K  %s  %s  %s[%s]%s%s\n",
				paint(cSuccess, SymOK), s.label,
				a(ansiDim), formatElapsed(elapsed), a(ansiReset),
				suffix)
		} else {
			reason := msg
			if reason == "" {
				reason = "failed"
			}
			fmt.Printf("\r\033[K  %s  %s  %s%s%s\n",
				paint(cError, SymFail), s.label,
				a(ansiDim), reason, a(ansiReset))
		}
		fmt.Print("\033[?25h")
	} else {
		if ok {
			fmt.Printf("  %s  %s  [%s]\n", paint(cSuccess, SymOK), s.label, formatElapsed(elapsed))
		} else {
			fmt.Printf("  %s  %s\n", paint(cError, SymFail), s.label)
		}
	}
}

// StopSilent collapses the spinner as a success without timing info.
func (s *Spinner) StopSilent() {
	if s.isTTY {
		s.mu.Lock()
		if s.done {
			s.mu.Unlock()
			return
		}
		s.done = true
		s.mu.Unlock()

		close(s.stopped)
		time.Sleep(80 * time.Millisecond)
		s.mu.Lock()
		defer s.mu.Unlock()
		fmt.Printf("\r\033[K  %s  %s\n", paint(cSuccess, SymOK), s.label)
		fmt.Print("\033[?25h")
	} else {
		fmt.Printf("  %s  %s\n", paint(cSuccess, SymOK), s.label)
	}
}

// UpdateLabel changes the spinner's label mid-animation.
func (s *Spinner) UpdateLabel(label string) {
	s.mu.Lock()
	s.label = label
	s.mu.Unlock()
}