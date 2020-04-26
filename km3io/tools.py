#!/usr/bin/env python3
import numba as nb
import numpy as np
import uproot

# 110 MB based on the size of the largest basket found so far in km3net
BASKET_CACHE_SIZE = 110 * 1024**2
BASKET_CACHE = uproot.cache.ThreadSafeArrayCache(BASKET_CACHE_SIZE)


class cached_property:
    """A simple cache decorator for properties."""
    def __init__(self, function):
        self.function = function

    def __get__(self, obj, cls):
        if obj is None:
            return self
        prop = obj.__dict__[self.function.__name__] = self.function(obj)
        return prop


def unfold_indices(obj, indices):
    """Unfolds an index chain and returns the corresponding item"""
    original_obj = obj
    for depth, idx in enumerate(indices):
        try:
            obj = obj[idx]
        except IndexError:
            print(
                "IndexError while accessing an item from '{}' at depth {} ({}) "
                "using the index chain {}".format(repr(original_obj), depth,
                                                  idx, indices))
            raise
    return obj


def to_num(value):
    """Convert a value to a numerical one if possible"""
    for converter in (int, float):
        try:
            return converter(value)
        except (ValueError, TypeError):
            pass
    return value


@nb.jit(nopython=True)
def unique(array, dtype=np.int64):
    """Return the unique elements of an array with a given dtype.

    The performance is better for pre-sorted input arrays.

    """
    n = len(array)
    out = np.empty(n, dtype)
    last = array[0]
    entry_idx = 0
    out[entry_idx] = last
    for i in range(1, n):
        current = array[i]
        if current == last: # shortcut for sorted arrays
            continue
        already_present = False
        for j in range(entry_idx + 1):
            if current == out[j]:
                already_present = True
                break
        if not already_present:
            entry_idx += 1
            out[entry_idx] = current
        last = current
    return out[:entry_idx+1]


@nb.jit(nopython=True)
def uniquecount(array, dtype=np.int64):
    """Count the number of unique elements in a jagged Awkward1 array."""
    n = len(array)
    out = np.empty(n, dtype)
    for i in range(n):
        sub_array = array[i]
        if len(sub_array) == 0:
            out[i] = 0
        else:
            out[i] = len(unique(sub_array))
    return out
