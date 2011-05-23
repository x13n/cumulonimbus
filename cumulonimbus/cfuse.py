#!/usr/bin/env python

import fuse
from cloud import Swift
from fs import FS, Stat
import stat
import errno

# Stubs for Stat
import os
from datetime import datetime

# Logging actions
import logging
from inspect import stack
from traceback import format_exc

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
        return self._handle( self._fsdestroy )

    def _fsdestroy( self ):
        self.fs = None

    def link( self, target, name ):
        # no hard links support
        return -errno.EOPNOTSUPP

    def opendir( self, path ):
        return self._handle( self._opendir, path )

    def _opendir( self, path ):
        retval = self.fs.opendir( path )
        if retval is not None:
            raise ErrnoException( retval )

    def readdir( self, path, offset, dh=None ):
        return self._handle( self._readdir, path, offset, dh )

    def _readdir( self, path, offset, dh ):
        for x in self.fs.readdir( path, offset, dh ):
            yield fuse.Direntry(x)

    def releasedir( self, path, dh=None ):
        return self._handle( self._releasedir, path, dh )

    def _releasedir( self, path, dh ):
        pass

    def mkdir( self, path, mode ):
        return self._handle( self._mkdir, path, mode )

    def _mkdir( self, path, mode ):
        retval = self.fs.mkdir( path, mode )
        if retval is None:
            return 0
        return retval

    def access( self, path, flags ):
        return self._handle( self._access, path, flags )

    def _access( self, path, flags ):
        retval = self.fs.access( path, flags )
        if retval != 0:
            raise ErrnoException( retval )
        return 0

    def getattr( self, path ):
        return self._handle( self._getattr, path )

    def _getattr( self, path ):
        retval = self.fs.getattr( path )
        if isinstance(retval, Stat):
            return retval
        raise ErrnoException( retval )

    def statfs( self ):
        return self._handle( self._statfs )

    def _statfs( self ):
        stat = fuse.StatVfs() # TODO: fill it
        return stat

    def chmod( self, path, mode ):
        return self._handle( self._chmod, path, mode )

    def _chmod( self, path, mode ):
        retval = self.fs.chmod( path, mode )
        if( retval is None ):
            return 0
        raise ErrnoException( -errno.EINVAL ) # TODO: other error(s)?

    def mknod(self, path, mode, rdev):
        return self._handle( self._mknod, path, mode, rdev )

    def _mknod(self, path, mode, rdev):
        if( mode & stat.S_IFREG == 0 ):
            raise ErrnoException( -errno.EOPNOTSUPP )
        retval = self.fs.create(path, mode & 0777, rdev)
        if retval is None:
            return 0
        raise ErrnoException( retval )

    def chown( self, path, uid, gid ):
        return self._handle( self._chown, path, uid, gid )
    
    def _chown( self, path, uid, gid ):
        pass

    def utime(self, path, times):
        return self._handle( self._utime, path, times )

    def _utime(self, path, times):
        pass

    def rename(self, src, dst):
        return self._handle( self._rename, src, dst )

    def _rename(self, src, dst):
        retval = self.fs.rename(src, dst)
        if not retval is None:
            raise ErrnoException(retval)

    def symlink(self, target, name):
        return self._handle(self._symlink, target, name)

    def _symlink(self, target, name):
        retval = self.fs.symlink(target, name)
        if not retval is None:
            raise ErrnoException( retval )

    def unlink(self, path):
        return self._handle(self._unlink, path)

    def _unlink(self, path):
        retval = self.fs.unlink( path )
        if not retval is None:
            raise ErrnoException( retval )

    def rmdir(self, path):
        return self._handle(self._rmdir, path)

    def _rmdir(self, path):
        retval = self.fs.rmdir( path )
        if not retval is None:
            raise ErrnoException( retval )

    def readlink(self, path):
        return self._handle(self._readllink, path)

    def _readllink(self, path):
        retval = self.fs.read(path)
        if not isinstance(retval, str):
            raise ErrnoException( retval )
        return retval

    def _handle(self, method, *args):
        name = stack()[1][3]
        logging.info("[%s][init] <- %s" % (name, map(str, args)))
        try:
            retval = method( *args )
        except ErrnoException as e:
            logging.info("[%s][errno] -> %s" % (name, e.errno))
            return e.errno
        except Exception as e:
            logging.error("[%s][exception] %s: %s" % (name, e.__class__.__name__, str(e)))
            logging.error(format_exc())
            return -errno.EINVAL
        else:
            logging.info("[%s][done] -> %s" % (name, str(retval)))
            return retval

class ErrnoException( Exception ):
    def __init__( self, errno ):
        self.errno = errno

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
