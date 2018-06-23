# Copyright 2017 Palantir Technologies, Inc.
import os
from ._version import get_versions

__version__ = get_versions()['version']
del get_versions

pygls = 'pygls'

IS_WIN = os.name == 'nt'
