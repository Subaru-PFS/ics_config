import os

def getPackageName(rootDir="python"):
    """Return the package name as the sole visible directory under rootDir.
    
    Raise RuntimeError if there is not exactly one visible directory under rootDir.
    """
    dirIter = os.walk(rootDir)
    (dirPath, dirList, fileList) = dirIter.next()
    dirList = [dirName for dirName in dirList if not dirName.startswith(".")]
    if len(dirList) != 1:
        raise RuntimeError("Found %s instead of 1 directory" % (dirList,))
    return dirList[0]
        
