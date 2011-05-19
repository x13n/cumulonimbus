
class Offspring( dict ) :
	def names( self ) :
		return self.keys()

	def objects( self ) :
		return self.values()

class Dir : 
	def __init__( self , mode ) :
		self.mode  = mode
		self.daddy = None
		self.offspring = Offspring()

	@property
	def children( self ) :
		return self.offspring

	def parent( self ) :
		return self.daddy

	def set_parent( self , dir ) :
		self.daddy = dir

	def set_child( self , name , child ) :
		if dir == None :
			del self.offspring[name]
		else :
			self.offspring[name] = child

