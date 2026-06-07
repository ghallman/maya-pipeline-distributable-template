"""
Utilities for common file functions.

Plain module functions (the old `Utilities` class added nothing). Kept Maya-free
on purpose - this layer raises standard exceptions instead of calling cmds.error,
so it can be imported and unit-tested outside a running Maya session.
"""

# base imports
import os
import logging

# logging
log = logging.getLogger(__name__)


def checkOrMakeFileDirectory(myPath):
    """
    Given a path, ensure its parent directory exists (create it if not).

    :param myPath: path whose parent directory should exist
    :return: parent directory string
    """
    d = os.path.dirname(myPath)
    if d and not os.path.exists(d):
        os.makedirs(d)
        log.info('created directory:\n%s', d)
    return d


def makeTuple(*args):
    """
    Flatten arguments (scalars/lists/tuples) into a de-duplicated tuple.

    :param args: objects to combine
    :return: tuple of unique items
    """
    collected = []
    # Does not recurse into dictionaries; extend as needed.
    for i in args:
        if isinstance(i, list):
            collected.extend(i)
        elif isinstance(i, tuple):
            collected.extend(list(i))
        else:
            collected.append(i)
    return tuple(set(collected))


def getFiles(directory, ext='', prefix='', suffix=''):
    """
    Get full-path files from the given directory/directories filtered by file
    extension(s), prefix(es) and suffix(es).

    :param directory: directory string or list of directories
    :param ext: file extension(s) to filter by
    :param prefix: prefix(es) to filter by
    :param suffix: suffix(es) to filter by
    :return: list of matching files with full path
    :raises TypeError: if any argument is not a str or list
    """
    allowedTypes = (str, list)
    if not isinstance(directory, allowedTypes):
        raise TypeError('Arg directory must be a string or list of directories')
    if not isinstance(ext, allowedTypes):
        raise TypeError('Arg ext must be a string or list of extensions')
    if not isinstance(prefix, allowedTypes):
        raise TypeError('Arg prefix must be a string or list of prefixes')
    if not isinstance(suffix, allowedTypes):
        raise TypeError('Arg suffix must be a string or list of suffixes')

    # normalize filters to tuples for str.startswith/endswith
    ext = makeTuple(ext)
    prefix = makeTuple(prefix)
    suffix = makeTuple(suffix)

    if isinstance(directory, str):
        directory = [directory]

    fileList = []
    for path in directory:
        tempList = [os.path.join(path, i) for i in os.listdir(path) if
                    i.endswith(ext) and                                            # extensions
                    os.path.basename(i).startswith(prefix) and                     # prefixes
                    os.path.splitext(os.path.basename(i))[0].endswith(suffix)]     # suffixes
        fileList.extend(tempList)

    return list(set(fileList))


def getMayaFiles(directory):
    """
    Get full-path Maya files (.ma/.mb) from the given directory.

    :param directory: directory to search
    :return: list of Maya files with full path
    """
    return getFiles(directory, ext=['.ma', '.mb'])


def getFbxFiles(directory):
    """
    Get full-path FBX files from the given directory.

    :param directory: directory to search
    :return: list of FBX files with full path
    """
    return getFiles(directory, ext='.fbx')
