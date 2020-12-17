from pkg_resources import get_distribution, DistributionNotFound

version = get_distribution(__name__).version

import warnings

warnings.simplefilter(action="ignore", category=FutureWarning)  # uproot3

from .offline import OfflineReader
from .online import OnlineReader
from .gseagen import GSGReader
