# tools/

Developer tools for the tsuki-ux project.

## release.py — publish to GitHub, PyPI, and crates.io

```bash
# From repo root:
python tools/release.py                        # patch bump, publish all
python tools/release.py --version 2.0.0       # explicit version
python tools/release.py --bump minor
python tools/release.py --dry-run             # preview, nothing runs
python tools/release.py --only pypi           # single target
python tools/release.py --only cargo
python tools/release.py --only github
```

Reads secrets from `.env` in the repo root. Copy `.env.example` to `.env` and fill in your tokens.

## package.py — create a zip archive of the repo

Respects `.gitignore` and always excludes `.git/`. Used internally by CI.

```python
from tools.package import zip_directory

zip_directory(dir_path=".", zip_path="tsuki-ux.zip")
```

## .env.example

Copy to `.env` and fill in your API tokens:

```
GITHUB_TOKEN=ghp_...
PYPI_API_TOKEN=pypi-...
CARGO_TOKEN=...
```

`.env` is in `.gitignore`. Never commit it.