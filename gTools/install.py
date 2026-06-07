__author__ = 'Gaige Hallman'

"""
Drag and drop installer for the gTools pipeline.

Without moving this file from its original location in the pipeline root, drag this
install.py onto your Maya viewport. Its location is used to write the pipeline's
.mod file into Maya's user `modules` folder, pointing Maya back at this location.

The module file is generated from the brand config (gTools/brand.py), so rebranding
or white-labeling only requires editing that one file - no changes here.
"""
## base Imports ##
import os
import sys
import stat
import logging

## maya Imports ##
import maya.cmds as cmds

# Make the pipeline root importable so we can read the brand config.
INSTALL_SOURCE = os.path.dirname(os.path.abspath(__file__))
if INSTALL_SOURCE not in sys.path:
    sys.path.insert(0, INSTALL_SOURCE)
import brand

# logging
logging.basicConfig()
log = logging.getLogger(brand.get('logger_tag', 'gTools'))
log.setLevel(logging.DEBUG)

# constants
MAYA_MODULES_PATH = os.path.join(cmds.internalVar(userAppDir=True), 'modules')
TOOL_NAME = brand.get('display_name', 'gTools')
MODFILE = brand.mod_filename()


def checkOrMakeFileDirectory(myPath):
    """
    Pass in a path. Check if parent directory exists. If not, make it.

    :param myPath: path whose parent directory should exist
    :return: parent directory string
    """
    d = os.path.dirname(myPath)
    if d and not os.path.exists(d):
        os.makedirs(d)
        log.info('created directory: \n{0}'.format(d))
    return d


def buildModContents():
    """
    Build the Maya .mod file contents from the brand config and this location.

    Format:
        + <name> <version> <path-to-pipeline-root>
        scripts: setup
    """
    name = brand.get('name', 'gTools')
    version = brand.get('version', '1.0')
    return "+ {0} {1} {2}\nscripts: setup\n".format(name, version, INSTALL_SOURCE)


def onMayaDroppedPythonFile(*args):
    log.info('Installing {} module'.format(TOOL_NAME))

    target = os.path.join(MAYA_MODULES_PATH, MODFILE)
    log.info('Target = {}'.format(target))
    log.info('Tools Path = {}'.format(INSTALL_SOURCE))

    try:
        checkOrMakeFileDirectory(target)

        if os.path.exists(target):
            # unlock target file for overwrite
            os.chmod(target, stat.S_IWRITE)

        with open(target, "wt") as fout:
            fout.write(buildModContents())

        log.info('Successfully created {} .mod file'.format(TOOL_NAME))
        log.info('Please restart Maya')

        # pop up
        message = """Successfully created {} .mod file
        Please restart Maya""".format(TOOL_NAME)
        cmds.confirmDialog(title=TOOL_NAME, message=message, ma="center")

    except Exception as exc:
        log.error("Failed to create {} .mod file: {}".format(TOOL_NAME, exc))

        # pop up
        message = """Failed to create {} .mod file""".format(TOOL_NAME)
        cmds.confirmDialog(title=TOOL_NAME, message=message, icon="critical", ma="center")
