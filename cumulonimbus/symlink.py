
import file

class Symlink( file.File ):
    def __init__( self, mode, target, ctime=None ):
        file.File.__init__( self, mode, target, ctime )

