"""
Utilities for common UI functions
"""

# base imports
import logging
import xml.etree.ElementTree as xml
from cStringIO import StringIO

# pyside imports
try:
    from PySide2.QtCore import *
    from PySide2.QtGui import *
    from PySide2.QtWidgets import *
    from pyside2uic import compileUi
    from shiboken2 import wrapInstance
except:
    from PySide.QtCore import *
    from PySide.QtGui import *
    from PySide.QtWidgets import *
    from pysideuic import compileUi
    from shiboken import wrapInstance

# maya imports
from maya import OpenMayaUI as omui

# logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# constants
MAYAWINDOW = wrapInstance(long(omui.MQtUtil.mainWindow()), QWidget)

###################################
# PYSIDE / QT METHODS
###################################

# Please read comments below as to why we use an internal loadUiType() function.
def loadUiType(uiFile):
    """
    Pyside "loadUiType" command like PyQt4 has one, so we have to convert the 
    ui file to py code in-memory first and then execute it in a special frame
    to retrieve the form_class.
    
    :param uiFile: OS path to QT Deisgner .ui file
    :return: generated_class, base_class - (<class '__main__.Ui_ThemeWidgetForm'>, <class 'PySide2.QtWidgets.QWidget'>)
    """
    parsed = xml.parse(uiFile)
    widget_class = parsed.find('widget').get('class')
    form_class = parsed.find('class').text

    with open(uiFile, 'r') as f:
        o = StringIO()
        frame = {}

        compileUi(f, o, indent=0)
        pyc = compile(o.getvalue(), '<string>', 'exec')
        exec pyc in frame

        # Fetch the base_class and form class based on their type
        # in the xml from designer
        form_class = frame['Ui_%s' % form_class]
        base_class = eval('%s' % widget_class)

    return form_class, base_class

###################################
# loadUiType Usage Example
###################################
# uiFormClass = loadUiType(<file.ui>)[0]
#
# class Window(QMainWindow, uiFormClass):
#     def __init__(self, parent = None):
#         super(Window, self).__init__(parent)
#         self.setupUi(self)
# Window().show()

###################################
## -- PySide2 brought back loadUiType in May 2020. So if you use a PySide2 package after that date then the above function is obsolete
## -- We use our own loadUiType function here as Maya's included Pyside / PySide2 packages may not have it
## -- https://doc.qt.io/qtforpython/PySide2/QtUiTools/ls.loadUiType.html
###################################
# Syntax is the same (you will use loadUiType(<file>)[0] )
# from PySide2.QtUiTools import loadUiType

###################################
# QUILoader Alternative
###################################
## -- QUILoader is an alternative to the above but requires an altered way of calling and editing the ui
## -- I'd prefer the PyQT style of returning the form class and using it as the mix-in with the app class itself
###################################
# from PySide2 import QtGui  
# from PySide2 import QtCore
# from PySide2 import QtUiTools
# 
# class MyWidget(QtGui.QMainWindow):
#     def __init__(self, *args):  
#        apply(QtGui.QMainWindow.__init__, (self,) + args)
# 
#        loader = QtUiTools.QUiLoader()
#        file = QtCore.QFile("pyside_ui_qtdesigner_form_test.ui")
#        file.open(QtCore.QFile.ReadOnly)
#        self.ui = loader.load(file, self)
#        file.close()
# 
#        self.setCentralWidget(self.ui)
# 
# win  = MyWidget()  
# win.show()
