#!/usr/bin/env python3
"""
tsuki_ux demo

Normal mode:       python examples/demo.py
Presentation mode: python examples/demo.py --presentation

Presentation mode is designed to be recorded as a GIF.
Recommended recorder: vhs (https://github.com/charmbracelet/vhs)

  Output demo.gif
  Set FontSize 14
  Set Width 900
  Set Height 600
  Type "python examples/demo.py --presentation"
  Enter
  Sleep 60s
"""

import sys, os, time, shutil, subprocess, textwrap
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from tsuki_ux import *


# ── Presentation helpers ───────────────────────────────────────────────────────

def clear_screen() -> None:
    print("\033[2J\033[H", end="", flush=True)


def pause(seconds: float) -> None:
    time.sleep(seconds)


def pres_title(title: str) -> None:
    clear_screen()
    w = 60
    bar = "─" * (w - 2)
    label = f"  🌙 tsuki-ux  ·  {title}"
    # 🌙 is 1 char but occupies 2 terminal columns — subtract 1 extra
    pad = max(0, w - len(label) - 1 - 1)
    print()
    print(f"  \033[2m╭{bar}╮\033[0m")
    print(f"  \033[2m│\033[0m\033[1;97m{label}{' ' * pad}\033[2m│\033[0m")
    print(f"  \033[2m╰{bar}╯\033[0m")
    print()
    pause(0.5)


# ── Full demo ──────────────────────────────────────────────────────────────────

