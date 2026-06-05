# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Environment

- **Shell**: zsh (Homebrew at `/opt/homebrew`)
- **Python**: 3.9.6 at `/usr/bin/python3` (system default; no virtualenv by default)
- **AGI Cockpit** is on `PATH` via `~/.agi-tools/data/cockpit/master/bin`

## Projects

Code lives under `~/Projects/`. Currently:

### python-hello (`~/Projects/python-hello/`)

A Python learning sandbox. Single entry point: `main.py`.

```bash
cd ~/Projects/python-hello
python3 main.py
```

To set up a virtualenv if needed:
```bash
python3 -m venv .venv
source .venv/bin/activate
```

No test suite exists yet. If adding one, use `pytest` and run with:
```bash
python3 -m pytest
```
