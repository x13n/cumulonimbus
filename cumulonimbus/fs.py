import errno
import stat
import os
from os.path import split, join
from file import File
from dir import Dir
from symlink import Symlink
from cloud import NoSuchFileOrDirectory

class Stat:
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

    @classmethod
    def for_file(cls, mode, size):
        st = Stat()
        st.st_mode = stat.S_IFREG | mode
        st.st_size = size
        return st

    @classmethod
    def for_dir(cls, mode):
        st = Stat()
        st.st_mode = stat.S_IFDIR | mode
        st.st_nlink = 1
        return st

    @classmethod
    def for_symlink(cls, mode, size):
        st = Stat()
        st.st_mode = stat.S_IFLNK | mode
        st.st_size = size
        return st

class FS:
    """
    Responsible for handling the file system logic. All requests coming from FUSE
    are forwarded to an instance of this class. Values returned by its methods
    are compatible with values expected by FUSE Python bindings. In case of
    errors negative integers are returned
    """

    def __init__(self, swift):
        """
        An FS instance is created when a file system is mounted. The first
        argument should be a cumulonimbus.swift.Swift instance.
        """
        self.swift = swift
        pass

    def opendir(self, path):
        """
        Called when a directory is opened. Returns None.
        """
        try:
            self._file_has_to_exist(path)
        except PathException as ex:
            return ex.error

    def releasedir(self, path, dh):
        """
        Closes a directory opened with opendir.
        """
        assert(dh is None)

    def readdir(self, path, offset, dh):
        """
        Yields strings with names of nodes in the given directory.
        """
        assert(dh is None)
        try:
            self._file_has_to_exist(path)
        except PathException:
            return
        if path != '/':
            head, tail = split(path)
            if tail not in self.swift.get(head).children.names():
                return
        yield "."
        yield ".."
        for name in self.swift.get(path).children.names():
            yield name

    def create(self, path, mode, rdev):
        """
        Creates a new file with a given mode and returns None.
        """
        assert(mode >= 0)
        self.swift.put(path, File(mode, ''))

    def write(self, path, buf, offset, fh):
        """
        Writes contents of buf to file at path beginning at the given offset.
        Returns the number of successfully written bytes.
        """
        assert(fh is None)

    def access(self, path, flags):
        """
        Checks accessibility of a given file.
        """
        try:
            self._file_has_to_exist(path)
        except PathException as ex:
            return ex.error
        return 0

    def mkdir(self, path, mode):
        """
        Writes contents of buf to file at path beginning at the given offset.
        Returns the number of successfully written bytes.
        """
        try:
            parent, _ = split(path)
            self._file_has_to_exist(parent)
        except PathException as ex:
            return ex.error
        self.swift.mkdir(path)

    def rename(self, src, dst):
        """
        Moves a file or a directory from one path to another. In case of
        directories uses a recursive approach.
        """
        if src == dst:
            # If src is equal to dst there's nothing we can do.
            return
        try:
            inode = self.swift.get(src)
            if isinstance(inode, File):
                self._mv_file(src, dst)
            elif isinstance(inode, Dir):
                self._mv_dir(src, dst)
            else:
                raise Exception("Unexpected inode type: %s" % type(inode))
        except NoSuchFileOrDirectory:
            return -errno.ENOENT

    def read(self, path):
        """
        Returns file contents
        """
        try:
            file = self.swift.get(path)
            assert(isinstance(file, File)) # kernel wouldn't ask to read a dir like this
            return file.contents
        except NoSuchFileOrDirectory:
            return -errno.ENOENT

    def _mv_dir(self, src, dst):
        src_dir = self.swift.get(src)
        assert(not src_dir.children is None)
        self.mkdir(dst, src_dir.mode)
        # Now recursively move contents of the src directory to the dst.
        for child in src_dir.children.names():
            if child in ['.', '..']:
                continue
            err = self.rename(join(src, child), join(dst, child))
            if err == -errno.ENOENT:
                raise NoSuchFileOrDirectory
            elif not err is None:
                # Not good, this isn't an error we're expecting to encounter.
                raise Exception(repr(err))
        self.swift.rm(src)
        assert(not self.swift.get(dst).children is None)

    def _mv_file(self, src, dst):
        assert(not self.swift.get(src).contents is None)
        self.swift.put(dst, self.swift.get(src))
        self.swift.rm(src)
        assert(not self.swift.get(dst).contents is None)

    def unlink(self, path):
        """
        Removes a file.
        """
        try:
            self.swift.rm(path)
        except NoSuchFileOrDirectory:
            return -errno.ENOENT

    def rmdir(self, path):
        """
        Removes a dir.
        """
        try:
            self.swift.rm(path, True)
        except NoSuchFileOrDirectory:
            return -errno.ENOENT

    def symlink(self, target, path):
        """
        Creates a symbolic link.
        """
        self.swift.put(path, Symlink(0777, target))

    def getattr(self, path):
        try:
            inode = self.swift.get(path)
            if isinstance(inode, Symlink):
                return Stat.for_symlink(inode.mode, len(inode.contents))
            elif isinstance(inode, File):
                return Stat.for_file(inode.mode, len(inode.contents))
            elif isinstance(inode, Dir):
                return Stat.for_dir(inode.mode)
            else:
                raise Exception("Unexpected inode type: %s" % type(inode))
        except NoSuchFileOrDirectory:
            return -errno.ENOENT

    def _file_has_to_exist(self, path):
        self._check_for_path_error(path)
        if path != '/':
            head, tail = split(path)
            if tail not in self.swift.get(head).children.names():
                raise PathException(-errno.ENOENT)

    def _check_for_path_error(self, path):
        if not any(path):
            raise PathException(-errno.ENOENT)
        if path[0] != '/':
            raise PathException(-errno.EINVAL)

class PathException(Exception):
    """
    An internal exception raised when a path is incorrect.
    """
    def __init__(self, error):
        self.error = error
