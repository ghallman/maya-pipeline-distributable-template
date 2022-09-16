"""
This file is a template for creating PySide QT interfaces within maya using gTools

========================== How to run ==========================
================================================================
import core.examples.mayaQtTemplate as temp
# reload(temp) 
temp = temp.MyWindow() # instance the UI object
temp.show()
================================================================
# todo: add check for if window exists
"""
# base imports
import os

# pyside imports
from PySide2.QtCore import *
from PySide2.QtGui import *
from PySide2.QtWidgets import *

# maya imports
from maya import cmds

# internal imports
from core.utils.ui_utils import loadUiType, MAYAWINDOW
# from core import iconsPath

UI_FILENAME = 'mayaQtTemplate.ui'
UI_FILE = os.path.join(os.path.dirname(__file__), UI_FILENAME)
UI_FORM_CLASS = loadUiType(UI_FILE)[0]


class MyWindow(QMainWindow, UI_FORM_CLASS):
    """
    A simple QT UI template class
    """
    def __init__(self, parent=MAYAWINDOW):
        super(MyWindow, self).__init__(parent)
        self.setupUi(self)

        # appIcon = os.path.join(iconsPath, 'logo_256.ico')
        # self.setWindowIcon(QIcon(appIcon))
        
        # globals
        self.printString = 'Congratulations'

        # connect menus
        self.actionMenuButton.triggered.connect(self.__uicb__printTest)

        # connect buttons
        self.myButton.clicked.connect(self.__uicb__printTest)

    def __uicb__printTest(self):
        """
        QT UI button callback method
        """
        cmds.warning('UI did a thing. {0}.'.format(self.printString))
