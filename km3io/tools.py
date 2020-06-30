#!/usr/bin/env python3
import numba as nb
import numpy as np
import awkward1 as ak1
import uproot

from .definitions import fitparameters, reconstruction, w2list_genhen, w2list_gseagen

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
        if current == last:  # shortcut for sorted arrays
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
    return out[:entry_idx + 1]


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


def w2list_genhen_keys():
    """names of the w2list parameters as defined in the official
    KM3NeT-Dataformat for genhen.

    Returns
    -------
    dict_keys
        genhen w2list keys.
    """
    return w2list_genhen.keys()


def w2list_gseagen_keys():
    """names of the w2list parameters as defined in the official
    KM3NeT-Dataformat for gseagen.

    Returns
    -------
    dict_keys
        gseagen w2list keys.
    """
    return w2list_gseagen.keys()


def get_w2list_param(events, generator, param):
    """get all the values of a specific parameter from the w2list
    in offline neutrino files.

    Parameters
    ----------
    events : class km3io.offline.OfflineBranch
        events class in offline neutrino files.
    generator : str
        the name of the software generating neutrinos, it is either
        'genhen' or 'gseagen'. 
    param : str
        the name of the parameters found in w2list as defined in the
        KM3NeT-Dataformat for both genhen and gseagen.

    Returns
    -------
    awkward array
        array of the values of interest.
    """
    if generator == "gseagen":
        return events.w2list[:, w2list_gseagen[param]]
    if generator == "genhen":
        return events.w2list[:, w2list_genhen[param]]


def rec_types():
    """name of the reconstruction type as defined in the official
    KM3NeT-Dataformat.

    Returns
    -------
    dict_keys
        reconstruction types.
    """
    return reconstruction.keys()


def fitinf(fitparam, tracks):
    """Access fit parameters in tracks.fitinf.

    Parameters
    ----------
    fitparam : str
        the fit parameter name according to fitparameters defined in
        KM3NeT-Dataformat.
    tracks : class km3io.offline.OfflineBranch
        the tracks class. both full tracks branch or a slice of the
        tracks branch (example tracks[:, 0]) work.

    Returns
    -------
    awkward array
        awkward array of the values of the fit parameter requested.
    """
    fit = tracks.fitinf
    index = fitparameters[fitparam]
    try:
        params = fit[count_nested(fit, axis=2) > index]
        return ak1.Array([i[:, index] for i in params])
    except ValueError:
        # This is the case for tracks[:, 0] or any other selection.
        params = fit[count_nested(fit, axis=1) > index]
        return params[:, index]


def fitparams():
    """name of the fit parameters as defined in the official
    KM3NeT-Dataformat.

    Returns
    -------
    dict_keys
        fit parameters keys.
    """
    return fitparameters.keys()


def count_nested(Array, axis=0):
    """count elements in a nested awkward Array.

    Parameters
    ----------
    Array : Awkward1 Array
        Array of data. Example tracks.fitinf or tracks.rec_stages.
    axis : int, optional
        axis = 0: to count elements in the outmost level of nesting.
        axis = 1: to count elements in the first level of nesting.
        axis = 2: to count elements in the second level of nesting.

    Returns
    -------
    awkward1 Array or int
        counts of elements found in a nested awkward1 Array.
    """
    if axis == 0:
        return ak1.num(Array, axis=0)
    if axis == 1:
        return ak1.num(Array, axis=1)
    if axis == 2:
        return ak1.count(Array, axis=2)


@nb.jit(nopython=True)
def _find(rec_stages, stages, builder):
    """construct an awkward1 array with the same structure as tracks.rec_stages.
    When stages are found, the Array is filled with value 1, otherwise it is filled
    with value 0.

    Parameters
    ----------
    rec_stages : awkward1 Array
        tracks.rec_stages .
    stages : awkward1 Array
        reconstruction stages of interest.
    builder : awkward1.highlevel.ArrayBuilder
        awkward1 Array builder.
    """
    for s in rec_stages:
        builder.begin_list()
        for i in s:
            num_stages = len(i)
            if num_stages == len(stages):
                found = 0
                for j in range(num_stages):
                    if i[j] == stages[j]:
                        found += 1
                if found == num_stages:
                    builder.append(1)
                else:
                    builder.append(0)
            else:
                builder.append(0)
        builder.end_list()


def mask(rec_stages, stages):
    """create a mask on tracks.rec_stages .

    Parameters
    ----------
    rec_stages : awkward1 Array
        tracks.rec_stages .
    stages : list
        reconstruction stages of interest.

    Returns
    -------
    awkward1 Array
        an awkward1 Array mask where True corresponds to the positions
        where stages were found. False otherwise.
    """
    builder = ak1.ArrayBuilder()
    _find(rec_stages, ak1.Array(stages), builder)
    return builder.snapshot() == 1


def best_track(tracks, strategy="default", rec_type=None):
    """best track selection based on different strategies

    Parameters
    ----------
    tracks : class km3io.offline.OfflineBranch
        a subset of reconstructed tracks where `events.n_tracks > 0` is always true. 
    strategy : str
        the trategy desired to select the best tracks. It is either: 
            - "first" : to select the first tracks.
            - "default": to select the best tracks (the first ones) corresponding to a specific
            reconstruction algorithm (JGandalf, Jshowerfit, etc). This requires rec_type input.
            Example: best_track(my_tracks, strategy="default", rec_type="JPP_RECONSTRUCTION_TYPE").
    rec_type : str, optional
        reconstruction type as defined in the official KM3NeT-Dataformat.

    Returns
    -------
    class km3io.offline.OfflineBranch
        tracks class with the desired "best tracks" selection.

    Raises
    ------
    ValueError
        ValueError raised when:
            - an invalid strategy is requested.
            - a subset of events with empty tracks is used.
    """
    options = ['first', 'default']
    if strategy not in options:
        raise ValueError("{} not in {}".format(strategy, options))

    n_events = len(tracks)
    if n_events > 1 and any(count_nested(tracks.lik, axis=1) == 0):
        raise ValueError(
            "'events' should not contain empty tracks. Consider applying the mask: events.n_tracks>0"
        )

    if strategy == "first":
        if n_events == 1:
            out = tracks[0]
        else:
            out = tracks[:, 0]

    elif strategy == "default" and rec_type is not None:
        if n_events == 1:
            out = tracks[tracks.rec_type == reconstruction[rec_type]][
                tracks.lik == ak1.max(tracks.lik, axis=0)][0]
        else:
            out = tracks[tracks.rec_type == reconstruction[rec_type]][
                tracks.lik == ak1.max(tracks.lik, axis=1)][:, 0]

    return out


def get_multiplicity(tracks, rec_stages):
    """tracks selection based on specific reconstruction stages (for multiplicity
    calculations).

    Parameters
    ----------
    tracks : class km3io.offline.OfflineBranch
        tracks or a subste of tracks. 
    rec_stages : list
        the reconstruction stages of interest. Examle: [1, 2, 3, 4, 5].

    Returns
    -------
    class km3io.offline.OfflineBranch
        tracks branch with the desired reconstruction stages only.
    """
    return tracks[mask(tracks.rec_stages, rec_stages)]
