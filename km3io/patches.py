import awkward0 as ak0
import awkward as ak1

# to avoid infinite recursion
old_getitem = ak0.ChunkedArray.__getitem__


def new_getitem(self, item):
    """Monkey patch the getitem in awkward.ChunkedArray to apply
    awkward1.Array masks on awkward.ChunkedArray"""
    if isinstance(item, (ak1.Array, ak0.ChunkedArray)):
        return ak1.Array(self)[item]
    else:
        return old_getitem(self, item)


ak0.ChunkedArray.__getitem__ = new_getitem
