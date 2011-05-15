
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

	def mode(self) :
		return self._mode

	@property
	def ctime( self ) :
		return self._ctime

	def touch( self ) :
		self._ctime = time.time()

	def contents( self ) :
		return self._data

