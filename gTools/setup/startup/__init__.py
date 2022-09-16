"""
Init to grab startup files

Assembles startup modules into the following dict syntax:
{
'fileName':'module_startup.py',
'importName':'module_startup',
'toolName':'module'
}
"""

import os

######################## 
## Core Startup ##
########################
coreFile = 'gTools_startup.py'  # Core Startup file should be booted before all others
core = {}
try:
    # assemble core startup dict
    core['fileName'] = coreFile
    core['importName'] = coreFile.split('.')[0]
    core['toolName'] = coreFile.split('_startup.py')[0]
except:
    # core dict failed
    pass

ignoreList = ['template_startup.py', coreFile]

######################## 
## Additional Startups ##
########################

try:
    # assemble dict for each tool and ignore any file in ignoreList
    startupList = [{'fileName': f} for f in os.listdir(os.path.dirname(__file__)) if f.endswith('_startup.py') and f not in ignoreList]

    for f in startupList:
        f['importName'] = f['fileName'].split('.')[0]
        f['toolName'] = f['fileName'].split('_startup.py')[0]
except:
    startupList = []