def run_full():
    header("tsuki-ux demo")

    step("Status primitives")
    success("compilación terminada")
    successf("firmware listo: %s", "tsuki-flash v4.0.0")
    fail("error: archivo no encontrado", file=sys.stdout)
    warn("versión antigua detectada")
    info("usando caché local")
    note("timestamp: 2026-03-21T10:00:00Z")

    step("Layout")
    rule("plataformas soportadas")
    section("Platform: linux-amd64")
    artifact("tsuki-linux-amd64.tar.gz", "4.2 MB")
    artifact("tsuki-flash-linux-amd64", "2.1 MB")
    section_end()

    step("Inline content")
    badge_line("GO",  "info",      "transpilando firmware")
    badge_line("OK",  "success",   "compilación exitosa")
    badge_line("ERR", "error",     "puerto serie ocupado")
    badge_line("⚡",  "highlight", "tsuki-flash activo")
    blank()
    key_value("board", "arduino-nano"); key_valuef("baud", "%d", 115200)
    blank()
    check_list(
        ["go.mod configurado", "paquetes instalados", "board detectada", "puerto disponible"],
        [True, True, True, False],
    )
    blank()
    indent("avrdude: AVR device initialized\navrdude: verifying flash memory")

    step("Text decoration & color")
    print(f"  {bold('Negrita')}  {dim('Tenue')}  {italic('Cursiva')}")
    print(f"  {underline('Subrayado')}  {strike('Tachado')}  {overline('Sobrelineado')}")
    print(f"  {reverse('Invertido')}  {blink('Parpadeo')}")
    blank()
    print("  256-color: " + "  ".join(color256(n, "█") for n in [196,214,226,46,51,57,201]))
    print("  truecolor: " + "  ".join(truecolor(r,g,b,"█") for r,g,b in [(255,80,80),(255,165,0),(255,255,80),(80,255,80),(80,200,255),(160,80,255)]))
    blank()
    print(f"  {Style().bold().underline().fg(C_SUCCESS).paint('bold + underline + success')}")
    print(f"  {Style().strike().fg_rgb(200, 80, 80).paint('strike + truecolor')}")
    print(f"  {Style().italic().fg_256(208).bg_256(234).paint('italic + 256-color bg')}")
    print(f"  {Style().bold().reverse().fg(C_INFO).paint('bold + reverse + info')}")

    step("Progress bars")
    bars = [
        ("Block    [████████░░░░]", lambda i: progress_bar("compilando", i, 40)),
        ("Braille  ⣿⣿⣿⣿⣦⣀⣀⣀",     lambda i: progress_bar_braille("compilando", i, 40, 20)),
        ("Gradient [████▓▒░   ]",   lambda i: progress_bar_gradient("compilando", i, 40)),
        ("Slim     ▰▰▰▰▰▰▱▱▱▱",     lambda i: progress_bar_slim("compilando", i, 40, 30)),
        ("Arrow    [=======>--]",    lambda i: progress_bar_arrow("compilando", i, 40)),
        ("Dots     ●●●●●●●○○○",     lambda i: progress_bar_dots("compilando", i, 40, 30)),
        ("Squares  ▪▪▪▪▪▫▫▫▫▫",    lambda i: progress_bar_squares("compilando", i, 40, 30)),
        ("Steps    [■■■□□□□□]",     lambda i: progress_bar_steps("compilando", i // 5, 8)),
    ]
    for name, draw in bars:
        note(name)
        for i in range(0, 41, 8):
            print("\033[1A\033[K", end="")
            draw(i)
            time.sleep(0.05)

    step("Spinners")
    for label, frames in [
        ("Braille", SPINNER_FRAMES), ("Arrow", SPINNER_FRAMES_ARROW),
        ("Moon",    SPINNER_FRAMES_MOON), ("Bounce", SPINNER_FRAMES_BOUNCE),
        ("Pulse",   SPINNER_FRAMES_PULSE), ("Snake", SPINNER_FRAMES_SNAKE),
        ("Grow",    SPINNER_FRAMES_GROW), ("Toggle", SPINNER_FRAMES_TOGGLE),
    ]:
        s = Spinner(label, frames=frames)
        s.start(); time.sleep(0.7); s.stop(ok=True)

    step("LiveBlock — éxito")
    blk = LiveBlock("cargo build --release --target avr-atmega328p")
    blk.start()
    for l in ["   Compiling proc-macro2 v1.0.94", "   Compiling tsuki-flash v4.0.0",
              "    Finished release [optimized] in 3.24s"]:
        blk.line(l); time.sleep(0.18)
    blk.finish(ok=True)

    step("LiveBlock — fallo")
    blk2 = LiveBlock("avrdude -p atmega328p -P /dev/ttyUSB0")
    blk2.start()
    blk2.line('avrdude: ser_open(): can\'t open "/dev/ttyUSB0"')
    blk2.line("No such file or directory")
    time.sleep(0.4)
    blk2.finish(ok=False, summary="exit 1")

    step("Config table")
    config_table("tsuki.json", [
        ConfigEntry("board",      "arduino-nano"),
        ConfigEntry("port",       "/dev/ttyUSB0"),
        ConfigEntry("baud_rate",  115200,       "velocidad serie"),
        ConfigEntry("flash_mode", "tsuki-flash"),
        ConfigEntry("verbose",    False),
    ])

    step("Box")
    box('board   = "nano"\nbaud    = 115200\nbackend = tsuki-flash', title="tsuki config", out=sys.stdout)

    step("Traceback")
    traceback_box("RuntimeError", "buffer overflow", [Frame(
        file="main.go", line=42, func="read_sensor",
        code=[CodeLine(41,"buf := make([]byte, 4)"), CodeLine(42,"n, _ = port.Read(buf)", is_pointer=True)],
        locals={"buf": "[0 0 0 0]", "n": "8"},
    )], out=sys.stdout)

    print()
    success("Demo completo")


# ── Presentation mode ──────────────────────────────────────────────────────────

def run_presentation():
    # 1 — Status
    pres_title("status primitives")
    for fn in [
        lambda: success("compilación terminada"),
        lambda: successf("firmware listo: %s", "tsuki-flash v4.0.0"),
        lambda: fail("error: archivo no encontrado", file=sys.stdout),
        lambda: warn("versión antigua detectada"),
        lambda: info("usando caché local"),
        lambda: note("timestamp: 2026-03-21T10:00:00Z"),
    ]:
        fn(); pause(0.22)
    pause(1.0)

    # 2 — Inline content
    pres_title("inline content")
    for fn in [
        lambda: badge_line("GO",  "info",      "transpilando firmware"),
        lambda: badge_line("OK",  "success",   "compilación exitosa"),
        lambda: badge_line("ERR", "error",     "puerto serie ocupado"),
        lambda: badge_line("⚡",  "highlight", "tsuki-flash activo"),
    ]:
        fn(); pause(0.2)
    blank()
    key_value("board", "arduino-nano"); key_valuef("baud", "%d", 115200)
    pause(0.5)
    blank()
    check_list(
        ["go.mod configurado", "paquetes instalados", "board detectada", "puerto disponible"],
        [True, True, True, False],
    )
    pause(1.2)

    # 3 — Text styles
    pres_title("text decoration & color")
    for s in [
        f"  {bold('Negrita')}  {dim('Tenue')}  {italic('Cursiva')}",
        f"  {underline('Subrayado')}  {strike('Tachado')}  {overline('Sobrelineado')}",
        f"  {reverse('Invertido')}",
    ]:
        print(s); pause(0.35)
    blank()
    print("  256-color: ", end="", flush=True)
    for n in [196, 214, 226, 46, 51, 57, 201]:
        print(color256(n, "█") + "  ", end="", flush=True); pause(0.08)
    print()
    pause(0.2)
    print("  truecolor: ", end="", flush=True)
    for r, g, b in [(255,80,80),(255,165,0),(255,255,80),(80,255,80),(80,200,255),(160,80,255)]:
        print(truecolor(r,g,b,"█") + "  ", end="", flush=True); pause(0.08)
    print()
    pause(0.4)
    blank()
    for s in [
        Style().bold().underline().fg(C_SUCCESS).paint("bold + underline + success"),
        Style().strike().fg_rgb(200, 80, 80).paint("strike + truecolor"),
        Style().italic().fg_256(208).bg_256(234).paint("italic + 256-color bg"),
        Style().bold().reverse().fg(C_INFO).paint("bold + reverse + info"),
    ]:
        print(f"  {s}"); pause(0.25)
    pause(1.2)

    # 4 — Progress bars (fully animated)
    pres_title("progress bars")
    bars = [
        ("Block    [████████░░░░]", lambda i: progress_bar("compilando", i, 40)),
        ("Braille  ⣿⣿⣿⣿⣦⣀⣀⣀",     lambda i: progress_bar_braille("compilando", i, 40, 20)),
        ("Gradient [████▓▒░   ]",   lambda i: progress_bar_gradient("compilando", i, 40)),
        ("Slim     ▰▰▰▰▰▰▱▱▱▱",     lambda i: progress_bar_slim("compilando", i, 40, 30)),
        ("Arrow    [=======>--]",    lambda i: progress_bar_arrow("compilando", i, 40)),
        ("Dots     ●●●●●●●○○○",     lambda i: progress_bar_dots("compilando", i, 40, 30)),
    ]
    for name, draw in bars:
        note(name)
        for i in range(0, 41):
            print("\033[1A\033[K", end="")
            draw(i); time.sleep(0.035)
        pause(0.4)

    # 5 — Spinners
    pres_title("spinners")
    for label, frames in [
        ("Braille  ⠋⠙⠹⠸⠼⠴",   SPINNER_FRAMES),
        ("Arrow    ▸▹▹▹▹",      SPINNER_FRAMES_ARROW),
        ("Moon     🌑🌒🌓🌔",   SPINNER_FRAMES_MOON),
        ("Bounce   [●    ]",     SPINNER_FRAMES_BOUNCE),
        ("Pulse    ▏▎▍▌▋▊▉█",  SPINNER_FRAMES_PULSE),
        ("Snake    ⣿⣿⣿⣿⣿",     SPINNER_FRAMES_SNAKE),
        ("Grow     ▰▰▰▰▱▱▱▱",  SPINNER_FRAMES_GROW),
    ]:
        s = Spinner(label, frames=frames)
        s.start(); time.sleep(1.2); s.stop(ok=True)
        pause(0.12)
    pause(0.6)

    # 6 — LiveBlock
    pres_title("live block")
    pause(0.3)
    blk = LiveBlock("cargo build --release --target avr-atmega328p")
    blk.start()
    for l in [
        "   Compiling proc-macro2 v1.0.94",
        "   Compiling quote v1.0.40",
        "   Compiling syn v2.0.100",
        "   Compiling tsuki-flash v4.0.0",
        "    Finished release [optimized] target(s) in 3.24s",
    ]:
        blk.line(l); time.sleep(0.28)
    blk.finish(ok=True)
    pause(0.5)
    blk2 = LiveBlock("avrdude -p atmega328p -c arduino -P /dev/ttyUSB0")
    blk2.start()
    blk2.line('avrdude: ser_open(): can\'t open "/dev/ttyUSB0"')
    blk2.line("No such file or directory")
    time.sleep(0.9)
    blk2.finish(ok=False, summary="exit 1")
    pause(1.0)

    # 7 — Config + Box
    pres_title("config table  &  box")
    pause(0.3)
    config_table("tsuki.json", [
        ConfigEntry("board",      "arduino-nano"),
        ConfigEntry("port",       "/dev/ttyUSB0"),
        ConfigEntry("baud_rate",  115200,       "velocidad serie"),
        ConfigEntry("flash_mode", "tsuki-flash"),
        ConfigEntry("verbose",    False),
    ])
    pause(0.7)
    print()
    box('board   = "nano"\nbaud    = 115200\nbackend = tsuki-flash', title="tsuki config", out=sys.stdout)
    pause(1.5)

    # fin
    pres_title("fin")
    success("tsuki-ux  ·  github.com/tsuki-team/tsuki-ux")
    pause(2.5)


# ── Recording helpers ──────────────────────────────────────────────────────────

def _write_vhs_tape(tape_path: str, gif_path: str) -> None:
    """Write a .tape file for vhs (https://github.com/charmbracelet/vhs)."""
    self_path = os.path.abspath(__file__)
    content = textwrap.dedent(f"""\
        Output {gif_path}
        Set FontSize 14
        Set Width 100
        Set Height 40
        Set Theme "Catppuccin Mocha"
        Type "python {self_path} --presentation"
        Enter
        Sleep 90s
    """)
    with open(tape_path, "w") as f:
        f.write(content)


def start_recording(out_file: str = "demo.cast") -> "subprocess.Popen | None":
    """
    Try to start a terminal recording session.

    Priority:
      1. asciinema  → records to ``out_file`` (.cast)
      2. vhs        → writes a .tape file and prints the command to run
      3. script     → Unix fallback, records raw typescript to ``out_file``

    Returns the Popen handle when asciinema or script starts,
    or None when only a vhs tape was written (vhs runs externally).
    """
    # 1 — asciinema
    if shutil.which("asciinema"):
        proc = subprocess.Popen(
            ["asciinema", "rec", "--overwrite", out_file],
            stdin=None,   # inherits the real TTY
        )
        print(f"\n  \033[90mRecording with asciinema → {out_file}\033[0m\n")
        return proc

    # 2 — vhs (writes tape, user runs it manually or CI does)
    if shutil.which("vhs"):
        tape = os.path.splitext(out_file)[0] + ".tape"
        gif  = os.path.splitext(out_file)[0] + ".gif"
        _write_vhs_tape(tape, gif)
        print(f"\n  \033[90mvhs tape written → {tape}\033[0m")
        print(f"  \033[90mRun: vhs {tape}\033[0m\n")
        return None

    # 3 — script (Unix)
    if shutil.which("script"):
        proc = subprocess.Popen(
            ["script", "-q", "-c", f"python {os.path.abspath(__file__)} --presentation", out_file],
        )
        print(f"\n  \033[90mRecording with script → {out_file}\033[0m\n")
        return proc

    # Nothing found
    sys.stderr.write(
        "  \033[1;93m⚠\033[0m  No recorder found.\n"
        "     Install asciinema: https://asciinema.org/docs/installation\n"
        "     Or vhs:            https://github.com/charmbracelet/vhs\n\n"
    )
    return None


def stop_recording(proc: "subprocess.Popen | None", out_file: str) -> None:
    if proc is None:
        return
    try:
        proc.send_signal(__import__("signal").SIGINT)
    except Exception:
        pass
    proc.wait()
    print(f"\n  \033[90mRecording saved → {out_file}\033[0m\n")


if __name__ == "__main__":
    is_presentation = "--presentation" in sys.argv
    is_record       = "--record"       in sys.argv

    # --record implies --presentation
    if is_record:
        is_presentation = True

    # resolve output file from --out <path>
    out_file = "demo.cast"
    if "--out" in sys.argv:
        idx = sys.argv.index("--out")
        if idx + 1 < len(sys.argv):
            out_file = sys.argv[idx + 1]

    rec_proc = None
    if is_record:
        rec_proc = start_recording(out_file)
        # Give the recorder a moment to attach
        time.sleep(0.4)

    try:
        if is_presentation:
            run_presentation()
        else:
            run_full()
    finally:
        if is_record and rec_proc is not None:
            stop_recording(rec_proc, out_file)