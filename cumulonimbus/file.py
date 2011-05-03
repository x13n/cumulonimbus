
class File : 
	def __init__( self , mod , contents=None ) :
		self.mod = mod
		self.ctime = None

		if contents == None :
			self.con = ''
		else : # FIXME: binary and text files?
			self.con = contents

		self.size = len(self.con)

	def contents( self ) :
		return self.con

