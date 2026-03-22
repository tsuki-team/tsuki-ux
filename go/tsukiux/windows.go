//go:build windows

package tsukiux

import (
	"syscall"
	"unsafe"
)

// ── Shared Windows kernel32 handles ──────────────────────────────────────────

var (
	kernel32                    = syscall.NewLazyDLL("kernel32.dll")
	procGetConsoleScreenBufferInfo = kernel32.NewProc("GetConsoleScreenBufferInfo")
	procGetConsoleMode           = kernel32.NewProc("GetConsoleMode")
	procSetConsoleMode           = kernel32.NewProc("SetConsoleMode")
)

// ── Types for GetConsoleScreenBufferInfo ──────────────────────────────────────

type coord struct {
	X, Y int16
}

type smallRect struct {
	Left, Top, Right, Bottom int16
}

type consoleScreenBufferInfo struct {
	Size              coord
	CursorPosition    coord
	Attributes        uint16
	Window            smallRect
	MaximumWindowSize coord
}

// ── Raw mode ──────────────────────────────────────────────────────────────────

const (
	_ENABLE_ECHO_INPUT             = 0x0004
	_ENABLE_LINE_INPUT             = 0x0002
	_ENABLE_PROCESSED_INPUT        = 0x0001
	_ENABLE_VIRTUAL_TERMINAL_INPUT = 0x0200
)

func enableRaw() (restore func(), err error) {
	handle, err := syscall.GetStdHandle(syscall.STD_INPUT_HANDLE)
	if err != nil {
		return func() {}, err
	}
	var origMode uint32
	r, _, e := procGetConsoleMode.Call(uintptr(handle), uintptr(unsafe.Pointer(&origMode)))
	if r == 0 {
		return func() {}, e
	}
	rawMode := origMode &^ uint32(_ENABLE_ECHO_INPUT|_ENABLE_LINE_INPUT|_ENABLE_PROCESSED_INPUT)
	rawMode |= _ENABLE_VIRTUAL_TERMINAL_INPUT
	procSetConsoleMode.Call(uintptr(handle), uintptr(rawMode))
	return func() {
		procSetConsoleMode.Call(uintptr(handle), uintptr(origMode))
	}, nil
}