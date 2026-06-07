"""
Core Module

This module is the core of gTools
"""

## Base Imports ##
import os
import sys
import logging

log = logging.getLogger(__name__)


########################
## Path Method ##
########################
def getPath():
    """

    :rtype: str
    :return: path string
    """
    return os.path.dirname(__file__)


def getMayaVersion():
    """
    Return the running Maya version as a string (e.g. '2026'), or None outside Maya.
    """
    try:
        from maya import cmds
        return str(cmds.about(version=True)).split()[0]
    except Exception:
        return None


def getVersionPluginPath():
    """
    Resolve the version-specific plugin folder for the running Maya (plugins/<year>).
    Supports py3 Maya 2022-2026. Returns the path if it exists, else None.
    """
    version = getMayaVersion()
    if not version:
        return None
    candidate = os.path.join(pluginsPath, version)
    return candidate if os.path.isdir(candidate) else None


########################
## Module Stuff ##
########################
# module variables
path = getPath()
packagesPath = os.path.join(path, 'packages')
pluginsPath = os.path.join(path, 'plugins')
resourcePath = os.path.join(path, 'resources')
iconsPath = os.path.join(resourcePath, 'icons')

# any dependencies that need added to sys path should be in this list
dependencyPaths = [packagesPath]

# version-specific plugins for the running Maya (None if outside Maya / no folder)
pluginPaths = []
_versionPlugins = getVersionPluginPath()
if _versionPlugins:
    pluginPaths.append(_versionPlugins)

## Add all necessary paths to sys path for core module dependencies ie. perforce / QT etc
for i in dependencyPaths:
    sys.path.append(i)

## Register version-specific plugin paths so cmds.loadPlugin can find them
for p in pluginPaths:
    existing = os.environ.get('MAYA_PLUG_IN_PATH', '')
    if p not in existing.split(os.pathsep):
        os.environ['MAYA_PLUG_IN_PATH'] = (p + os.pathsep + existing) if existing else p
