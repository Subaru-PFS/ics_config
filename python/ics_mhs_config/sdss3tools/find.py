from distutils.core import setup
import distutils.util
import fnmatch
import os

def findPackages(where='.', exclude=()):
    """Return a list of all Python package names found within a directory.
    
    The returned data is in the form used by distutils for the packages argument to setup.

    Inputs:
    - where: path of base directory.
    - exclude: a sequence of package names or glob expressions to exclude.
    
    From setuptools (which one cannot easily import without ruining one's ability
    to use distutils and avoid eggs, though pip might solve that!).
    """
    out = []
    stack=[(where, '')]
    while stack:
        where,prefix = stack.pop(0)
        for name in os.listdir(where):
            fn = os.path.join(where,name)
            if ('.' not in name and os.path.isdir(fn) and
                os.path.isfile(os.path.join(fn,'__init__.py'))
            ):
                out.append(prefix+name); stack.append((fn,prefix+name+'.'))
    for pat in list(exclude)+['ez_setup']:
        out = [item for item in out if not fnmatch.fnmatchcase(item,pat)]
    return out

def findDataFiles(where, excludeFiles=(".*", "*~", "#*#"), excludeDirs=(".*",)):
    """Return all files found within a directory in the form used by distutils for data_files.
    
    Returns a list of (dir path, files in dir), one entry for each dir and subdirectory in where.
    Dir path and all file paths are relative to the current working directory.
    This is the format used by distutils for the data_files argument to setup.
    
    Inputs:
    - where: path of base directory.
    - excludeFiles: a sequence of glob expressions for file names to exclude.
    - excludeDirs: a sequence of glob expressions for directory names to exclude.
    """
    out = []
    for dirPath, dirNames, fileNames in os.walk(where):
        for excludePat in excludeDirs:
            dirNames[:] = [dn for dn in dirNames if not fnmatch.fnmatch(dn, excludePat)]
        for excludePat in excludeFiles:
            fileNames[:] = [fn for fn in fileNames if not fnmatch.fnmatch(fn, excludePat)]
        filePaths = [os.path.join(dirPath, fn) for fn in fileNames]
        out.append((dirPath, filePaths))
    return out
    
def findFiles(where, excludeFiles=(".*", "*~", "#*"), excludeDirs=(".*",)):
    """Return a list all files recusively found within directory 'where'.
    
    The file paths are relative to the current working directory.

    Inputs:
    - where: path of base directory.
    - excludeFiles: a sequence of glob expressions for file names to exclude.
    - excludeDirs: a sequence of glob expressions for directory names to exclude.
    """
    out = []
    for dirPath, dirNames, fileNames in os.walk(where):
        print "after walk dirPath=%s, dirNames=%s, fileNames=%s" % (dirPath, dirNames, fileNames)
        for excludePat in excludeDirs:
            dirNames[:] = [dn for dn in dirNames if not fnmatch.fnmatch(dn, excludePat)]
        for excludePat in excludeFiles:
            fileNames[:] = [fn for fn in fileNames if not fnmatch.fnmatch(fn, excludePat)]
        out += [os.path.join(dirPath, fn) for fn in fileNames]
        print "before iter dirPath=%s, dirNames=%s, fileNames=%s" % (dirPath, dirNames, fileNames)
    return out
