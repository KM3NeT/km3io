import numpy as np
import awkward as ak
import awkward1 as ak1

from pkg_resources import get_distribution, DistributionNotFound

version = get_distribution(__name__).version

from .offline import OfflineReader
from .online import OnlineReader
from .gseagen import GSGReader

# to avoid infinite recursion
old_getitem = ak.ChunkedArray.__getitem__


def new_getitem(self, item):
    """Monkey patch the getitem in awkward.ChunkedArray to apply
        awkward1.Array masks on awkward.ChunkedArray"""
    if isinstance(item, (ak1.Array, ak.ChunkedArray)):
        return ak1.Array(self)[item]
    else:
        return old_getitem(self, item)


ak.ChunkedArray.__getitem__ = new_getitem
