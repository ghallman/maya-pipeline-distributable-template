__author__ = 'Gaige Hallman'

"""
Drag and drop installer for gTools pipeline

Without moving this file from its original location in the pipeline root, drag this install.py file onto your maya viewport.
It's file location will be used to setup the pipeline's .mod file
"""
## base Imports ##
import os
import shutil
import stat
import logging

## maya Imports ##
import maya.cmds as cmds


# logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# constants
MAYA_MODULES_PATH = os.path.join(cmds.internalVar(userAppDir=True), 'modules')
INSTALL_SOURCE = os.path.dirname(__file__)
TOOL_NAME = "gTools"
MODFILE = "{}.mod".format(TOOL_NAME)


def checkOrMakeFileDirectory(myPath):
    """
    Pass in a path. Check if parent directory exists. If not, make it.
    
    :param path string: 
    :return: parent directory string
    """
    
    d = os.path.dirname(myPath)
    if not os.path.exists(d):
        os.makedirs(d)
        log.info('created directory: \n{0}'.format(d))

    return d

def onMayaDroppedPythonFile(*args):
    log.info('Installing {} module'.format(TOOL_NAME))

    source = os.path.join(INSTALL_SOURCE, MODFILE)
    target = os.path.join(MAYA_MODULES_PATH, MODFILE)

    log.info('Source = {}'.format(source))
    log.info('Target = {}'.format(target))

    try:
        checkOrMakeFileDirectory(target)
        
        if os.path.exists(target):
            # unlock target file for overwrite
            os.chmod(target, stat.S_IWRITE)
            
        # open source mod file using "with" so file operation auto closes after use
        # read text mode
        with open(source, "rt") as fin:
            # open what will be the target mod file
            #  write text mode
            with open(target, "wt") as fout:
                for line in fin:
                    # write new line per line in source file
                    fout.write(line.replace('[REPLACE_WITH_TOOLS_DIR]', INSTALL_SOURCE))

        log.info('Successfully created {} .mod file'.format(TOOL_NAME))
        log.info('Tools Path - {}'.format(INSTALL_SOURCE))
        log.info('Please restart maya')

        # pop up
        message = """Successfully created {} .mod file
        Please restart maya""".format(TOOL_NAME)
        cmds.confirmDialog(title=TOOL_NAME, message=message, ma="center")

    except:
        log.info("""Failed to copy {} .mod file""".format(TOOL_NAME))

        # pop up
        message = """Failed to copy {} mod file""".format(TOOL_NAME)
        cmds.confirmDialog(title=TOOL_NAME, message=message, icon="critical", ma="center")



