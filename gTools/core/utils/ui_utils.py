"""
Utilities for common UI functions (Python 3, PySide2/PySide6 via the qt shim).
"""

# base imports
import logging
import xml.etree.ElementTree as xml
from io import StringIO

# qt binding (PySide6 on Maya 2025-2026, PySide2 on 2022-2024) - star brings in
# QWidget, QMainWindow, QIcon, etc. for the eval() in the loadUiType fallback.
from core.utils.qt import *
from core.utils.qt import QtWidgets, wrapInstance, QT_BINDING

# maya imports
from maya import OpenMayaUI as omui

# logging
log = logging.getLogger(__name__)


###################################
# MAYA MAIN WINDOW
###################################
def get_maya_main_window():
    """Return Maya's main window wrapped as a QWidget, or None if unavailable."""
    ptr = omui.MQtUtil.mainWindow()
    if ptr is None:
        return None
    # py3: pointer is an int (py2 used long()).
    return wrapInstance(int(ptr), QtWidgets.QWidget)


try:
    MAYAWINDOW = get_maya_main_window()
except Exception:
    # Importing outside a running Maya session (e.g. byte-compile) must not fail.
    MAYAWINDOW = None


###################################
# PYSIDE / QT METHODS
###################################
def loadUiType(uiFile):
    """
    Return (form_class, base_class) for a Qt Designer .ui file.

    PySide6 and modern PySide2 both ship a native loadUiType in QtUiTools, so we
    prefer that. We keep the legacy in-memory compileUi path as a fallback for
    old PySide2 builds that lack QtUiTools.loadUiType.

    :param uiFile: OS path to a Qt Designer .ui file
    :return: (form_class, base_class)
    """
    # --- preferred: native loadUiType -------------------------------------
    try:
        if QT_BINDING == "PySide6":
            from PySide6.QtUiTools import loadUiType as _native
        else:
            from PySide2.QtUiTools import loadUiType as _native
        return _native(uiFile)
    except Exception:
        log.debug("Native loadUiType unavailable; using in-house compileUi fallback.")

    # --- fallback: compile the .ui to py in-memory ------------------------
    try:
        from pyside2uic import compileUi
    except ImportError:
        from pysideuic import compileUi

    parsed = xml.parse(uiFile)
    widget_class = parsed.find('widget').get('class')
    form_class = parsed.find('class').text

    with open(uiFile, 'r') as f:
        o = StringIO()
        frame = {}

        compileUi(f, o, indent=0)
        pyc = compile(o.getvalue(), '<string>', 'exec')
        exec(pyc, frame)

        # Fetch base/form classes by their type from the designer xml.
        form_class = frame['Ui_%s' % form_class]
        base_class = eval('%s' % widget_class)

    return form_class, base_class


###################################
# loadUiType Usage Example
###################################
# uiFormClass = loadUiType(<file.ui>)[0]
#
# from core.utils.qt import QtWidgets
# from core.utils.ui_utils import loadUiType, MAYAWINDOW
#
# class Window(QtWidgets.QMainWindow, uiFormClass):
#     def __init__(self, parent=MAYAWINDOW):
#         super(Window, self).__init__(parent)
#         self.setupUi(self)
# Window().show()
