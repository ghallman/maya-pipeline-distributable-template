"""
Utilities for common file functions
"""

# base imports
import os
import logging

# logging
logging.basicConfig()
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)


class Utilities(object):
    '''
    Utility class for common file functions
    # TODO: this really doesnt need to be a class
    '''

    def __init__(self):
        pass

    def checkOrMakeFileDirectory(myPath):
        """
        Pass in a path. Check if parent directory exists. If not, make it.

        :param string: path
        :return: parent directory string
        """

        d = os.path.dirname(myPath)
        if not os.path.exists(d):
            os.makedirs(d)
            log.info('created directory: \n{0}'.format(d))

        return d
    
    def makeTuple(self, *args):
        """
        Flatten arguements into a tuple

        :param args: Objects to add into tuple
        :return: Biggie Tuple
        """
        myTuple = []
        # Does not take into account dictionaries.Make more robust as needed.
        for i in args:
            myType = type(i)
            if myType is list:
                myTuple.extend(i)
            elif myType is tuple:
                myTuple.extend(list(i))
            else:
                myTuple.append(i)
        # Tuples are immutable so add everything to large list then convert back
        myTuple = tuple(set(myTuple))
        return myTuple

    def getFiles(self, directory, ext='', prefix='', suffix=''):
        """
        Get list of full path files from the given directory with the given file extenstions, prefixes and suffixes

        :param dir: Directory to grab files from
        :param args: File extension(s) to filter files by
        :param prefix: Prefix(s) to filter files by
        :param suffix: Suffix(s) to filter files by
        :return: List of files with full path
        """

        allowedTypes = [str, list]
        if type(directory) not in allowedTypes:
            cmds.error('Arg directory must be provided a string or list of directories')

        if type(ext) in allowedTypes:
            ext = self.makeTuple(ext)
        else:
            cmds.error('Arg ext must be provided a string or list of extensions')

        if type(prefix) in allowedTypes:
            prefix = self.makeTuple(prefix)
        else:
            cmds.error('Arg prefix must be provided a string or list of prefixes')

        if type(suffix) in allowedTypes:
            suffix = self.makeTuple(suffix)
        else:
            cmds.error('Arg suffix must be provided a string or list of suffixes')

        if type(directory) is str:
            directory = [directory]
        set(directory)

        fileList = []
        for path in directory:
            # Use list comprehension to filter and add directory path to files
            tempList = [(os.path.join(path, i)) for i in os.listdir(path) if
                        i.endswith(ext) and # sorting extensions
                        os.path.basename(i).startswith(prefix) and  # sorting prefixes
                        os.path.splitext(os.path.basename(i))[0].endswith(suffix)] # sorting suffixes
            fileList.extend(tempList)

        return list(set(fileList))

    def getMayaFiles(self,directory):
        """
        Get list of full path maya files from the given directory

        :param dir: Directory to grab files from
        :return: List of maya files with full path
        """
        ext = ['.ma','.mb']
        mayaFileList = self.getFiles(directory, ext=ext)
        return mayaFileList

    def getFbxFiles(self,directory):
        """
        Get list of full path fbx files from the given directory

        :param dir: Directory to grab files from
        :return: List of fbx files with full path
        """
        fbxFileList = self.getFiles(directory, ext='.fbx')
        return fbxFileList
