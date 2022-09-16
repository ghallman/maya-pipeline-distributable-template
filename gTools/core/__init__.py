"""
Core Module

This module is the core of gTools
"""

## Base Imports ##
import os
import sys

########################
## Path Method ##
########################
def getPath():
    """

    :rtype: str
    :return: path string
    """
    return os.path.dirname(__file__)


########################
## Module Stuff ##
########################
# module variables
path = getPath()
packagesPath = os.path.join(path, 'packages')
resourcePath = os.path.join(path, 'resources')
iconsPath = os.path.join(resourcePath, 'icons')

# any dependencies that need added to sys path should be in this list
dependencyPaths = [packagesPath]
pluginPaths = []

## Add all necessary paths to sys path for core module dependencies ie.perforce / QT etc
for i in dependencyPaths:
    sys.path.append(i)
