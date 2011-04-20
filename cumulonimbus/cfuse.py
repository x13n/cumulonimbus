#!/usr/bin/env python

import fuse

# Logging actions
import logging

LOG_FILENAME = "LOG"
logging.basicConfig(filename=LOG_FILENAME,level=logging.INFO,)
# /Logging actions

# FUSE version at the time of writing. Be compatible with this version.
fuse.fuse_python_api = (0, 2)

class Stat( fuse.Stat ):
    pass

class CFuse( fuse.Fuse ):
    pass
