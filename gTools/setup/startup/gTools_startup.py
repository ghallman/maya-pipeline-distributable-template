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

## Brand (single source of truth for user-visible names) ##
import brand
MENU_OBJ = '{0}Menu'.format(brand.get('name', 'gTools'))   # internal Maya UI name
MENU_LABEL = brand.get('menu_label', 'gTools')             # human-facing label

## Logging ##
packName = brand.get('logger_tag', 'gTools')
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
# Menu name/label come from the brand config (MENU_OBJ / MENU_LABEL above).
def menuSetup(parent='MayaWindow'):#Make "parent" more dynamic later

    # if menu exists, delete
    if cmds.menu(MENU_OBJ, exists=True):
        cmds.deleteUI(MENU_OBJ)

    # Try to create menu
    gToolsMenu = None
    try:
        gToolsMenu = cmds.menu(MENU_OBJ, l=MENU_LABEL, p=parent, tearOff=True, allowOptionBoxes=True)
    except:
        cmds.warning('{0} menu failed to find parent (Likely "MayaWindow")'.format(MENU_LABEL))
        #if we error this method here, does it not kill the boot process overall?

    if gToolsMenu:
        # Fill menus
        artDiv = cmds.menuItem(parent=gToolsMenu, label="Art", divider=True)
        animMenu = cmds.menuItem(parent=gToolsMenu, label="Animation", subMenu=True)
        techDiv = cmds.menuItem(parent=gToolsMenu, label="Tech", divider=True)
        rigMenu = cmds.menuItem(parent=gToolsMenu, label="Rigging", subMenu=True)
        skinningMenu = cmds.menuItem(parent=gToolsMenu, label="Skinning", subMenu=True)

    else:
        cmds.warning('{0} parent menu does not exist'.format(MENU_LABEL))

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
    import importlib
    import core.xxxx.xxxx as x
    importlib.reload(x)
    x.some_function()
    """
    pass