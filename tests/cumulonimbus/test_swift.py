import unittest
from unittest import TestCase

import sys, os
sys.path.insert(0, os.path.join('..','..'))

from cumulonimbus.cloud import File, Dir, Swift

conn_opts = { 'authurl' : 'http://127.0.0.1:8080/auth/v1.0' , 'user' : 'test:tester' , 'key' : 'testing' }

class TestFile(TestCase):

    def setUp(self):
        self.data = "\n".join(map(str, range(1000)))
        self.file = File(0644, contents=self.data)

    def test_empty_file(self):
        self.assertEqual(File(0644).contents(), '')

    def test_having_contents(self):
        self.assertEqual(self.file.contents(), self.data)

    def test_not_having_ctime_before_being_saved(self):
        self.assertIsNone(self.file.ctime)

    def test_size(self):
        self.assertEqual(self.file.size, len(self.data))

class TestDir(TestCase):

    def setUp(self):
        self.dir = Dir(0755)

	def test_no_children_before_being_saved(self):
#        self.assertFalse(any(self.dir.children()))
		self.assertIsNone(self.dir.children())

    def test_no_parent_before_being_saved(self):
        self.assertIsNone(self.dir.parent())

class TestEmptySwift(TestCase):

    def setUp(self):
        self.swift = Swift(**conn_opts)

#    def test_put_file_in_root(self):
#        data = "contents"
#        path = "/test_put_file_in_root"
#        self.assertIsNone(self.swift.put(path, File(0644, data)))
#        self.assertEqual(self.swift.get(path).contents(), data)

#    def test_put_empty_file_in_not_existing_dir(self):
#        with self.assertRaises(NoSuchDirectory):
#            self.swift.put("/doesnt_exist/file", File(0644, 'foo'))

    def test_empty_root(self):
        root = self.swift.get("/")
#        self.assertIs(root, Dir) # orly?
        self.assertIsNone(root.children())

#    def test_make_directory(self):
#        self.assertIsNone(self.swift.mkdir("/test_make_directory"))
#        self.assertIs(self.swift.get("/").children()["test_make_directory"], Dir)

#    def test_put_file_in_subdirectory(self):
#        dir = "/test_put_file_in_subdirectory"
#        data = "foobar"
#        self.swift.mkdir(dir)
#        self.assertIsNone(self.swift.put(dir + "/file", File(0644, data)))
#        self.assertEqual(self.swift.get(dir + "/file").contents(), data)

#    def test_new_directory_name_in_children_names(self):
#        self.assertIsNone(self.swift.mkdir("/another_directory"))
#        self.assertIn("another_directory", self.swift.get("/").children_names())

class TestDirs(TestCase) :
	def setUp( self ) :
		self.swift = Swift(**conn_opts)
		self.swift.mkdir("/")
		self.swift.mkdir("/dir1")

	def test_connection( self ) :
		try:
			self.swift.con.get_auth()
		except :
#        except SwiftConnection as e : 
			self.assertTrue(False,"Connection fail")

	def tearDown( self ) :
		self.swift.rm("/",recursive=True)
		self.swift.rm("/dir1",recursive=True)

if __name__ == "__main__":
    unittest.main()

