//go:build darwin || freebsd || openbsd || netbsd

package tsukiux

import (
	"syscall"
	"unsafe"
)

const (
	_TIOCGETA = uintptr(0x40487413)
	_TIOCSETA = uintptr(0x80487414)
	_ICANON   = uint32(0x00000100)
	_ECHO     = uint32(0x00000008)
	_ISIG     = uint32(0x00000080)
	_IEXTEN   = uint32(0x00000400)
	_ICRNL    = uint32(0x00000100)
	_IXON     = uint32(0x00000200)
)

type _termios struct {
	Iflag  uint32
	Oflag  uint32
	Cflag  uint32
	Lflag  uint32
	Cc     [20]uint8
	Ispeed uint32
	Ospeed uint32
}

func enableRaw() (restore func(), err error) {
	var orig _termios
	if _, _, e := syscall.Syscall(syscall.SYS_IOCTL, 0, _TIOCGETA, uintptr(unsafe.Pointer(&orig))); e != 0 {
		return func() {}, e
	}
	raw := orig
	raw.Lflag &^= _ICANON | _ECHO | _ISIG | _IEXTEN
	raw.Iflag &^= _ICRNL | _IXON
	raw.Cc[16] = 1 // VMIN (darwin index)
	raw.Cc[17] = 0 // VTIME (darwin index)
	if _, _, e := syscall.Syscall(syscall.SYS_IOCTL, 0, _TIOCSETA, uintptr(unsafe.Pointer(&raw))); e != 0 {
		return func() {}, e
	}
	return func() {
		syscall.Syscall(syscall.SYS_IOCTL, 0, _TIOCSETA, uintptr(unsafe.Pointer(&orig)))
	}, nil
}