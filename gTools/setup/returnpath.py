"""
File needed to return directory path as userSetup.py is loaded in main and cannot return __file__
"""

import os


def getpath():
    # Nesting os.path.dirname returns directory above file directory
    # In this case, the gTools>Maya directory which will act as our tools hub
    return os.path.dirname(os.path.dirname(__file__))
