"""
When module is setup correctly this file will run at maya boot

# This file runs before scene load and will not register in script editor unless cmds.evalDeferred() is used
# Menu creation and tools may fail to start if not deferred.

Use this file to:
# Get setup folders path via "returnpath.py" (could be redundant, mayeb use module path?)
# From that path add necessary plug-in and script paths (could this be handled already by module as well?)

The above may be redundant if plugin folder is in the right location relative to module
May still need to add 3rdParty > plug-ins folder as a plugin path

# =============================================================================================================================
# This file should only get the main tools repo setup and kick the boot manager which will then manage which modules are used.
# Keep all module requirements tied to their module startup (ig. Core module startup should ensure its dependencies are functional)
# =============================================================================================================================
"""

import logging
import sys

import maya.cmds as cmds

import returnpath

logging.basicConfig()
log = logging.getLogger('gTools')
log.setLevel(logging.INFO)

# Try to import Startup Module (Startup Folder)
try:
    import startup

    # reload (startup)
    startupImported = True
except:
    startupImported = False

######################## 
## Path Method ##
########################
## Ensures that the pipelines path is added to sys path, allowing us to import directly from it
## Maya boots > runs .mod > runs userSetup.py in dir from .mod > uses this code to add desired dir to sys path
# todo Convert userSetup to instead run the boot manager module which shouldnt need this weird return path setup. It can return its own path
#       unlike the userSetup files. 
modulepath = returnpath.getpath()
sys.path.append(modulepath)

########################
## Boot Methods ##
########################
## TODO: NEED TO ADD BOOT MANAGER UI THAT DEFINES WHAT EXTRA STARTUPS TO BOOT
## TODO: PROBABLY RIP OUT BOOT CODE INTO BOOT MANAGER MODULE (keep boot module in startup folder and kick from here)

def bootImporter(impDic):
    '''
	Imports startup modules. Requires the following dict syntax:
	{
	'fileName':'module_startup.py',
	'importName':'module_startup',
	'toolName':'module'
	}

	@param impDic - dict with with module info. See above.
	'''
    # join startup folder with startup file to create import path - startup.XXXXX
    importPath = 'startup.{0}'.format(impDic['importName'])

    exec ('import {0} as tempMod'.format(importPath))
    reload(tempMod)
    tempMod.start()


def bootLoader():
    """ Load all startup modules and initiate the toolset """

    log.info(('#' * 15 + '  Module Boot Manager - Start!  ' + '#' * 15))

    # If Startup Module imported then continue if True
    if startupImported == True:
        # Test if Core Startup runs then continue if True
        if bootCore() == True:
            # Run through rest of Startups if Core Startup ran successfully
            bootStartups()
    else:
        log.error('Failed to Initiate Startup Module')

    log.info(('#' * 15 + '  Module Boot Manager - End!  ' + '#' * 15))


########################
## Boot Core ##
########################
def bootCore():
    """ Boot core module for toolset. This module is required for all others to function """

    if startup.core == {}:
        log.error('Core Module : Missing ')
        return False

    log.info('Core Module : Loading')
    try:
        bootImporter(startup.core)
        log.info('Core Module : Loaded')
        return True

    except:
        log.error('Core Module : Failed to Load')
        return False


########################
## Boot Startups ##
########################
def bootStartups(importPath=None):
    """ Run through all additional startup modules """

    startupList = startup.startupList
    if not startupList:
        log.warning('Startup List Empty - Nothing to Load')
        return False

    # modules = {} dict for failed module import attempt below
    for i in startupList:
        # try import and run start function
        try:
            bootImporter(i)

        except:
            log.info('Module : {0} failed to run start function'.format(importPath))


########################
## Deferred Function ##
########################
cmds.evalDeferred(bootLoader, lp=True)
