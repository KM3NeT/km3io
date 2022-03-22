from pkg_resources import get_distribution, DistributionNotFound

version = get_distribution(__name__).version

import warnings

with warnings.catch_warnings():
    for warning_category in (FutureWarning, DeprecationWarning):
        warnings.simplefilter("ignore", category=warning_category)
    import uproot3

from .offline import OfflineReader
from .online import OnlineReader
from .acoustics import RawAcousticReader
from .gseagen import GSGReader
