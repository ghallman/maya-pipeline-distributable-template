"""
MayaDccAdapter (sketch) — implements DccAdapter against maya.*.

All `maya` imports are LAZY (inside methods) so this module can be imported for
inspection/registration on a machine without Maya. In real gTools, get_main_window()
delegates to the already-modernized `core.utils.ui_utils.get_maya_main_window()`.
"""

from core.dcc_adapter import DccAdapter
from core.assetmanager.models import Asset


class MayaDccAdapter(DccAdapter):
    host_name = "Maya"

    def get_main_window(self):
        # Real gTools: `from core.utils.ui_utils import get_maya_main_window`
        from maya import OpenMayaUI as omui
        try:
            from shiboken6 import wrapInstance
            from PySide6 import QtWidgets
        except ImportError:
            from shiboken2 import wrapInstance
            from PySide2 import QtWidgets
        ptr = omui.MQtUtil.mainWindow()
        return wrapInstance(int(ptr), QtWidgets.QWidget) if ptr else None

    def open_file(self, path: str) -> None:
        from maya import cmds
        cmds.file(path, open=True, force=True)

    def import_asset(self, asset: Asset) -> None:
        from maya import cmds
        # Reference the asset's published file into the current scene.
        cmds.file(asset.path, reference=True, namespace=asset.name)

    def export_selection(self, path: str) -> None:
        from maya import cmds
        cmds.file(path, exportSelected=True, force=True)

    def current_scene(self):
        from maya import cmds
        return cmds.file(query=True, sceneName=True) or None
