//go:build linux

package tsukiux

import (
	"syscall"
	"unsafe"
)

const (
	_TCGETS  = uintptr(0x5401)
	_TCSETS  = uintptr(0x5402)
	_ICANON  = uint32(0x00000002)
	_ECHO    = uint32(0x00000008)
	_ISIG    = uint32(0x00000001)
	_IEXTEN  = uint32(0x00008000)
	_ICRNL   = uint32(0x00000100)
	_IXON    = uint32(0x00000400)
)

type _termios struct {
	Iflag  uint32
	Oflag  uint32
	Cflag  uint32
	Lflag  uint32
	Line   uint8
	Cc     [19]uint8
	_      [3]byte
	Ispeed uint32
	Ospeed uint32
}

func enableRaw() (restore func(), err error) {
	var orig _termios
	if _, _, e := syscall.Syscall(syscall.SYS_IOCTL, 0, _TCGETS, uintptr(unsafe.Pointer(&orig))); e != 0 {
		return func() {}, e
	}
	raw := orig
	raw.Lflag &^= _ICANON | _ECHO | _ISIG | _IEXTEN
	raw.Iflag &^= _ICRNL | _IXON
	raw.Cc[6] = 1 // VMIN — return after 1 byte
	raw.Cc[5] = 0 // VTIME — no timeout
	if _, _, e := syscall.Syscall(syscall.SYS_IOCTL, 0, _TCSETS, uintptr(unsafe.Pointer(&raw))); e != 0 {
		return func() {}, e
	}
	return func() {
		syscall.Syscall(syscall.SYS_IOCTL, 0, _TCSETS, uintptr(unsafe.Pointer(&orig)))
	}, nil
}