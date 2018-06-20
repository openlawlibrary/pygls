# Copyright 2017 Palantir Technologies, Inc.
import os
from future.standard_library import install_aliases
from ._version import get_versions

install_aliases()
__version__ = get_versions()['version']
del get_versions

pygls = 'pygls'

IS_WIN = os.name == 'nt'
