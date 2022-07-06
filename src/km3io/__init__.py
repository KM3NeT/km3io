from pkg_resources import get_distribution, DistributionNotFound

version = get_distribution(__name__).version

import warnings
import os

# Getting rid of OpenMP warnings, related to Numba
# See: https://github.com/numba/numba/issues/5275
# This needs to be done before import numpy
os.environ["KMP_WARNINGS"] = "off"

with warnings.catch_warnings():
    for warning_category in (FutureWarning, DeprecationWarning):
        warnings.simplefilter("ignore", category=warning_category)
    import uproot3

from .offline import OfflineReader
from .online import OnlineReader
from .acoustics import RawAcousticReader
from .gseagen import GSGReader
