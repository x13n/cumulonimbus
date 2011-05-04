#!/usr/bin/env python

import fuse

# Logging actions
import logging

LOG_FILENAME = "LOG"
logging.basicConfig(filename=LOG_FILENAME,level=logging.INFO,)
# /Logging actions

# FUSE version at the time of writing. Be compatible with this version.
fuse.fuse_python_api = (0, 2)

class Stat( fuse.Stat ):
    pass

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
        self.fs = None
        logging.info("[unmount][done]")

    def link( self, target, name ):
        # no hard links support
        return -errno.EOPNOTSUPP

    def opendir( self, path ):
        logging.info("[opendir][init]")
        retval = self.fs.opendir( path )
        if retval is None:
            logging.info("[opendir][done]")
        return retval

    def mkdir( self, path, mode ):
        logging.info("[mkdir][init]")
        self.fs.mkdir( path, mode )
        logging.info("[mkdir][done]")

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
