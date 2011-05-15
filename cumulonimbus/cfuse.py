#!/usr/bin/env python

import fuse
import stat
import errno

# Logging actions
import logging

LOG_FILENAME = "LOG"
logging.basicConfig(filename=LOG_FILENAME,level=logging.INFO,)
# /Logging actions

# FUSE version at the time of writing. Be compatible with this version.
fuse.fuse_python_api = (0, 2)

class CFuse( fuse.Fuse ):
    """
    Cumulonimbus filesystem Fuse entry point. Implements methods called by
    Fuse - translates and passes them to FS.
    """

    def __init__(self, fs, *args, **kwargs):
        logging.info("[mount][init]")
        self.fs = fs
        super(CFuse, self).__init__(*args, **kwargs)

    def fsinit( self ):
        logging.info("[mount][done]")

    def fsdestroy( self ):
        logging.info("[unmount][init]")
        logging.info("[unmount][done]")

    def getattr(self, path):
        if path == "/":
            return fuse.Stat(st_ino = 1, st_mode = (stat.S_IFDIR | 0755),
                    st_dev = 0, st_nlink = 1, st_uid = 0, st_gid = 0,
                    st_size = 0, st_atime = 0, st_mtime = 0, st_ctime = 0)
        else:
            return -errno.ENOENT

    def opendir(self, path):
        return self.fs.opendir(path)

    def releasedir(self, path, dh):
        return self.fs.releasedir(path, dh)

    def readdir(self, path, offset, dh):
        return self.fs.readdir(path, offset, dh)

    def create(self, path, mode, rdev):
        return self.fs.create(path, mode, rdev)

    def write(self, path, buf, offset, fh):
        return self.fs.write(path, buf, offset, fh)

    def access(self, path, flags):
        return self.fs.access(path, flags)

    def mkdir(self, path, mode):
        return self.fs.mkdir(path, mode)

    def rename(self, old, new):
        return self.fs.rename(self, old, new)

if __name__ == '__main__':
    def main():
        swift = None # Swift()
        fs = FS( swift )
        cfuse = CFuse( fs, dash_s_do='setsingle' )
        cfuse.parse( errex=1 )
        cfuse.multithreaded = 0
        cfuse.main()
    #from cloud import Swift
    from fs import FS
    main()
