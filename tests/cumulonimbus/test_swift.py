#!/usr/bin/python
# vim: set fileencoding=utf-8 :

import unittest
from unittest import TestCase

from cumulonimbus.cloud import Swift , NoSuchFileOrDirectory 
from cumulonimbus.dir import Dir
from cumulonimbus.file import File

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
		self.assertFalse(any(self.dir.children()))

	def test_no_parent_before_being_saved(self):
		self.assertIsNone(self.dir.parent())

class TestEmptySwift(TestCase):

	def setUp(self):
		self.swift = Swift(**conn_opts)

	def test_put_file_in_root(self):
		data = "contents"
		path = "/test_put_file_in_root"
		self.assertIsNone(self.swift.put(path, File(0644, data)))
		self.assertEqual(self.swift.get(path).contents(), data)

	def test_put_empty_file_in_not_existing_dir(self):
		with self.assertRaises(NoSuchFileOrDirectory):
			self.swift.put("/doesnt_exist/file", File(0644, 'foo'))

	def test_empty_root(self):
		root = self.swift.get("/")
#        self.assertIs(root, Dir()) # orly?
		self.assertFalse(any(root.children()))

	def test_make_directory(self):
		self.assertIsNone(self.swift.mkdir("/test_make_directory"))
		self.assertIsNotNone(self.swift.get("/").children()["test_make_directory"])

	def test_put_file_in_subdirectory(self):
		dir = "/test_put_file_in_subdirectory"
		data = "foobar"
		self.swift.mkdir(dir)
		self.assertIsNone(self.swift.put(dir + "/file", File(0644, data)))
		self.assertEqual(self.swift.get(dir + "/file").contents(), data)

	def test_new_directory_name_in_children_names(self):
		self.assertIsNone(self.swift.mkdir("/another_directory"))
		self.assertIn("another_directory", self.swift.get("/").children_names())

	def tearDown( self ) :
		self.swift.rm("/",recursive=True)

class TestSwiftDirs(TestCase) :
	def setUp( self ) :
		self.swift = Swift(**conn_opts)
		self.swift.mkdir("/")
		self.swift.mkdir("/dir1")

	def test_dir_rm( self ) :
		self.swift.rm("/dir1",recursive=True)
		self.swift.mkdir("/dir1/")
		self.swift.rm("/dir1/",recursive=True)

	def test_dir_rm_recursive( self ) :
		self.swift.mkdir("/dir2")
		self.swift.mkdir("/dir2/dir3")
		self.swift.mkdir("/dir2/dir4")
		self.swift.rm( '/dir2' , recursive=True )

		with self.assertRaises(NoSuchFileOrDirectory) as cm :
			self.swift.get("/dir2/")
		self.assertEqual(str(cm.exception),'/dir2') 
		# note missing '/'. Swift api removes last '/'

	def test_dir_rm_fail( self ) :
		with self.assertRaises(NoSuchFileOrDirectory) as cm :
			self.swift.get('/dir2/dir3')
		self.assertEqual(str(cm.exception),'/dir2/dir3')

	def test_dir_mk( self ) :
		self.swift.mkdir("/dir2")
		self.swift.mkdir("/dir2/dir3/")
		self.assertIsNotNone( self.swift.get("/dir2") )
		self.assertIsNotNone( self.swift.get("/dir2/dir3") )

	def test_dir_mk_parents( self ) :
		self.swift.mkdir("/dir3/dir4/dir5",parents=True)
		self.assertIsNotNone( self.swift.get("/dir3") )
		self.assertIsNotNone( self.swift.get("/dir3/dir4") )
		self.assertIsNotNone( self.swift.get("/dir3/dir4/dir5") )

	def test_dir_mk_fail( self ) :
		with self.assertRaises(NoSuchFileOrDirectory) as cm :
			self.swift.mkdir("/dir4/dir5/dir6")
		self.assertEqual(str(cm.exception),'/dir4/dir5')

	def test_dir_children( self ) :
		self.assertIn('dir1',self.swift.get('/').children_names())
		self.swift.mkdir('/dir1/dir2/')
		self.assertIn('dir2',self.swift.get('/dir1').children_names())

	def test_dir_children_tree( self ) :
		self.swift.mkdir('/a/b/c/d',parents=True)
		self.swift.mkdir('/a/b/e')
		self.swift.mkdir('/a/b/f')
		self.swift.mkdir('/a/g/')
		dir = self.swift.get('/')
		self.assertIn('a',dir.children_names())
		self.assertIn('dir1',dir.children_names())
		dir = dir.children()['dir1']
		self.assertFalse(any(dir.children_names()))
		dir = dir.parent().children()['a']
		self.assertEqual(['b','g'],dir.children_names())
		dir = dir.children()['g']
		self.assertSequenceEqual([],dir.children_names())
		dir = dir.parent().children()['b']
		self.assertSequenceEqual(['c','e','f'],dir.children_names())
		self.assertSequenceEqual(['d'],dir.children()['c'].children_names())

	def test_dir_parent( self ) :
		# FIXME: how test dir equality?
		self.assertEqual(
				self.swift.get('/').children_names() ,
				self.swift.get('/dir1/').parent().children_names() )

	def tearDown( self ) :
		self.swift.rm("/",recursive=True)

class TestSwiftObjects(TestCase) :
	def setUp( self ) :
		self.data = 'zażółć gęślą jaźń\n'*1000
		self.file = File(0600,self.data)
		self.swift = Swift(**conn_opts)
		self.swift.mkdir("/")

	def test_put_get( self ) :
		self.swift.put( '/file' , self.file )
		self.assertEqual(
				self.swift.get( '/file' ).contents() , self.data )

	def test_put_fail( self ) :
		with self.assertRaises(NoSuchFileOrDirectory) as cm :
			self.swift.put( '/dir/file' , self.file ) 
		self.assertEqual(str(cm.exception),'/dir')

		with self.assertRaises(ValueError) as cm :
			self.swift.put( '/file/' , self.file ) 

	def test_put_rm( self ) :
		self.swift.put('/file' , self.file )
		self.swift.rm('/file')

		with self.assertRaises(NoSuchFileOrDirectory) as cm :
			self.swift.get('/file')
		self.assertEqual(str(cm.exception),'/file')

	def test_file_ctime( self ) :
		self.swift.put('/file' , self.file )
		self.file.touch()
		self.assertLessEqual(self.swift.get('/file').ctime,self.file.ctime)

	def tearDown( self ) :
		self.swift.rm("/",recursive=True,force=True)

if __name__ == "__main__":
	unittest.main()

