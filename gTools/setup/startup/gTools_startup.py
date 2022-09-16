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
        # Fill menus
        artDiv = cmds.menuItem(parent=gToolsMenu, label="Art", divider=True)
        animMenu = cmds.menuItem(parent=gToolsMenu, label="Animation", subMenu=True)
        techDiv = cmds.menuItem(parent=gToolsMenu, label="Tech", divider=True)
        rigMenu = cmds.menuItem(parent=gToolsMenu, label="Rigging", subMenu=True)
        skinningMenu = cmds.menuItem(parent=gToolsMenu, label="Skinning", subMenu=True)
        
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