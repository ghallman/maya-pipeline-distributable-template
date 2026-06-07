# maya-pipeline-distributable-template

`gTools` is a source-control-friendly, path-agnostic Maya pipeline distributable.
It is the foundation of a personal/freelance pipeline ecosystem — see the roadmap
below for where it's headed.

To install, drag-and-drop `gTools/install.py` onto your Maya viewport. It writes a
`.mod` file into Maya's user `modules` folder pointing at this pipeline's location,
then asks you to restart Maya.

## How it works

The pipeline uses a deferred **boot manager** (`setup/userSetup.py`) that runs at
Maya startup: it loads the required **core** module first, then auto-discovers and
boots any additional `*_startup.py` module under `setup/startup/`. To add a tool
module, copy `template_startup.py`, rename it `yourtool_startup.py`, and put your
imports and boot logic in its `start()` function.

## Supported Maya versions

Python 3 only: **Maya 2022–2026**. The Qt layer (`core/utils/qt.py`) auto-selects
**PySide2** (2022–2024) or **PySide6** (2025–2026). Version-specific plugins live
under `core/plugins/<year>/`.

## Branding (white-label)

All user-visible naming (menu label, window titles, `.mod` filename, log tags) is
driven from **one file**: `gTools/brand.py`. To rebrand, edit the `DEFAULTS` there,
or drop a `brand.json` next to it to override fields without touching code. The
Python package namespace stays `gTools`.

## Modes & data

`core/config.py` resolves where data lives based on mode (`GTOOLS_MODE` env var or a
`pipeline.cfg`):

- **dev** — pipeline runs from your git clone; data under `_data/` (git-ignored).
- **client** — installed for an end user; data under the user profile.

`config.get_db_path()` returns the SQLite path reserved for the future asset manager.

## Roadmap

- **Phase 0 — Modernize foundation** ✅ py3 port, brand config, mode-aware data layer,
  2022–2026 support.
- **Phase 1 — Standalone GUI installer** (planned): PySide6 + PyInstaller exe with
  registry-based Maya auto-detection and dev/client (git-clone vs release-zip) modes.
- **Phase 2 — Asset manager** (planned): a boot module backed by SQLite via the
  Phase-0 data layer.
