from __future__ import print_function
from __future__ import absolute_import
import distutils.core
import glob
import os
from . import find
from . import getPackageName

def setup(debug=False, copyUps=False, **kargs):
    """Helpful version of distuils.core.setup
    
    Inputs:
    - debug: if True then print diagnostic information
    
        You may replace the following items:
    - name: name of package; defaults to sole subdirectory of "python"
    - package_dir: {package name: package subdir}; defaults to {name: "python"}
    - packages: list of packages and sub-packages making up this package;
        defaults to all python packages and sub-packages in "python"
    - scripts: list of files to install as executables;
        omitted by default because the contents of bin are installed via data_dirs

        You may supplement the following items:
    - data_dirs: a list of directories whose contents will be recursivly copied;
        always includes: bin, doc, etc, examples, lib, ups
        Note: the files in data_dirs are added to the data_files argument.
    - data_files: a list of (dir, list of files), with these rules:
        - Recursive directories require a separate entry for each subdirectory
        - All file paths must be relative to your package root directory, even files in subdirs
        For example to install these files:
            data/a.txt, data/b.txt data/subdata/c.txt
        set data_files = [
              ("data", ["data/a.txt", "data/b.txt"]),
              ("data/subdata", ["data/subdata/c.txt"])
        ]
        It is usually simpler to use data_dirs, or, if you must exclude specific files
        or directories then consider the function sdss3tools.files.findDataFiles.
        
    All paths are relative to your package root directory
    (the directory containing your setup.py file).
    """
    print("copyUps: %s" % (copyUps))
    
    if "name" not in kargs:
        kargs["name"] = getPackageName.getPackageName("python")
    name = kargs["name"]
    if "package_dir" not in kargs:
        kargs["package_dir"] = {'': 'python'}
    if "packages" not in kargs:
        kargs["packages"] = find.findPackages("python")

    if "install_platlib" not in kargs:
        kargs['install_platlib'] = "$base/python"
    if "install_purelib" not in kargs:
        kargs['install_purelib'] = "$base/python"
        
    stdDataDirs = ("bin", "doc", "etc", "examples", "lib")
    if copyUps:
        stdDataDirs += ("ups",)
        print("add ups dir to copy")
    data_dirs = list(set(kargs.pop("data_dirs", ())) | set(stdDataDirs))
    data_files = list(kargs.get("data_files", ()))
    for dirName in sorted(data_dirs):
        data_files += find.findDataFiles(dirName)
    kargs["data_files"] = data_files
    if debug:
        print("Keyword arguments for setup:")
        for key in sorted(kargs.keys()):
            if key != "data_files":
                print("* %s: %s" % (key, kargs[key]))
            else:
                print("* %s:" % (key,))
                for dirPath, fileList in data_files:
                    print(" ", dirPath)
                    for fn in fileList:
                        print("   ", fn)

    distutils.core.setup(**kargs)
