"""
StandaloneDccAdapter (sketch) — DccAdapter with no DCC behind it.

This is the adapter that unlocks producer / non-artist use: there is no scene,
so host actions degrade to OS-level equivalents instead of Maya calls. Same
interface, so the SHARED widget runs unchanged.
"""

import os

from core.dcc_adapter import DccAdapter
from core.assetmanager.models import Asset


class StandaloneDccAdapter(DccAdapter):
    host_name = "Standalone"

    def __init__(self, main_window=None):
        self._main_window = main_window  # top-level QWidget, or None

    def get_main_window(self):
        return self._main_window

    def open_file(self, path: str) -> None:
        # No DCC scene — open with the OS default application.
        if hasattr(os, "startfile"):           # Windows
            os.startfile(path)                  # noqa: S606  (sketch)

    def import_asset(self, asset: Asset) -> None:
        # Nothing to import *into* without a scene; reveal the source instead.
        if asset.path:
            self.open_file(asset.path)

    def export_selection(self, path: str) -> None:
        # No selection concept standalone — intentionally a no-op.
        return None

    def current_scene(self):
        return None
