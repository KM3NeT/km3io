try:
    from importlib.metadata import version as get_version

    version = get_version(__name__)
except ImportError:
    from pkg_resources import get_distribution

    version = get_distribution(__name__).version


import warnings
import os

# Getting rid of OpenMP warnings, related to Numba
# See: https://github.com/numba/numba/issues/5275
# This needs to be done before import numpy
os.environ["KMP_WARNINGS"] = "off"

from .offline import OfflineReader
from .acoustics import RawAcousticReader
