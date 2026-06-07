# DCC-Agnostic Architecture — Sketch (analysis & proofing only)

> **This folder has ZERO impact on the live pipeline.** It is not on Maya's `sys.path`
> (the `.mod` only exposes `gTools/setup`; `userSetup` only adds `gTools/`), the boot
> manager only scans `gTools/setup/startup/*_startup.py`, and `core/__init__.py` only
> appends `gTools/core/packages`. Nothing here is ever imported by the running pipeline.
> It exists purely to read, reason about, and prove the Phase 2/3 design compiles.

## What this proves

The asset manager can be built as a **DCC-agnostic core + shared UI + thin host adapters**,
so the same code runs **inside Maya** and **standalone** (for producers / non-artists / other
systems). Treat `sketch/dcc_agnostic/` as if it were a future `gTools/`.

```
sketch/dcc_agnostic/
  core/                       # PURE PYTHON — no Qt, no maya.*  (runnable headless)
    dcc_adapter.py            # DccAdapter ABC — the single host seam
    assetmanager/
      models.py               # Asset dataclass (no deps)
      repository.py           # AssetRepository ABC + SQLiteAssetRepository (stdlib sqlite3)
  ui/                         # SHARED PySide widgets — DCC-agnostic, parented dynamically
    assetmanager/
      asset_manager_widget.py # one widget, used by BOTH hosts; talks to the adapter only
  dcc/
    maya/                     # imports maya.*  — Maya adapter + launch wiring
      adapter.py  launch.py
    standalone/               # QApplication bootstrap + no-DCC adapter
      adapter.py  app.py
  selftest.py                 # runs the core headless to PROVE it needs no DCC/Qt
```

## The one rule: dependencies point inward

```
dcc/maya ─┐
dcc/standalone ─┤──> ui ──> core        core imports NEITHER Qt NOR any DCC
          └────────────────> core
```

`core` is the only thing the standalone app and Maya share. The **`DccAdapter`** interface
(`get_main_window`, `open_file`, `import_asset`, `export_selection`, `current_scene`,
`host_name`) is the seam each host implements. The UI calls the adapter, never Maya directly —
that's what lets the GUIs mirror from one source.

## How it maps onto the real gTools (when Phase 2/3 lands)

| Sketch file | Real gTools target |
|---|---|
| `core/assetmanager/*` | new `gTools/core/assetmanager/` |
| `core/dcc_adapter.py` | new `gTools/core/dcc_adapter.py` |
| `ui/assetmanager/asset_manager_widget.py` | new `gTools/ui/...`, imports `core.utils.qt` shim |
| `dcc/maya/adapter.py` | new `gTools/dcc/maya/...`, reuses `core.utils.ui_utils.get_maya_main_window` |
| `dcc/standalone/app.py` | bundled later like the Phase-1 installer (PyInstaller) |
| DB path | already exists: `core.config.get_db_path()` |

## Run the proof

```
py -3 sketch/dcc_agnostic/selftest.py      # exercises the SQLite repo with no Qt/maya present
py -3 -m compileall sketch/dcc_agnostic     # confirms every stub (incl. ui/dcc) is valid py3
```

## Key design note carried from the roadmap

All DB access goes through `AssetRepository` (an ABC). Local SQLite is v1; a future
shared/served/synced backend becomes a *new implementation* of the same interface — a swap,
not a rewrite. That is what keeps the producer/ecosystem ambitions cheap.
