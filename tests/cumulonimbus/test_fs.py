import errno
import os
from unittest import TestCase
from mock import Mock
from cumulonimbus.fs import FS
from cumulonimbus.file import File

class TestFS(TestCase):

    def setUp(self):
        self.mock_swift = self.prepare_mock_swift()
        self.fs = FS(self.mock_swift)

    def prepare_mock_swift(self):
        mock = Mock()
        mock.get.return_value.children.names.return_value = []
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

    def test_creating_file(self):
        self.assertIsNone(self.fs.create('/file', 0321, 0))
        args = self.mock_swift.put.call_args
        self.assertEquals(args[1], {})
        self.assertEquals(len(args[0]), 2)
        self.assertEquals(args[0][1].mode, 0321)
        self.assertEquals(args[0][1].contents, '')

    def test_creating_directory(self):
        self.assertIsNone(self.fs.mkdir('/new_dir', 0321))
        args = self.mock_swift.mkdir.call_args
        self.assertEquals(args[1], {})
        self.assertEquals(len(args[0]), 1)
        self.assertEquals(args[0][0], '/new_dir')
        # TODO: check mode

    def test_creating_invalid_dir(self):
        self.assertEquals(self.fs.mkdir('asdf', 0755), -errno.ENOENT)
        self.assertFalse(self.mock_swift.mkdir.called)

class SmallFS(TestFS):

    def prepare_mock_swift(self):
        """
        We're mocking a following directory structure:

          /
            dir1
            dir2
              dir3

        """
        swift = super(SmallFS, self).prepare_mock_swift()

        fs = {
                '/':            ['dir1', 'dir2'],
                '/dir1' :       [],
                '/dir2' :       ['dir3'],
                '/dir2/dir3' :  [],
                }

        def get_side_effect(path):
            m = Mock()
            m.children.names.return_value = fs[path]
            m.contents = None
            return m

        def mkdir_side_effect(path):
            pairs = []
            head = path
            while True:
                head, tail = os.path.split(head)
                pairs = [(head,tail)] + pairs
                if head == '/':
                    break
            for head, tail in pairs:
                if not head in fs:
                    raise Exception("The test wasn't set up correctly.")
                if not tail in fs[head]:
                    fs[head].append(tail)
            fs[path] = []

        swift.get.side_effect = get_side_effect
        swift.mkdir.side_effect = mkdir_side_effect
        return swift

    def test_opening_dir(self):
        self.assertIsNone(self.fs.opendir('/dir1'))
        self.assertTrue(self.mock_swift.get.called)

    def test_opening_nonexistent_dir(self):
        self.assertEquals(self.fs.opendir('/no_such_directory'), -errno.ENOENT)
        self.assertTrue(self.mock_swift.get.called)

    def test_readdir_returns_strings(self):
        self.fs.opendir('/')
        self.mock_swift.get.called = False
        for ent in self.fs.readdir('/', 0, None):
            self.assertTrue(isinstance(ent, str))

    def test_readdir_empty_dir(self):
        self.fs.opendir('/dir1')
        self.mock_swift.get.called = False
        entries = [entry for entry in self.fs.readdir('/dir1', 0, None)]
        entries.sort()
        self.assertEquals(entries, ['.', '..'])
        self.assertTrue(self.mock_swift.get.called)

    def test_readdir_dir(self):
        self.fs.opendir('/dir2')
        self.mock_swift.get.called = False
        entries = [entry for entry in self.fs.readdir('/dir2', 0, None)]
        entries.sort()
        self.assertEquals(entries, ['.', '..', 'dir3'])
        self.assertTrue(self.mock_swift.get.called)

    def test_readdir_root_dir(self):
        self.fs.opendir('/')
        self.mock_swift.get.called = False
        entries = [entry for entry in self.fs.readdir('/', 0, None)]
        entries.sort()
        self.assertEquals(entries, ['.', '..', 'dir1', 'dir2'])
        self.assertTrue(self.mock_swift.get.called)

    def test_accessing_dir(self):
        for dir in ['/dir1', '/dir2', '/dir2/dir3']:
            self.assertEquals(self.fs.access(dir, os.F_OK), 0)

    def test_accessing_nonexistent_dir(self):
        for dir in ['/nothing', '/dir2/no_such_dir']:
            self.assertEquals(self.fs.access(dir, os.F_OK), -errno.ENOENT)

    def test_renaming_dir(self):
        self.fs.rename('/dir2', '/new_directory')
        self.assertTrue(self.mock_swift.get.called)
        self.assertTrue(self.mock_swift.mkdir.called)
