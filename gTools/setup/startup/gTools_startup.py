'''
Startup file to load menus and other needed modules
'''

## Base Imports ##
import os
import sys
import logging

## Maya Imports ##
import maya.cmds as cmds
import maya.mel as mel

## Logging ##
packName = 'gTools'
logging.basicConfig()
#log = logging.getLogger(__name__)
log = logging.getLogger(packName)
log.setLevel(logging.INFO)

# log.info('PRE BOOT LOG TEST')
########################
## Module Import ##
########################
# todo: setup the module import to trigger exception properly if failed. Ideally should tie in to the start() function below (as a standard)
#       anything risky (like custom modules) in a startup file should go through the start() and error logging
#       could potentially have FAILED exception in each method themselves and start only tries to run each. If any returns error that error is the log printed?
#       sounds convoluted :/
import core

def importModule():
    pass
    
######################## 
## Menu Methods ##
########################
# TODO: set core menu name as a constant so it can be more easily changed
# MENU_SPEC is the data definition of the gTools menu's contents. Keeping
# it as plain data (not a sequence of cmds.menuItem calls) means it can be
# unit-tested without Maya. _buildMenuItems is the thin shell that walks
# the spec and makes the side-effecting cmds calls.
MENU_SPEC = (
    {'label': 'Art', 'divider': True},
    {'label': 'Animation', 'subMenu': True},
    {'label': 'Tech', 'divider': True},
    {'label': 'Rigging', 'subMenu': True},
    {'label': 'Skinning', 'subMenu': True},
)


def _buildMenuItems(parentMenu, spec):
    """Render a MENU_SPEC entry list under the given parent menu."""
    for item in spec:
        kwargs = {'parent': parentMenu, 'label': item['label']}
        if item.get('divider'):
            kwargs['divider'] = True
        if item.get('subMenu'):
            kwargs['subMenu'] = True
        cmds.menuItem(**kwargs)


def menuSetup(parent='MayaWindow'):#Make "parent" more dynamic later

    # if menu exists, delete
    if cmds.menu('gToolsMenu', exists=True):
        cmds.deleteUI('gToolsMenu')

    # Try to create menu
    try:
        gToolsMenu = cmds.menu('gToolsMenu', l="gTools", p=parent, tearOff=True, allowOptionBoxes=True)
    except:
        cmds.warning('gTools Menu failed to find parent (Likely "MayaWindow"')
        #if we error this method here, does it not kill the boot process overall?

    if gToolsMenu:
        _buildMenuItems(gToolsMenu, MENU_SPEC)
    else:
        cmds.warning('gTools parent menu does not exist')

######################## 
## Boot Method ##
########################
def start():
    #log.info('Boot Status : RUNNING')

    try:
        menuSetup()

        log.info('Boot Status : SUCCESS')
    except ImportError:
        log.info('Boot Status: FAILED - Module Import')
    except:
        log.info('Boot Status: FAILED')




######################## 
## menu callback functions ##
########################
def _some_menu_cb(*args):
    """
    import core.xxxx.xxxx as x
    reload(x)
    x.some_function()
    """
    pass