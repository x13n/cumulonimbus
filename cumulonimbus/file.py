
import time

class File : 
	def __init__( self , mode , contents=None , ctime=None ) :
		self._mode  = mode
		self._ctime = ctime    if ctime   !=None else None
		self._data  = contents if contents!=None else ''
		self._size  = len(self._data)

	@property
	def size( self ) :
		return self._size

	@property
	def mode(self) :
		return self._mode

	@property
	def ctime( self ) :
		return self._ctime

	def touch( self ) :
		self._ctime = time.time()

	@property
	def contents( self ) :
		return self._data

	@contents.setter
	def contents( self , data ) :
		self._data = data

	@contents.deleter
	def contents( self ) :
		self._data = ''

