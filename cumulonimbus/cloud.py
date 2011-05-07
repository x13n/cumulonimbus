
import os.path

import swift.common.client as scc

import dir
import file

class NoSuchFileOrDirectory( Exception ) : pass
# in default swift doesnt alarm if container exists do we need this?
#class DirectoryExists( Exception ) : pass

def sw2fs( path ) :
	return str.replace(path,'\\','/')

def fs2sw( path ) :
	return str.replace(path,'/','\\')

class Dir( dir.Dir ) :
	def __init__( self , connection , mode ) :
		dir.Dir.__init__( self , mode ) 

		self.con = connection

	def children( self ) :
		return None

class File( file.File ) :
	pass

class Swift :
	con = None

	def __init__( self , authurl , user , key ) :
		''' Connect to swift server and create root directory '''
		self.con = scc.Connection( authurl , user , key )
#        try :
		self.mkdir('/')
#        except DirectoryExists :
#            pass

#        self.dirs = {}
#        for p in self.con.get_account()[1] :
#            self.dirs[p['name']] = Dir( self.con , 0644 )

	def _flush( self ) :
		''' force send all data to swift server '''
		pass

	def sync( self ) :
		''' synchronize with swift server '''
		pass

	def get( self , path ) :
		''' recive file or dir given by path '''
		assert( self.con != None ) 

		cont , obj = os.path.split(path)

		try :
			self.con.get_container(fs2sw(path))
			# TODO: create children list
			return Dir( self.con , 0600 )
		except scc.ClientException as e :
			if e.http_status != 404 : raise e
			cont , obj = os.path.split(path)
			if obj == '' : raise NoSuchFileOrDirectory(path)

			try :
				obj = self.con.get_object(fs2sw(cont),obj)
			except scc.ClientException as e :
				if e.http_status == 404 :
					raise NoSuchFileOrDirectory(path)
				else : raise e
			return File(0600,obj[1])

	def put( self , path , file ) :
		'''
		send file at given path 

		can rise error if path is invalid
		'''
		assert( self.con != None )

		cont , obj = os.path.split(path)

		if obj == '' :
			raise ValueError('cannot put file with empty name')

		self.get(cont)

		self.con.put_object(fs2sw(cont),obj,file.contents())

	def mkdir( self , path  , parents = False ) :
		'''
		creates new directory on swift server

		can rise error if path is invalid

		if parents is true, parents are created
		if they dont exists
		'''
		assert( self.con != None )

		swpath = fs2sw(path)

		if path == '/' : # FIXME: is this portable?
			self.con.put_container(swpath)
			return

		path = os.path.normpath(path)

		if not parents :
			parent , obj = os.path.split(path)
			swpar = fs2sw(parent)
			for p in self.con.get_account()[1] :
				if p['name'] == swpar :
					self.con.put_container(fs2sw(path))
					return
			raise NoSuchFileOrDirectory(parent)
		else :
			directory = path
			while directory != '/' : # FIXME: is this portable?
				self.con.put_container(fs2sw(directory))
				directory = os.path.split(directory)[0]

	def rm( self , path , recursive = False , force = False ) :
		''' removes file or directory '''
		assert( self.con != None )

		path = os.path.normpath(path)

		if recursive : 
			try :
				self._rm_dir( path )
			except scc.ClientException as e :
				if e.http_status != 404 : raise e
				self._rm_file( path )
		else :
			self._rm_file( path )

	def _rm_dir( self , path ) :
		swpath = fs2sw(path)

		# check if path is a dir
		self.con.get_container( swpath )

		# delete subdirectries
		for p in self.con.get_account()[1] :
			name = p['name']
			if name[:len(swpath)] == swpath : # p is substring
				for p in self.con.get_container(name)[1] :
					self.con.delete_object(name,p['name'])
				self.con.delete_container(name)

	def _rm_file( self , path ) :
		cont , obj = os.path.split(path)
		if obj == '' : raise NoSuchFileOrDirectory(path)

		try :
			self.con.delete_object(fs2sw(cont),obj)
		except scc.ClientException as e :
			if e.http_status == 404 :
				raise NoSuchFileOrDirectory(path)
			else : raise e

