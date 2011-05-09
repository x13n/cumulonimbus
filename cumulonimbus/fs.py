import errno
from os.path import split

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
        yield "."
        yield ".."
        for name in self.swift.get(path).children_names():
            yield name

    def create(self, path, mode, rdev):
        """
        Creates a new file with a given mode and returns None.
        """
        pass

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

    def _file_has_to_exist(self, path):
        self._check_for_path_error(path)
        if path != '/':
            head, tail = split(path)
            if tail not in self.swift.get(head).children_names():
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
