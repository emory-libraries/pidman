# Project Version and Author Information
__author__ = "EUL Systems"
__copyright__ = "Copyright 2010, Emory University General Library"
__credits__ = ["Rebecca Koeser", "Ben Ranker", "Alex Thomas", "Scott Turnbull"]
__email__ = "libsys-dev@listserv.cc.emory.edu"

# Version Info, parsed below for actual version number.
__version_info__ = (0, 9, 0)

# Dot-connect all but the last. Last is dash-connected if not None.
__version__ = '.'.join([ str(i) for i in __version_info__[:-1] ])
if __version_info__[-1] is not None: # Adds dash
    __version__ += ('-%s' % (__version_info__[-1],))