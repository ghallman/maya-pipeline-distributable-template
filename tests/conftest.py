"""
Shared pytest setup for the gTools test suite.

The gTools layout mimics the runtime that Maya provides via the .mod file:
  - `gTools/` is on sys.path so `import core` / `import core.utils.file_utils` work.
  - `gTools/setup/` is on sys.path so `import returnpath` / `import startup` work.

We also stub the `maya` modules so files that `import maya.cmds` at module
load time don't crash the test runner. Tests that need richer Maya behaviour
should monkeypatch on top of these stubs.
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

    maya.cmds = cmds
    maya.mel = mel
    maya.OpenMayaUI = omui

    sys.modules["maya"] = maya
    sys.modules["maya.cmds"] = cmds
    sys.modules["maya.mel"] = mel
    sys.modules["maya.OpenMayaUI"] = omui


_install_maya_stubs()
