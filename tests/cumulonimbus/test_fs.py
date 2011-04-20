import errno
from unittest import TestCase
from mock import Mock
from cumulonimbus.fs import FS

class TestFS(TestCase):

    def setUp(self):
        self.mock_swift = self.prepare_mock_swift()
        self.fs = FS(self.mock_swift)

    def prepare_mock_swift(self):
        dir = Mock()
        dir.contents = Mock()
        dir.contents.return_value = {}
        mock = Mock()
        mock.get = Mock()
        mock.get.return_value = dir
        return mock

class EmptyFS(TestFS):

    def test_opening_root_dir(self):
        self.assertIsNone(self.fs.opendir('/'))
        self.assertFalse(self.mock_swift.get.called)

    def test_opening_dir_with_incorrect_path(self):
        self.assertEquals(self.fs.opendir('dir'), -errno.EINVAL)
        self.assertFalse(self.mock_swift.get.called)

    def test_opening_empty_string_directory(self):
        self.assertEquals(self.fs.opendir(''), -errno.ENOENT)
        self.assertFalse(self.mock_swift.get.called)

    def test_opening_nonexistent_dir(self):
        self.assertEquals(self.fs.opendir('/no_such_directory'), -errno.ENOENT)
        self.assertTrue(self.mock_swift.get.called)

class SmallFS(TestFS):

    def prepare_mock_swift(self):
        swift = super(SmallFS, self).prepare_mock_swift()
        swift.get.return_value.contents.return_value = {'dir1': object()}
        return swift

    def test_opening_dir(self):
        self.assertIsNone(self.fs.opendir('/dir1'))
        self.assertTrue(self.mock_swift.get.called)

    def test_opening_nonexistent_dir(self):
        self.assertEquals(self.fs.opendir('/no_such_directory'), -errno.ENOENT)
        self.assertTrue(self.mock_swift.get.called)
