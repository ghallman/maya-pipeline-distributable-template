"""
Shared pytest setup for the gTools test suite.

The gTools layout mimics the runtime that Maya provides via the .mod file:
  - `gTools/` is on sys.path so `import core` / `import core.utils.file_utils` work.
  - `gTools/setup/` is on sys.path so `import returnpath` / `import startup` work.

We also stub the `maya` modules (and the PySide2 stack that vanilla Maya
bundles) so files that import them at module load time don't crash the test
runner. Tests that need richer behaviour should monkeypatch on top of these
stubs.
"""

import os
import sys
import types


REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GTOOLS_ROOT = os.path.join(REPO_ROOT, "gTools")
SETUP_ROOT = os.path.join(GTOOLS_ROOT, "setup")

for p in (GTOOLS_ROOT, SETUP_ROOT):
    if p not in sys.path:
        sys.path.insert(0, p)


def _install_maya_stubs():
    if "maya" in sys.modules:
        return

    maya = types.ModuleType("maya")
    cmds = types.ModuleType("maya.cmds")
    mel = types.ModuleType("maya.mel")
    omui = types.ModuleType("maya.OpenMayaUI")

    def _raise_error(msg, *args, **kwargs):
        raise RuntimeError("maya.cmds.error: {0}".format(msg))

    cmds.error = _raise_error
    cmds.warning = lambda *a, **k: None
    cmds.confirmDialog = lambda *a, **k: None
    cmds.menu = lambda *a, **k: None
    cmds.menuItem = lambda *a, **k: None
    cmds.deleteUI = lambda *a, **k: None
    cmds.evalDeferred = lambda *a, **k: None
    cmds.internalVar = lambda **k: "/tmp/maya"

    # OpenMayaUI.MQtUtil.mainWindow() returns a pointer-as-int in real Maya;
    # ui_utils wraps it at import time, so the stub must return something
    # int() accepts.
    class _MQtUtil(object):
        @staticmethod
        def mainWindow():
            return 0

    omui.MQtUtil = _MQtUtil

    maya.cmds = cmds
    maya.mel = mel
    maya.OpenMayaUI = omui

    sys.modules["maya"] = maya
    sys.modules["maya.cmds"] = cmds
    sys.modules["maya.mel"] = mel
    sys.modules["maya.OpenMayaUI"] = omui


def _install_qt_stubs():
    """
    Stub the PySide2 stack that vanilla Maya bundles.

    gTools assumes PySide is always present (Maya is the core dependency),
    so ui_utils.py imports PySide2/pyside2uic/shiboken2 unconditionally and
    builds MAYAWINDOW at import time. In a headless CI runner none of that
    exists, so we register lightweight stand-ins here rather than weakening
    the production module with no-PySide fallbacks.

    The stubs cover only what gTools touches:
      - QWidget / QMainWindow  (loadUiType resolves the base class by name)
      - compileUi              (emits a Ui_<class> stub from the .ui XML)
      - wrapInstance           (returns a sentinel main-window object)
    """
    if "PySide2" in sys.modules:
        return

    import re

    class QWidget(object):
        def __init__(self, *args, **kwargs):
            pass

    class QMainWindow(QWidget):
        pass

    class QIcon(object):
        def __init__(self, *args, **kwargs):
            pass

    def compileUi(ui_file_obj, out, indent=0):
        # Real pyside2uic.compileUi reads the .ui and writes a Ui_<class>
        # form class. We emit a minimal equivalent so loadUiType has a
        # class to pull out of the exec frame.
        content = ui_file_obj.read()
        match = re.search(r"<class>(.+?)</class>", content)
        name = match.group(1) if match else "Form"
        out.write(
            "class Ui_{0}(object):\n"
            "    def setupUi(self, widget):\n"
            "        pass\n".format(name)
        )

    def wrapInstance(ptr, base):
        return ("WRAPPED", ptr, base)

    pyside2 = types.ModuleType("PySide2")
    qtcore = types.ModuleType("PySide2.QtCore")
    qtgui = types.ModuleType("PySide2.QtGui")
    qtwidgets = types.ModuleType("PySide2.QtWidgets")
    pyside2uic = types.ModuleType("pyside2uic")
    shiboken2 = types.ModuleType("shiboken2")

    qtgui.QIcon = QIcon
    qtwidgets.QWidget = QWidget
    qtwidgets.QMainWindow = QMainWindow
    pyside2uic.compileUi = compileUi
    shiboken2.wrapInstance = wrapInstance

    pyside2.QtCore = qtcore
    pyside2.QtGui = qtgui
    pyside2.QtWidgets = qtwidgets

    sys.modules["PySide2"] = pyside2
    sys.modules["PySide2.QtCore"] = qtcore
    sys.modules["PySide2.QtGui"] = qtgui
    sys.modules["PySide2.QtWidgets"] = qtwidgets
    sys.modules["pyside2uic"] = pyside2uic
    sys.modules["shiboken2"] = shiboken2


_install_maya_stubs()
_install_qt_stubs()
