#!/usr/bin/env python

import fuse
from cloud import Swift
from fs import FS
import stat
import errno

# Stubs for Stat
import os
from datetime import datetime

# Logging actions
import logging

LOG_FILENAME = "LOG"
logging.basicConfig(filename=LOG_FILENAME,level=logging.INFO,)
# /Logging actions

# FUSE version at the time of writing. Be compatible with this version.
fuse.fuse_python_api = (0, 2)

class Stat( fuse.Stat ):
    def __init__( self ):
        self.st_ino = 0
        self.st_dev = 0
        self.st_mode = stat.S_IFDIR | 0777 # full access dir TODO: change
        self.st_nlink = 2 # 2 hardlinks, as for empty dir  TODO: change
        self.st_uid = os.getuid() # current uid TODO: change
        self.st_gid = os.getgid() # current gid TODO: change
        self.st_size = 4096 # dirsize TODO: change
        now = 0 # datetime.utcnow()
        self.st_atime = now
        self.st_mtime = now
        self.st_ctime = now

class CFuse( fuse.Fuse ):
    """
    Cumulonimbus filesystem Fuse entry point. Implements methods called by
    Fuse - translates and passes them to FS.
    """

    def __init__(self, *args, **kwargs):
        logging.info("[mount][init]")
        self.fs = None
        super(CFuse, self).__init__(*args, **kwargs)
        self.parser.add_option(mountopt="user", help="describes Swift user")
        self.parser.add_option(mountopt="key", help="describes Swift key")
        self.parser.add_option(mountopt="authurl", help="describes Swift auth url")

    def main( self ):
        if( self.fs is None ):
            raise "Filesystem was not set!"
        super(CFuse, self).main()

    def fsinit( self ):
        assert( self.fs is not None )
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

    def readdir( self, path, offset, dh=None ):
        logging.info("[readdir][init]")
        for x in self.fs.readdir( path, offset, dh ):
            yield fuse.Direntry(x)
        logging.info("[readdir][done]")

    def releasedir( self, path, dh=None ):
        logging.info("[releasedir][init]")
        logging.info("[releasedir][done]")

    def mkdir( self, path, mode ):
        logging.info("[mkdir][init]")
        retval = self.fs.mkdir( path, mode )
        if retval is None:
            logging.info("[mkdir][done]")
            return 0
        return retval

    def access( self, path, flags ):
        logging.info("[access][init] [%s] [%s]" % (path, oct(flags) ) )
        retval = self.fs.access( path, flags )
        if retval == 0:
            logging.info("[access][done]")
        return retval

    def getattr( self, path ):
        logging.info("[getattr][init] [%s]" % (path) )
        if self.fs.access( path, 0 ) == -errno.ENOENT:
            err = -errno.ENOENT
            return err # TODO: call self.fs.getattr( path ) when implemented
        retval = Stat()# self.fs.getattr( path )
        logging.info("[getattr][done]")
        return retval

    def statfs( self ):
        logging.info("[statfs][init]")
        stat = fuse.StatVfs() # TODO: fill it
        logging.info("[statfs][done]")
        return stat

    def chmod( self, path, mode ):
        logging.info("[chmod][init] [%s] [%s]" % (path, oct(mode)) )
        retval = self.fs.chmod( path, mode )
        if( retval is None ):
            logging.info("[chmod][done]")
            return 0
        return -errno.EINVAL # TODO: other error(s)?

    def mknod(self, path, mode, rdev):
        logging.info("[mknod][init]")
        if( mode & os.S_IFREG == 0 ):
            return -errno.EOPNOTSUPP
        retval = self.fs.create(path, mode & 0777, rdev)
        if retval == 0:
            logging.info("[mknod][done]")
        return retval

if __name__ == '__main__':
    def main():
        cfuse = CFuse( dash_s_do='setsingle' )
        cfuse.parse( errex=1 )
        cfuse.multithreaded = 0
        cmd = cfuse.cmdline[0]
        swift = Swift( cmd.authurl, cmd.user, cmd.key )
        cfuse.fs = FS( swift )
        cfuse.main()
    main()
