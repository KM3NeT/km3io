import warnings
import os

# Getting rid of OpenMP warnings, related to Numba
# See: https://github.com/numba/numba/issues/5275
# This needs to be done before import numpy
os.environ["KMP_WARNINGS"] = "off"

from .version import *
from .offline import OfflineReader
from .acoustics import RawAcousticReader
