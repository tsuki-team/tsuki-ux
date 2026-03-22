package tsukiux

import (
	"fmt"
	"os"
	"strings"
)

// ── Key codes ─────────────────────────────────────────────────────────────────

type keyCode int

const (
	keyNone keyCode = iota
	keyUp
	keyDown
	keyLeft
	keyRight
	keyEnter
	keySpace
	keyEsc
	keyBackspace
	keyDelete
	keyCtrlC
	keyRune
)

type keyPress struct {
	code keyCode
	r    rune
}

// readKey reads one logical key press from stdin.
// Handles multi-byte escape sequences (arrows, etc.).
func readKey() keyPress {
	buf := make([]byte, 1)
	os.Stdin.Read(buf) //nolint:errcheck

	switch buf[0] {
	case '\r', '\n':
		return keyPress{code: keyEnter}
	case ' ':
		return keyPress{code: keySpace}
	case 27: // ESC or escape sequence
		seq := make([]byte, 2)
		n, _ := os.Stdin.Read(seq)
		if n == 0 {
			return keyPress{code: keyEsc}
		}
		if seq[0] == '[' && n >= 2 {
			switch seq[1] {
			case 'A':
				return keyPress{code: keyUp}
			case 'B':
				return keyPress{code: keyDown}
			case 'C':
				return keyPress{code: keyRight}
			case 'D':
				return keyPress{code: keyLeft}
			case '3': // DEL sequence: \x1b[3~
				extra := make([]byte, 1)
				os.Stdin.Read(extra) //nolint:errcheck
				return keyPress{code: keyDelete}
			}
		}
		return keyPress{code: keyEsc}
	case 3: // Ctrl+C
		return keyPress{code: keyCtrlC}
	case 127, 8: // Backspace
		return keyPress{code: keyBackspace}
	case 0xe0: // Windows arrow prefix
		seq := make([]byte, 1)
		os.Stdin.Read(seq) //nolint:errcheck
		switch seq[0] {
		case 0x48:
			return keyPress{code: keyUp}
		case 0x50:
			return keyPress{code: keyDown}
		case 0x4B:
			return keyPress{code: keyLeft}
		case 0x4D:
			return keyPress{code: keyRight}
		case 0x53:
			return keyPress{code: keyDelete}
		}
	default:
		if buf[0] >= 32 {
			return keyPress{code: keyRune, r: rune(buf[0])}
		}
	}
	return keyPress{code: keyNone}
}

// ── Fallback (non-TTY) ────────────────────────────────────────────────────────

func selectFallback(prompt string, items []string) (int, bool) {
	fmt.Printf("\n  %s%s%s  %s\n", a(ansiBold), SymStep, a(ansiReset), prompt)
	for i, item := range items {
		fmt.Printf("    %s%d.%s  %s\n", a(cMuted), i+1, a(ansiReset), item)
	}
	fmt.Printf("  Enter number (1-%d): ", len(items))
	var n int
	fmt.Scan(&n)
	if n < 1 || n > len(items) {
		return -1, false
	}
	return n - 1, true
}

func confirmFallback(prompt string, defaultYes bool) bool {
	hint := "Y/n"
	if !defaultYes {
		hint = "y/N"
	}
	fmt.Printf("\n  %s%s%s  %s (%s): ", a(ansiBold), SymStep, a(ansiReset), prompt, hint)
	var resp string
	fmt.Scan(&resp)
	resp = strings.ToLower(strings.TrimSpace(resp))
	if resp == "" {
		return defaultYes
	}
	return resp == "y" || resp == "yes"
}

func inputFallback(prompt, placeholder string) (string, bool) {
	hint := ""
	if placeholder != "" {
		hint = fmt.Sprintf(" %s[%s]%s", a(cMuted), placeholder, a(ansiReset))
	}
	fmt.Printf("\n  %s%s%s  %s%s: ", a(ansiBold), SymStep, a(ansiReset), prompt, hint)
	var resp string
	fmt.Scan(&resp)
	if resp == "" {
		resp = placeholder
	}
	return resp, true
}

// ── Internal drawing helpers ──────────────────────────────────────────────────

