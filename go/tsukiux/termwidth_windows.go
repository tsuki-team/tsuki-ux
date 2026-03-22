//go:build windows

package tsukiux

import (
	"fmt"
	"os"
	"syscall"
	"unsafe"
)

// TermWidth returns the real terminal column width, falling back to 100.
func TermWidth() int {
	handle, err := syscall.GetStdHandle(syscall.STD_OUTPUT_HANDLE)
	if err == nil {
		var info consoleScreenBufferInfo
		r, _, _ := procGetConsoleScreenBufferInfo.Call(uintptr(handle), uintptr(unsafe.Pointer(&info)))
		if r != 0 {
			w := int(info.Window.Right-info.Window.Left) + 1
			if w > 0 {
				return w
			}
		}
	}
	if col := os.Getenv("COLUMNS"); col != "" {
		var w int
		if _, err := fmt.Sscanf(col, "%d", &w); err == nil && w > 0 {
			return w
		}
	}
	return 100
}