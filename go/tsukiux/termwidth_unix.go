//go:build !windows

package tsukiux

import (
	"fmt"
	"os"
	"syscall"
	"unsafe"
)

type winsize struct {
	Row, Col, Xpixel, Ypixel uint16
}

// TermWidth returns the real terminal column width, falling back to 100.
func TermWidth() int {
	var ws winsize
	if _, _, errno := syscall.Syscall(
		syscall.SYS_IOCTL,
		uintptr(syscall.Stdout),
		uintptr(syscall.TIOCGWINSZ),
		uintptr(unsafe.Pointer(&ws)),
	); errno == 0 && ws.Col > 0 {
		return int(ws.Col)
	}
	if col := os.Getenv("COLUMNS"); col != "" {
		var w int
		if _, err := fmt.Sscanf(col, "%d", &w); err == nil && w > 0 {
			return w
		}
	}
	return 100
}