const (
	menuHintColor = cMuted
	menuHint      = "↑↓ navegar  Enter confirmar  Esc cancelar"
	multiHint     = "↑↓ navegar  Espacio seleccionar  Enter confirmar  Esc cancelar"
)

func clearLines(n int) {
	if n > 0 {
		fmt.Printf("\033[%dA\033[J", n)
	}
}

func hideCursor() { fmt.Print("\033[?25l") }
func showCursor() { fmt.Print("\033[?25h") }

// ── Select ────────────────────────────────────────────────────────────────────

// Select shows an interactive arrow-key single-selection menu.
//
//	▶  Choose board
//	   ❱ arduino-nano          ← highlighted
//	     arduino-uno
//	     esp32-devkit
//	   ↑↓ navegar  Enter confirmar  Esc cancelar
//
// Returns (selectedIndex, true) or (-1, false) if cancelled.
func Select(prompt string, items []string) (int, bool) {
	if len(items) == 0 {
		return -1, false
	}
	if !IsTTY() {
		return selectFallback(prompt, items)
	}

	restore, err := enableRaw()
	if err != nil {
		return selectFallback(prompt, items)
	}
	defer restore()

	cursor := 0
	maxVisible := 8
	offset := 0 // scroll offset

	draw := func(linesDrawn int) int {
		clearLines(linesDrawn)
		lines := 0

		// Header
		fmt.Printf("\n  %s  %s%s%s\n", paint(cStep, SymStep), a(ansiBold), prompt, a(ansiReset))
		lines += 2

		// Items
		end := offset + maxVisible
		if end > len(items) {
			end = len(items)
		}
		for i := offset; i < end; i++ {
			item := items[i]
			if i == cursor {
				fmt.Printf("    %s %s%s%s\n",
					paint(cInfo, SymPtr),
					a(cAccent+ansiBold),
					item,
					a(ansiReset))
			} else {
				fmt.Printf("      %s%s%s\n", a(cMuted), item, a(ansiReset))
			}
			lines++
		}
		if len(items) > maxVisible {
			fmt.Printf("      %s(%d/%d)%s\n", a(cMuted), cursor+1, len(items), a(ansiReset))
			lines++
		}

		// Hint
		fmt.Printf("    %s%s%s\n", a(cMuted), menuHint, a(ansiReset))
		lines++
		return lines
	}

	hideCursor()
	defer showCursor()

	linesDrawn := 0
	linesDrawn = draw(linesDrawn)

	for {
		k := readKey()
		switch k.code {
		case keyUp:
			if cursor > 0 {
				cursor--
				if cursor < offset {
					offset--
				}
			}
		case keyDown:
			if cursor < len(items)-1 {
				cursor++
				if cursor >= offset+maxVisible {
					offset++
				}
			}
		case keyEnter:
			clearLines(linesDrawn)
			fmt.Printf("  %s  %s: %s%s%s\n",
				paint(cSuccess, SymOK),
				prompt,
				a(cAccent),
				items[cursor],
				a(ansiReset))
			return cursor, true
		case keyEsc, keyCtrlC:
			clearLines(linesDrawn)
			fmt.Printf("  %s  %s%s%s\n",
				paint(cMuted, SymDash),
				a(cMuted), prompt+" cancelado", a(ansiReset))
			return -1, false
		}
		linesDrawn = draw(linesDrawn)
	}
}

// ── MultiSelect ───────────────────────────────────────────────────────────────

