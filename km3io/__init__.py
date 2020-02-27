from pkg_resources import get_distribution, DistributionNotFound

try:
    version = get_distribution(__name__).version
except DistributionNotFound:
    version = "unknown version"

from .offline import OfflineReader
from .daq import DAQReader
