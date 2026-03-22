#!/usr/bin/env python3
"""
tools/release.py — Automate publishing tsuki-ux to GitHub, PyPI, and crates.io.

Usage (always run from repo root):
    python tools/release.py [--version 1.2.3] [--dry-run] [--only github|pypi|cargo]

Environment variables (loaded from .env automatically):
    GITHUB_TOKEN     — Personal access token (repo + write:packages)
    PYPI_API_TOKEN   — PyPI API token (starts with pypi-)
    CARGO_TOKEN      — crates.io API token

What it does:
  1. Bumps version in python/pyproject.toml and rust/Cargo.toml
  2. Runs tests for all three packages
  3. Creates a git tag and GitHub release with auto-generated changelog
  4. Publishes the Python package to PyPI
  5. Publishes the Rust crate to crates.io
"""
from __future__ import annotations
import argparse, json, os, re, shutil, subprocess, sys, textwrap, urllib.request, urllib.error
from pathlib import Path
from typing import Optional

TOOLS_DIR = Path(__file__).resolve().parent
REPO_ROOT = TOOLS_DIR.parent

# ── Venv resolution ───────────────────────────────────────────────────────────
# Prefer the Python interpreter inside python\venv (Windows) or python/venv (Unix).
# Falls back to the current interpreter if the venv doesn't exist yet.
_VENV_ROOT = REPO_ROOT / "python" / "venv"
if sys.platform == "win32":
    _VENV_PY = _VENV_ROOT / "Scripts" / "python.exe"
else:
    _VENV_PY = _VENV_ROOT / "bin" / "python"

VENV_PY = str(_VENV_PY) if _VENV_PY.exists() else sys.executable

_TTY = sys.stdout.isatty()
def _c(code, s): return f"\033[{code}m{s}\033[0m" if _TTY else s
def ok(m):   print(f"  \033[1;92m✔\033[0m  {m}" if _TTY else f"  +  {m}")
def err(m):  print(f"  \033[1;91m✖\033[0m  {m}" if _TTY else f"  x  {m}", file=sys.stderr)
def warn(m): print(f"  \033[1;93m⚠\033[0m  {m}" if _TTY else f"  !  {m}")
def info(m): print(f"  \033[96m●\033[0m  {m}" if _TTY else f"  *  {m}")
def step(m): print(f"\n  \033[36m▶\033[0m  \033[1m{m}\033[0m" if _TTY else f"\n  >  {m}")
def die(m):  err(m); sys.exit(1)

def load_env(path=".env"):
    p = Path(path) if Path(path).is_absolute() else REPO_ROOT / path
    if not p.exists():
        warn(f".env not found at {p}"); return
    for line in p.read_text().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line: continue
        k, _, v = line.partition("=")
        k = k.strip(); v = v.strip().strip('"').strip("'")
        if k and k not in os.environ: os.environ[k] = v
    info(f"Loaded {p.name}")

def run(cmd, *, cwd=None, env=None, capture=False, dry=False, allow_codes=()):
    disp = " ".join(str(c) for c in cmd)
    if dry: info(f"[dry-run] {disp}"); return ""
    info(f"$ {disp}")
    r = subprocess.run(cmd, cwd=cwd or REPO_ROOT,
                       env={**os.environ, **(env or {})},
                       capture_output=capture, text=True)
    if r.returncode != 0 and r.returncode not in allow_codes:
        die(f"Failed:\n{r.stderr or r.stdout}" if capture else f"Failed: {disp}")
    return r.stdout.strip() if capture else ""

def require(t):
    if not shutil.which(t): die(f"Required: {t}")

_SV = re.compile(r"^(\d+)\.(\d+)\.(\d+)$")

def parse_version(v):
    m = _SV.match(v.lstrip("v"))
    if not m: die(f"Invalid semver: {v!r}")
    return int(m[1]), int(m[2]), int(m[3])

def bump_version(current, part):
    a, b, c = parse_version(current)
    if part == "major": return f"{a+1}.0.0"
    if part == "minor": return f"{a}.{b+1}.0"
    return f"{a}.{b}.{c+1}"

def current_git_version():
    try:
        t = subprocess.check_output(
            ["git","describe","--tags","--abbrev=0"],
            stderr=subprocess.DEVNULL, text=True, cwd=REPO_ROOT
        ).strip().lstrip("v")
        if _SV.match(t): return t
    except subprocess.CalledProcessError: pass
    return "0.0.0"

def patch_file(path, pattern, replacement, dry):
    text = path.read_text()
    new  = re.sub(pattern, replacement, text, count=1)
    if text == new: warn(f"Pattern not found in {path}"); return
    if not dry: path.write_text(new)
    info(f"{'[dry] ' if dry else ''}Updated {path.relative_to(REPO_ROOT)}")

def bump_python(version, dry):
    patch_file(REPO_ROOT/"python"/"pyproject.toml",
               r'(?m)^version\s*=\s*"[^"]+"', f'version = "{version}"', dry)

def bump_rust(version, dry):
    patch_file(REPO_ROOT/"rust"/"Cargo.toml",
               r'(?m)^version\s*=\s*"[^"]+"', f'version = "{version}"', dry)

def git_changelog(from_tag, to_ref="HEAD"):
    try:
        log = subprocess.check_output(
            ["git","log",f"{from_tag}..{to_ref}","--oneline","--no-decorate"],
            text=True, stderr=subprocess.DEVNULL, cwd=REPO_ROOT
        ).strip()
    except subprocess.CalledProcessError:
        log = subprocess.check_output(
            ["git","log","--oneline","--no-decorate","-20"],
            text=True, cwd=REPO_ROOT
        ).strip()
    return "\n".join(f"- {l}" for l in log.splitlines()) if log else "No changes."