// MultiSelect shows an interactive multi-selection menu with Space to toggle.
//
//	▶  Select packages
//	   ❱ [✔] dht
//	     [ ] ws2812
//	     [✔] mpu6050
//	   ↑↓ navegar  Espacio seleccionar  Enter confirmar  Esc cancelar
//
// Returns ([]selectedIndices, true) or (nil, false) if cancelled.
func MultiSelect(prompt string, items []string, defaultSelected ...int) ([]int, bool) {
	if len(items) == 0 {
		return nil, false
	}
	if !IsTTY() {
		idx, ok := selectFallback(prompt+" (elige varios)", items)
		if !ok {
			return nil, false
		}
		return []int{idx}, true
	}

	restore, err := enableRaw()
	if err != nil {
		idx, ok := selectFallback(prompt, items)
		if !ok {
			return nil, false
		}
		return []int{idx}, true
	}
	defer restore()

	selected := make([]bool, len(items))
	for _, i := range defaultSelected {
		if i >= 0 && i < len(items) {
			selected[i] = true
		}
	}

	cursor := 0
	maxVisible := 8
	offset := 0

	drawCheck := func(checked bool) string {
		if checked {
			return paint(cSuccess, "[✔]")
		}
		return paint(cMuted, "[ ]")
	}

	draw := func(linesDrawn int) int {
		clearLines(linesDrawn)
		lines := 0

		fmt.Printf("\n  %s  %s%s%s\n", paint(cStep, SymStep), a(ansiBold), prompt, a(ansiReset))
		lines += 2

		end := offset + maxVisible
		if end > len(items) {
			end = len(items)
		}
		for i := offset; i < end; i++ {
			item := items[i]
			check := drawCheck(selected[i])
			if i == cursor {
				fmt.Printf("    %s %s %s%s%s\n",
					paint(cInfo, SymPtr),
					check,
					a(cAccent+ansiBold), item, a(ansiReset))
			} else {
				fmt.Printf("      %s %s%s%s\n",
					check,
					a(ansiDim), item, a(ansiReset))
			}
			lines++
		}
		if len(items) > maxVisible {
			fmt.Printf("      %s(%d/%d)%s\n", a(cMuted), cursor+1, len(items), a(ansiReset))
			lines++
		}

		count := 0
		for _, s := range selected {
			if s {
				count++
			}
		}
		fmt.Printf("    %s%s  %s%d seleccionados%s\n", a(cMuted), multiHint, a(cAccent), count, a(ansiReset))
		lines++
		return lines
	}

	hideCursor()
	defer showCursor()

	linesDrawn := 0
	linesDrawn = draw(linesDrawn)

	for {
		k := readKey()
		switch k.code {
		case keyUp:
			if cursor > 0 {
				cursor--
				if cursor < offset {
					offset--
				}
			}
		case keyDown:
			if cursor < len(items)-1 {
				cursor++
				if cursor >= offset+maxVisible {
					offset++
				}
			}
		case keySpace:
			selected[cursor] = !selected[cursor]
		case keyEnter:
			var result []int
			for i, s := range selected {
				if s {
					result = append(result, i)
				}
			}
			clearLines(linesDrawn)
			if len(result) == 0 {
				fmt.Printf("  %s  %s: %snone%s\n",
					paint(cSuccess, SymOK), prompt, a(cMuted), a(ansiReset))
			} else {
				names := make([]string, len(result))
				for i, idx := range result {
					names[i] = items[idx]
				}
				fmt.Printf("  %s  %s: %s%s%s\n",
					paint(cSuccess, SymOK),
					prompt,
					a(cAccent),
					strings.Join(names, ", "),
					a(ansiReset))
			}
			return result, true
		case keyEsc, keyCtrlC:
			clearLines(linesDrawn)
			fmt.Printf("  %s  %s%s%s\n",
				paint(cMuted, SymDash),
				a(cMuted), prompt+" cancelado", a(ansiReset))
			return nil, false
		}
		linesDrawn = draw(linesDrawn)
	}
}

// ── Confirm ───────────────────────────────────────────────────────────────────

// Confirm shows a yes/no prompt and returns the user's choice.
//
//	▶  ¿Continuar? (Y/n)
func Confirm(prompt string, defaultYes bool) bool {
	if !IsTTY() {
		return confirmFallback(prompt, defaultYes)
	}

	hint := paint(cMuted, "(") + paint(cSuccess, "Y") + paint(cMuted, "/n)")
	if !defaultYes {
		hint = paint(cMuted, "(y/") + paint(cSuccess, "N") + paint(cMuted, ")")
	}
	fmt.Printf("\n  %s  %s%s%s %s ", paint(cStep, SymStep), a(ansiBold), prompt, a(ansiReset), hint)

	restore, err := enableRaw()
	if err != nil {
		return confirmFallback(prompt, defaultYes)
	}
	defer restore()

	for {
		k := readKey()
		switch k.code {
		case keyEnter:
			fmt.Println()
			if defaultYes {
				fmt.Printf("  %s  %s\n", paint(cSuccess, SymOK), prompt)
			} else {
				fmt.Printf("  %s  %s\n", paint(cMuted, SymDash), prompt)
			}
			return defaultYes
		case keyCtrlC, keyEsc:
			fmt.Println()
			fmt.Printf("  %s  %s%s%s\n", paint(cMuted, SymDash), a(cMuted), prompt+" cancelado", a(ansiReset))
			return false
		case keyRune:
			r := k.r
			fmt.Printf("%s\n", string(r))
			switch r {
			case 'y', 'Y':
				fmt.Printf("  %s  %s\n", paint(cSuccess, SymOK), prompt)
				return true
			case 'n', 'N':
				fmt.Printf("  %s  %s%s%s\n", paint(cMuted, SymDash), a(cMuted), prompt, a(ansiReset))
				return false
			}
		}
	}
}

