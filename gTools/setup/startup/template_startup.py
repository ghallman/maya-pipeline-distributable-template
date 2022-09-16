"""
Startup file to load menus and other needed modules

Startup files should always follow the convention XXXX_startup.py
The string is split via boot manager and XXXX will be that modules name
"""
import os

import maya.cmds as cmds
import maya.mel as mel

# get startup package name
packName = (__name__)
if (__name__).endswith('_startup'):
    packName = packName.split('_startup')[0]
if '.' in __name__:
    packName = packName.split('.')[-1]

import logging
logging.basicConfig()
log = logging.getLogger(packName)
log.setLevel(logging.INFO)


# log.info('PRE BOOT LOG TEST')

######################## 
## Package Methods ##
########################


######################## 
## Boot Method ##
######################## 

def start():
    """ Runs the module """

    # log.info('Boot Status : RUNNING')
    try:
        intentionalFail()  # REPLACE WITH YOUR METHODS

        log.info('Boot Status : SUCCESS')
    except:
        log.info('Boot Status : FAILED')