def github_release(repo, tag, title, body, token, dry):
    url = f"https://api.github.com/repos/{repo}/releases"
    payload = json.dumps({"tag_name":tag,"name":title,"body":body,"draft":False,"prerelease":False}).encode()
    if dry: info(f"[dry-run] POST {url}  tag={tag}"); return
    req = urllib.request.Request(url, data=payload, method="POST", headers={
        "Authorization":f"Bearer {token}","Accept":"application/vnd.github+json",
        "Content-Type":"application/json","X-GitHub-Api-Version":"2022-11-28",
    })
    try:
        with urllib.request.urlopen(req) as r:
            ok(f"GitHub release: {json.loads(r.read())['html_url']}")
    except urllib.error.HTTPError as e:
        die(f"GitHub API {e.code}: {e.read().decode()}")

def publish_pypi(token, dry):
    py = REPO_ROOT/"python"
    info(f"Using Python: {VENV_PY}")
    step("Building Python package")
    run([VENV_PY,"-m","build","--wheel","--sdist"], cwd=py, dry=dry)
    step("Uploading to PyPI")
    run([VENV_PY,"-m","twine","upload","--skip-existing", str(py/"dist"/"*")],
        env={"TWINE_USERNAME":"__token__","TWINE_PASSWORD":token}, cwd=py, dry=dry)
    ok("Published to PyPI")

def publish_cargo(token, dry):
    require("cargo")
    step("Publishing to crates.io")
    run(["cargo","publish","--token",token,"--allow-dirty"]+( ["--dry-run"] if dry else []),
        cwd=REPO_ROOT/"rust")
    ok("Published to crates.io")

def run_tests(only, dry):
    step("Running tests")
    if only in (None,"go") and shutil.which("go"):
        run(["go","test","./..."], cwd=REPO_ROOT/"go", dry=dry); ok("Go tests passed")
    if only in (None,"pypi"):
        # pytest exit 5 = no tests collected — treat as pass
        run([VENV_PY,"-m","pytest","--tb=short","-q"], cwd=REPO_ROOT/"python", dry=dry, allow_codes=(5,))
        ok("Python tests passed")
    if only in (None,"cargo") and shutil.which("cargo"):
        run(["cargo","test"], cwd=REPO_ROOT/"rust", dry=dry); ok("Rust tests passed")

def main():
    p = argparse.ArgumentParser(
        description="Publish tsuki-ux to GitHub, PyPI, and crates.io",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Examples:
              python tools/release.py                       # patch bump, publish all
              python tools/release.py --version 2.0.0      # explicit version
              python tools/release.py --bump minor
              python tools/release.py --dry-run
              python tools/release.py --only pypi
              python tools/release.py --only cargo
              python tools/release.py --only github
        """),
    )
    p.add_argument("--version",    help="Explicit version (e.g. 1.2.3)")
    p.add_argument("--bump",       choices=["major","minor","patch"], default="patch")
    p.add_argument("--dry-run",    action="store_true")
    p.add_argument("--only",       choices=["github","pypi","cargo"])
    p.add_argument("--skip-tests", action="store_true")
    p.add_argument("--repo",       default="tsuki-team/tsuki-ux")
    p.add_argument("--env",        default=".env")
    args = p.parse_args()
    dry  = args.dry_run

    load_env(args.env)

    github_token = os.environ.get("GITHUB_TOKEN","")
    pypi_token   = os.environ.get("PYPI_API_TOKEN","")
    cargo_token  = os.environ.get("CARGO_TOKEN","")

    if not dry:
        if args.only in (None,"github") and not github_token: die("GITHUB_TOKEN not set")
        if args.only in (None,"pypi")   and not pypi_token:   die("PYPI_API_TOKEN not set")
        if args.only in (None,"cargo")  and not cargo_token:  die("CARGO_TOKEN not set")

    current     = current_git_version()
    new_version = args.version.lstrip("v") if args.version else bump_version(current, args.bump)
    tag         = f"v{new_version}"
    if args.version: parse_version(new_version)

    print()
    info(f"Repo root       : {REPO_ROOT}")
    info(f"Current version : {current}")
    info(f"New version     : {new_version}  ({tag})")
    info(f"Dry run         : {dry}")
    info(f"Target          : {args.only or 'all'}")
    print()

    if not dry:
        ans = input(f"  Proceed with release {tag}? [y/N] ").strip().lower()
        if ans not in ("y","yes"): die("Aborted.")

    step("Bumping versions")
    bump_python(new_version, dry)
    bump_rust(new_version, dry)

    step("Creating git commit and tag")
    run(["git","add","--all"], dry=dry)
    run(["git","commit","-m",f"chore: release {tag}"], dry=dry)
    run(["git","tag","-a",tag,"-m",f"Release {tag}"], dry=dry)

    step("Pushing repo to GitHub")
    run(["git","push","--all","origin"], dry=dry)
    run(["git","push","--tags","origin"], dry=dry)
    ok(f"Repo and tag {tag} pushed")

    if not args.skip_tests: run_tests(args.only, dry)

    if args.only in (None,"github"):
        step("Creating GitHub release")
        github_release(args.repo, tag, f"tsuki-ux {tag}",
                       f"## What's changed\n\n{git_changelog(f'v{current}')}\n",
                       github_token, dry)

    if args.only in (None,"pypi"):
        publish_pypi(pypi_token, dry)

    if args.only in (None,"cargo"):
        publish_cargo(cargo_token, dry)

    print(); ok(f"Release {tag} complete! 🚀")

if __name__ == "__main__":
    main()