//go:build !linux && !darwin && !freebsd && !openbsd && !netbsd && !windows

package tsukiux

func enableRaw() (restore func(), err error) {
	return func() {}, nil
}