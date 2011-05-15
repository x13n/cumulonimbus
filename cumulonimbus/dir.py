
class Dir : 
	def __init__( self , mode ) :
		self.mode  = mode
		self.daddy = None
		self.offspring = {}

	def children( self ) :
		return self.offspring

	def children_names( self ) :
		return self.offspring.keys()

	def parent( self ) :
		return self.daddy

	def set_parent( self , dir ) :
		self.daddy = dir

	def set_child( self , name , dir ) :
		if dir == None :
			del self.offspring[name]
		else :
			self.offspring[name] = dir

