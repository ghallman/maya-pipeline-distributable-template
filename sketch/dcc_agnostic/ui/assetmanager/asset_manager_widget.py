"""
Shared asset-manager widget (sketch).

ONE widget used by BOTH hosts. It receives:
  - a `repository` (AssetRepository)  -> where data lives
  - a `dcc`        (DccAdapter)       -> how to talk to the host

It never imports `maya.*`. In real gTools the Qt import below becomes:
    from core.utils.qt import QtWidgets, QtCore
(the existing PySide6/PySide2 shim). Here we mirror that shim locally so the
sketch is self-contained; the import is lazy/guarded so this file byte-compiles
on machines without PySide installed.
"""

from core.assetmanager.repository import AssetRepository
from core.assetmanager.models import Asset
from core.dcc_adapter import DccAdapter


def _qt():
    """Lazy Qt import mirroring gTools' core.utils.qt shim (PySide6 -> PySide2)."""
    try:
        from PySide6 import QtWidgets, QtCore  # Maya 2025-2026 / standalone
        return QtWidgets, QtCore
    except ImportError:
        from PySide2 import QtWidgets, QtCore  # Maya 2022-2024
        return QtWidgets, QtCore


def build_widget(repository: AssetRepository, dcc: DccAdapter):
    """Construct and return the asset-manager widget.

    A factory (not a module-level class) so the heavy Qt base class is only
    resolved when actually building UI — keeping this module import-safe headless.
    """
    QtWidgets, QtCore = _qt()

    class AssetManagerWidget(QtWidgets.QWidget):
        def __init__(self, parent=None):
            super().__init__(parent)
            self._repo = repository
            self._dcc = dcc
            self.setWindowTitle("Asset Manager  -  {}".format(dcc.host_name))

            layout = QtWidgets.QVBoxLayout(self)
            self._list = QtWidgets.QListWidget()
            self._import_btn = QtWidgets.QPushButton("Import selected into host")
            layout.addWidget(self._list)
            layout.addWidget(self._import_btn)

            # The ONLY host interaction is via the adapter — identical code in
            # Maya and standalone; behaviour differs inside the adapter.
            self._import_btn.clicked.connect(self._on_import)
            self.refresh()

        def refresh(self):
            self._list.clear()
            for asset in self._repo.list():
                self._list.addItem(
                    "[{}] {} v{}  ({})".format(
                        asset.asset_type, asset.name, asset.version, asset.status
                    )
                )

        def _on_import(self):
            row = self._list.currentRow()
            assets = self._repo.list()
            if 0 <= row < len(assets):
                self._dcc.import_asset(assets[row])

    parent = dcc.get_main_window()
    return AssetManagerWidget(parent)