// ── Input ─────────────────────────────────────────────────────────────────────

// Input shows a single-line text input prompt.
//
//	▶  Board name: arduino-nano█
//
// Returns (text, true) or ("", false) if cancelled.
// placeholder is shown in muted style when the input is empty.
func Input(prompt, placeholder string) (string, bool) {
	if !IsTTY() {
		return inputFallback(prompt, placeholder)
	}

	restore, err := enableRaw()
	if err != nil {
		return inputFallback(prompt, placeholder)
	}
	defer restore()

	buf := []rune{}

	draw := func() {
		fmt.Print("\r\033[K")
		display := string(buf)
		if display == "" && placeholder != "" {
			fmt.Printf("  %s  %s%s%s: %s%s%s",
				paint(cStep, SymStep),
				a(ansiBold), prompt, a(ansiReset),
				a(cMuted), placeholder, a(ansiReset))
		} else {
			fmt.Printf("  %s  %s%s%s: %s",
				paint(cStep, SymStep),
				a(ansiBold), prompt, a(ansiReset),
				display)
		}
	}

	fmt.Println()
	draw()

	hideCursor()
	defer showCursor()

	for {
		k := readKey()
		switch k.code {
		case keyEnter:
			result := string(buf)
			if result == "" {
				result = placeholder
			}
			fmt.Print("\r\033[K")
			fmt.Printf("  %s  %s: %s%s%s\n",
				paint(cSuccess, SymOK),
				prompt,
				a(cAccent), result, a(ansiReset))
			return result, true
		case keyEsc, keyCtrlC:
			fmt.Print("\r\033[K")
			fmt.Printf("  %s  %s%s%s\n",
				paint(cMuted, SymDash),
				a(cMuted), prompt+" cancelado", a(ansiReset))
			return "", false
		case keyBackspace, keyDelete:
			if len(buf) > 0 {
				buf = buf[:len(buf)-1]
			}
		case keyRune:
			buf = append(buf, k.r)
		}
		draw()
	}
}

// ── InputPassword ─────────────────────────────────────────────────────────────

// InputPassword is like Input but masks the typed characters with ●.
func InputPassword(prompt string) (string, bool) {
	if !IsTTY() {
		fmt.Printf("  %s  %s: ", paint(cStep, SymStep), prompt)
		var resp string
		fmt.Scan(&resp)
		return resp, true
	}

	restore, err := enableRaw()
	if err != nil {
		return "", false
	}
	defer restore()

	buf := []rune{}

	draw := func() {
		fmt.Print("\r\033[K")
		mask := strings.Repeat(SymDot, len(buf))
		fmt.Printf("  %s  %s%s%s: %s",
			paint(cStep, SymStep),
			a(ansiBold), prompt, a(ansiReset),
			paint(cMuted, mask))
	}

	fmt.Println()
	draw()

	hideCursor()
	defer showCursor()

	for {
		k := readKey()
		switch k.code {
		case keyEnter:
			result := string(buf)
			fmt.Print("\r\033[K")
			fmt.Printf("  %s  %s\n", paint(cSuccess, SymOK), prompt)
			return result, true
		case keyEsc, keyCtrlC:
			fmt.Print("\r\033[K")
			return "", false
		case keyBackspace, keyDelete:
			if len(buf) > 0 {
				buf = buf[:len(buf)-1]
			}
		case keyRune:
			buf = append(buf, k.r)
		}
		draw()
	}
}