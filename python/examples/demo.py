#!/usr/bin/env python3
"""
tsuki_ux demo — all primitives in action.
Run:  python examples/demo.py
"""

import time
import sys
import os

# Allow running from the repo root without installing
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tsuki_ux import (
    success, fail, warn, info, step, note,
    artifact, header, section, section_end,
    progress_bar, LiveBlock, Spinner, box, config_table, ConfigEntry,
    traceback_box, Frame, CodeLine,
)


def demo_primitives():
    header("tsuki-ux demo")

    step("Output primitives")
    success("compilación terminada")
    fail("error: archivo no encontrado", file=sys.stdout)
    warn("versión antigua detectada")
    info("usando caché local")
    note("timestamp: 2026-03-21T10:00:00Z")


def demo_section():
    section("Platform: linux-amd64")
    artifact("tsuki-linux-amd64.tar.gz", "4.2 MB")
    artifact("tsuki-flash-linux-amd64", "2.1 MB")
    section_end()


def demo_progress():
    step("Progress bar")
    for i in range(0, 41, 8):
        print(f"\033[1A\033[K", end="")  # erase previous bar
        progress_bar("compiling", i, 40)
        time.sleep(0.1)


def demo_spinner():
    step("Spinner (standalone)")
    s = Spinner("Detectando puerto serie…")
    s.start()
    time.sleep(1.5)
    s.stop(ok=True, msg="Puerto detectado: /dev/ttyUSB0")


def demo_liveblock_success():
    step("LiveBlock — éxito (colapsa)")
    blk = LiveBlock("cargo build --release --target avr-atmega328p")
    blk.start()
    lines = [
        "   Compiling proc-macro2 v1.0.94",
        "   Compiling quote v1.0.40",
        "   Compiling syn v2.0.100",
        "   Compiling tsuki-flash v4.0.0",
        "    Finished release [optimized] target(s) in 3.24s",
    ]
    for l in lines:
        blk.line(l)
        time.sleep(0.18)
    blk.finish(ok=True)


def demo_liveblock_failure():
    step("LiveBlock — fallo (expande)")
    blk = LiveBlock("avrdude -p atmega328p -c arduino -P /dev/ttyUSB0")
    blk.start()
    error_lines = [
        "avrdude: ser_open(): can't open device \"/dev/ttyUSB0\"",
        "avrdude: serial port open: No such file or directory",
    ]
    for l in error_lines:
        blk.line(l)
        time.sleep(0.3)
    blk.finish(ok=False, summary="exit 1")


def demo_context_manager():
    step("LiveBlock — context manager")
    with LiveBlock("npm install") as b:
        b.line("added 312 packages")
        b.line("found 0 vulnerabilities")
        time.sleep(0.5)


def demo_box():
    step("Box / Panel")
    box(
        "board      =  \"arduino-nano\"\n"
        "port       =  \"/dev/ttyUSB0\"\n"
        "baud_rate  =  115200",
        title="tsuki config",
        out=sys.stdout,
    )


def demo_config_table():
    step("Config table")
    config_table("tsuki.json", [
        ConfigEntry("board",      "arduino-nano"),
        ConfigEntry("port",       "/dev/ttyUSB0"),
        ConfigEntry("baud_rate",  115200,   "velocidad serie"),
        ConfigEntry("flash_mode", "tsuki-flash"),
        ConfigEntry("verbose",    False),
    ])


def demo_traceback():
    step("Rich traceback")
    traceback_box(
        err_type="ZeroDivisionError",
        err_msg="division by zero",
        frames=[
            Frame(
                file="main.go",
                line=21,
                func="divide_all",
                code=[
                    CodeLine(19, "for n, d in divides:"),
                    CodeLine(20, "    result = divide_by(n, d)", is_pointer=False),
                    CodeLine(21, "    result = divide_by(n, d)", is_pointer=True),
                    CodeLine(22, "    print(f\"{n} / {d} = {result}\")"),
                ],
                locals={"divides": "[(1000, 200), ...]", "divisor": "0"},
            ),
        ],
        out=sys.stdout,
    )


if __name__ == "__main__":
    demo_primitives()
    demo_section()
    demo_progress()
    demo_spinner()
    demo_liveblock_success()
    demo_liveblock_failure()
    demo_context_manager()
    demo_box()
    demo_config_table()
    demo_traceback()

    print()
    success("Demo completo")
