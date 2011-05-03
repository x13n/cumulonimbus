
import swift.common.client as scc

import dir
import file

class Dir( dir.Dir ) :
	pass

class File( file.File ) :
	pass

class Swift :
	con = None

	def __init__( self , authurl , user , key ) :
		self.con = scc.Connection( authurl , user , key )
		print self.con.get_account()[1]

	def _flush( self ) :
		''' force send all data to swift server '''
		pass

	def sync( self ) :
		''' synchronize with swift server '''
		pass

	def get( self , path ) :
		''' recive file or dir given by path '''
		assert( self.con != None ) 
		return Dir(0600,path)

	def put( self , path , file ) :
		'''
		send file at given path 

		can rise error if path is invalid
		'''
		assert( self.con != None )

	def mkdir( self , path  , parents = False ) :
		'''
		creates new directory on swift server

		can rise error if path is invalid

		if parents is true, parents are created
		if they dont exists
		'''
		assert( self.con != None )

		self.con.put_container(path)

	def rm( self , path , recursive = False ) :
		''' removes file or directory '''
		assert( self.con != None )

		self.con.delete_container(path)

