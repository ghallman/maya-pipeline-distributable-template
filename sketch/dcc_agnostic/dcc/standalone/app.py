"""
Standalone asset-manager entry point (sketch).

This is the key Phase-2 deliverable: the asset DB, opened with NO DCC, for
producers / non-artists / other systems. Later bundled to a single exe the same
way as the Phase-1 installer (PyInstaller + PySide6).

Run (with PySide6 installed):  py -3 -m dcc.standalone.app
"""


def main():
    try:
        from core.config import get_db_path
    except Exception:
        import os, tempfile
        def get_db_path():
            return os.path.join(tempfile.gettempdir(), "assets.db")

    try:
        from PySide6 import QtWidgets
    except ImportError:
        from PySide2 import QtWidgets

    from core.assetmanager.repository import SQLiteAssetRepository
    from dcc.standalone.adapter import StandaloneDccAdapter
    from ui.assetmanager.asset_manager_widget import build_widget

    import sys
    app = QtWidgets.QApplication(sys.argv)

    repo = SQLiteAssetRepository(get_db_path())
    dcc = StandaloneDccAdapter()            # no scene, OS-level fallbacks
    widget = build_widget(repo, dcc)        # SAME widget the Maya host uses
    widget.resize(420, 320)
    widget.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
