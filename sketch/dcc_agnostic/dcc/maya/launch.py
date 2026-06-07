"""
Maya launch wiring (sketch) — what the gTools menu item would call.

Shows the whole assembly in the Maya host: real DB path from core.config, the
Maya adapter, and the SHARED widget. Note there is no UI code here — the window
is the same `build_widget` used by standalone.
"""


def launch():
    # Real gTools seam — the asset DB location resolved by mode (dev/client).
    try:
        from core.config import get_db_path
    except Exception:
        import os, tempfile
        def get_db_path():
            return os.path.join(tempfile.gettempdir(), "assets.db")

    from core.assetmanager.repository import SQLiteAssetRepository
    from dcc.maya.adapter import MayaDccAdapter
    from ui.assetmanager.asset_manager_widget import build_widget

    repo = SQLiteAssetRepository(get_db_path())
    dcc = MayaDccAdapter()
    widget = build_widget(repo, dcc)   # parented to the Maya main window via the adapter
    widget.show()
    return widget
