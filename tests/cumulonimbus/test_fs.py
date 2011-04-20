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
        dir.contents.returned_value = {}
        mock = Mock()
        mock.get = Mock()
        mock.get.returned_value = dir
        return mock

    def test_opening_root_dir(self):
        self.assertIsNone(self.fs.opendir('/'))
        self.assertTrue(self.mock_swift.get.called)

    def test_opening_dir_with_incorrect_path(self):
        self.assertEquals(self.fs.opendir('dir'), -errno.EINVAL)
        self.assertFalse(self.mock_swift.get.called)

    def test_opening_empty_string_directory(self):
        self.assertEquals(self.fs.opendir(''), -errno.ENOENT)
        self.assertFalse(self.mock_swift.get.called)

    def test_opening_nonexistent_dir(self):
        self.assertEquals(self.fs.opendir('/no_such_directory'), -errno.ENOENT)
        self.assertTrue(self.mock_swift.get.called)
