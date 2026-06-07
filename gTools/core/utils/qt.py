"""
Qt binding compatibility shim.

Maya 2025-2026 ship PySide6; Maya 2022-2024 ship PySide2. This module hides that
difference behind one stable import surface so the rest of the pipeline never has
to branch on the binding.

Usage:
    from core.utils.qt import QtCore, QtGui, QtWidgets, wrapInstance, QT_BINDING
    # or, for the convenient star style:
    from core.utils.qt import *

The three Qt sub-modules are also star-imported here, so `from core.utils.qt import *`
brings QWidget, QMainWindow, QIcon, etc. into scope just like a direct PySide import.
"""

import logging

log = logging.getLogger(__name__)

QT_BINDING = None

try:
    from PySide6 import QtCore, QtGui, QtWidgets
    from PySide6.QtCore import *
    from PySide6.QtGui import *
    from PySide6.QtWidgets import *
    from shiboken6 import wrapInstance, getCppPointer
    QT_BINDING = "PySide6"
except ImportError:
    from PySide2 import QtCore, QtGui, QtWidgets
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *
    from shiboken2 import wrapInstance, getCppPointer
    QT_BINDING = "PySide2"

log.debug("Qt binding selected: %s", QT_BINDING)
