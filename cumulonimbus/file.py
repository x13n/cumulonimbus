
class File : 
	def __init__( self , mode , contents=None ) :
		self.mode = mode
		self.ctime = None

		if contents == None :
			self.con = ''
		else : # FIXME: binary and text files?
			self.con = contents

		self.size = len(self.con)

	def contents( self ) :
		return self.con

