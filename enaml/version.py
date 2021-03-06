#------------------------------------------------------------------------------
#  Copyright (c) 2012, Enthought, Inc.
#  All rights reserved.
#------------------------------------------------------------------------------
""" The version information for this release of Enaml.

"""
from collections import namedtuple

# The major release number. Differences in the major number indicate
# possibly large differences in API.
MAJOR = 0

# The minor release number. Differences in the minor number indicate
# possibly small differences in the API, but these changes will come
# backwards compatibility support when possible. Minor releases are
# typically used for large feature additions.
MINOR = 5

# The micro release number. The micro release number is incremented
# for bug fix releases and small feature additions.
MICRO = 1

# The version info for the current release.
version_info = namedtuple('version_info', 'major minor micro')
version_info = version_info(MAJOR, MINOR, MICRO)

# Remove everything but the 'version_info' from this module.
del namedtuple, MAJOR, MINOR, MICRO

