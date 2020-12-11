from pkg_resources import get_distribution, DistributionNotFound

version = get_distribution(__name__).version

from .offline import OfflineReader
from .online import OnlineReader
from .gseagen import GSGReader
