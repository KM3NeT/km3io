#!/usr/bin/env python3
import numba as nb
import numpy as np
import awkward1 as ak1
import uproot

from km3io.definitions import reconstruction as krec
from km3io.definitions import trigger as ktrg
from km3io.definitions import fitparameters as kfit
from km3io.definitions import w2list_genhen as kw2gen
from km3io.definitions import w2list_gseagen as kw2gsg

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
            raise IndexError(
                "IndexError while accessing an item from '{}' at depth {} ({}) "
                "using the index chain {}".format(repr(original_obj), depth,
                                                  idx, indices))
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
    return kw2gen.keys()


def w2list_gseagen_keys():
    """names of the w2list parameters as defined in the official
    KM3NeT-Dataformat for gseagen.

    Returns
    -------
    dict_keys
        gseagen w2list keys.
    """
    return kw2gsg.keys()


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
        return events.w2list[:, kw2gsg[param]]
    if generator == "genhen":
        return events.w2list[:, kw2gen[param]]


def rec_types():
    """name of the reconstruction type as defined in the official
    KM3NeT-Dataformat.

    Returns
    -------
    dict_keys
        reconstruction types.
    """
    return krec.keys()


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
    index = kfit[fitparam]
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
    return kfit.keys()


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
    return tracks[mask(tracks, rec_stages)]


def best_track(tracks, start=None, end=None, stages=None):
    """Best track selection.

    Parameters
    ----------
    tracks : class km3io.offline.OfflineBranch
        tracks of interest. tracks can be from multiple events, or from one event, or a slice of tracks.
    start : None, optional
        the exact starting step of rec_stages, as in tracks.rec_stages.
    end : None, optional
        the exact ending step of rec_stages, as in tracks.rec_stages.
    stages : None, optional
        either a list or a set of stages:
        - if stages is a list, the order of the rec_stages is conserved.
        - if stages in a set, the order is irrelevant.

    Returns
    -------
    class km3io.offline.OfflineBranch
        the best tracks based on the rec_stages selection. The logest track and the highest likelihood track is returned.

    Raises
    ------
    ValueError
        valueError raised when:
            - too many inputs specified.
            - no inputs are specified.
    """
    if (start is None) and (end is None) and (stages is not None):
        selected_tracks = tracks[mask(tracks, stages=stages)]

    if (start is not None) and (end is not None) and (stages is None):
        selected_tracks = tracks[mask(tracks, start=start, end=end)]

    if (start is None) and (end is None) and (stages is None):
        raise ValueError("No reconstruction stages were specified")

    if ((start is not None) or (end is not None)) and (stages is not None):
        raise ValueError("too many inputs are specified")

    return _max_lik_track(_longest_tracks(selected_tracks))


def _longest_tracks(tracks):
    """ select the longest reconstructed track"""
    if tracks.is_single:
        stages_nesting_level = 1
        tracks_nesting_level = 0

    else:
        stages_nesting_level = 2
        tracks_nesting_level = 1

    len_stages = count_nested(tracks.rec_stages, axis=stages_nesting_level)
    longest = tracks[len_stages == ak1.max(len_stages,
                                           axis=tracks_nesting_level)]

    return longest


def _max_lik_track(tracks):
    """ select the track with the highest likelihood """
    if tracks.is_single:
        tracks_nesting_level = 0
    else:
        tracks_nesting_level = 1

    return tracks[tracks.lik == ak1.max(tracks.lik, axis=tracks_nesting_level)]


def mask(tracks, stages=None, start=None, end=None):
    """create a mask for tracks.rec_stages .

    Parameters
    ----------
    tracks : class km3io.offline.OfflineBranch
        tracks, or one track, or slice of tracks, or slice of one track.
    stages : list or set
        reconstruction stages of interest:
        - if stages is a list: the order of rec_stages in conserved.
        - if stages is a set: the order of rec_stages in irrelevant.
    start : None, optional
        the exact starting step of rec_stages, as in tracks.rec_stages.
    end : None, optional
        the exact ending step of rec_stages, as in tracks.rec_stages.

    Returns
    -------
    awkward1 Array
        an awkward1 Array mask where True corresponds to the positions
        where stages were found. False otherwise.

    Raises
    ------
    ValueError
        valueError raised when:
            - too many inputs specified.
            - no inputs are specified.
    """
    if (stages is None) and (start is None) and (end is None):
        raise ValueError("either stages or (start and end) must be specified")

    if (stages is not None) and (start is not None) and (end is not None):
        raise ValueError("too many inputs are specified")

    if (stages is not None) and (start is None) and (end is None):
        if isinstance(stages, list):
            # order of stages is conserved
            return _mask_explicit_rec_stages(tracks, stages)
        if isinstance(stages, set):
            # order of stages is no longer conserved
            mini = min(stages)
            maxi = max(stages)
            return _mask_rec_stages_in_range_min_max(tracks, mini, maxi)

    if (stages is None) and (start is not None) and (end is not None):
        return _mask_rec_stages_between_start_end(tracks, start, end)


def _mask_rec_stages_between_start_end(tracks, start, end):
    """ mask tracks.rec_stages that start exactly with start and end exactly with end. ie [start, a, b ...,z , end] """
    builder = ak1.ArrayBuilder()
    if tracks.is_single:
        _find_between_single(tracks.rec_stages, start, end, builder)
        return (builder.snapshot() == 1)[0]
    else:
        _find_between(tracks.rec_stages, start, end, builder)
        return builder.snapshot() == 1


@nb.jit(nopython=True)
def _find_between(rec_stages, start, end, builder):
    """ find tracks.rec_stages where rec_stages[0] == start and rec_stages[-1] == end."""

    for s in rec_stages:
        builder.begin_list()
        for i in s:
            num_stages = len(i)
            if num_stages != 0:
                if (i[0] == start) and (i[-1] == end):
                    builder.append(1)
                else:
                    builder.append(0)
            else:
                builder.append(0)
        builder.end_list()


@nb.jit(nopython=True)
def _find_between_single(rec_stages, start, end, builder):
    """ find tracks.rec_stages where rec_stages[0] == start and rec_stages[-1] == end in a single track. """

    builder.begin_list()
    for s in rec_stages:
        num_stages = len(s)
        if num_stages != 0:
            if (s[0] == start) and (s[-1] == end):
                builder.append(1)
            else:
                builder.append(0)
        else:
            builder.append(0)
    builder.end_list()


def _mask_explicit_rec_stages(tracks, stages):
    """mask explicit rec_stages .

    Parameters
    ----------
    tracks : class km3io.offline.OfflineBranch
        tracks or one track, or slice of tracks.
    stages : list
        reconstruction stages of interest. The order of stages is conserved.

    Returns
    -------
    awkward1 Array
        an awkward1 Array mask where True corresponds to the positions
        where stages were found. False otherwise.
    """

    builder = ak1.ArrayBuilder()
    if tracks.is_single:
        _find_single(tracks.rec_stages, ak1.Array(stages), builder)
        return (builder.snapshot() == 1)[0]
    else:
        _find(tracks.rec_stages, ak1.Array(stages), builder)
        return builder.snapshot() == 1


@nb.jit(nopython=True)
def _find(rec_stages, stages, builder):
    """construct an awkward1 array with the same structure as tracks.rec_stages.
    When stages are found, the Array is filled with value 1, otherwise it is filled
    with value 0.

    Parameters
    ----------
    rec_stages : awkward1 Array
        tracks.rec_stages from multiple events.
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


@nb.jit(nopython=True)
def _find_single(rec_stages, stages, builder):
    """construct an awkward1 array with the same structure as tracks.rec_stages.
    When stages are found, the Array is filled with value 1, otherwise it is filled
    with value 0.

    Parameters
    ----------
    rec_stages : awkward1 Array
        tracks.rec_stages from a SINGLE event.
    stages : awkward1 Array
        reconstruction stages of interest.
    builder : awkward1.highlevel.ArrayBuilder
        awkward1 Array builder.
    """
    builder.begin_list()
    for s in rec_stages:
        num_stages = len(s)
        if num_stages == len(stages):
            found = 0
            for j in range(num_stages):
                if s[j] == stages[j]:
                    found += 1
            if found == num_stages:
                builder.append(1)
            else:
                builder.append(0)
        else:
            builder.append(0)
    builder.end_list()


def best_jmuon(tracks):
    """select the best JMUON track.

    Parameters
    ----------
    tracks : class km3io.offline.OfflineBranch
        tracks, or one track, or slice of tracks, or slices of tracks.

    Returns
    -------
    km3io.offline.OfflineBranch
        the longest + highest likelihood track reconstructed with JMUON.
    """
    mask = _mask_rec_stages_in_range_min_max(tracks, krec.JMUONBEGIN,
                                             krec.JMUONEND)

    return _max_lik_track(_longest_tracks(tracks[mask]))


def best_jshower(tracks):
    """select the best JSHOWER track.

    Parameters
    ----------
    tracks : class km3io.offline.OfflineBranch
        tracks, or one track, or slice of tracks, or slices of tracks.

    Returns
    -------
    km3io.offline.OfflineBranch
        the longest + highest likelihood track reconstructed with JSHOWER.
    """
    mask = _mask_rec_stages_in_range_min_max(tracks, krec.JSHOWERBEGIN,
                                             krec.JSHOWEREND)

    return _max_lik_track(_longest_tracks(tracks[mask]))


def best_aashower(tracks):
    """select the best AASHOWER track.

    Parameters
    ----------
    tracks : class km3io.offline.OfflineBranch
        tracks, or one track, or slice of tracks, or slices of tracks.

    Returns
    -------
    km3io.offline.OfflineBranch
        the longest + highest likelihood track reconstructed with AASHOWER.
    """
    mask = _mask_rec_stages_in_range_min_max(tracks, krec.AASHOWERBEGIN,
                                             krec.AASHOWEREND)

    return _max_lik_track(_longest_tracks(tracks[mask]))


def best_dusjshower(tracks):
    """select the best DISJSHOWER track.

    Parameters
    ----------
    tracks : class km3io.offline.OfflineBranch
        tracks, or one track, or slice of tracks, or slices of tracks.

    Returns
    -------
    km3io.offline.OfflineBranch
        the longest + highest likelihood track reconstructed with DUSJSHOWER.
    """
    mask = _mask_rec_stages_in_range_min_max(tracks, krec.DUSJSHOWERBEGIN,
                                             krec.DUSJSHOWEREND)

    return _max_lik_track(_longest_tracks(tracks[mask]))


def _mask_rec_stages_in_range_min_max(tracks, min, max):
    """mask tracks where rec_stages are withing the range(min, max).

    Parameters
    ----------
    tracks : class km3io.offline.OfflineBranch
        tracks, or one track, or slice of tracks, or slices of tracks.
    min : int
        minimum range of rec_stages.
    max : int
        maximum range of rec_stages.

    Returns
    -------
    awkward1 Array
        an awkward1 Array mask where True corresponds to the positions
        where stages were found. False otherwise.
    """
    builder = ak1.ArrayBuilder()
    if tracks.is_single:
        _find_in_range_single(tracks.rec_stages, min, max, builder)
        return (builder.snapshot() == 1)[0]
    else:
        _find_in_range(tracks.rec_stages, min, max, builder)
        return builder.snapshot() == 1


@nb.jit(nopython=True)
def _find_in_range(rec_stages, min, max, builder):
    """construct an awkward1 array with the same structure as tracks.rec_stages.
    When stages are within the range(min, max), the Array is filled with value 1, otherwise it is filled
    with value 0.

    Parameters
    ----------
    rec_stages : awkward1 Array
        tracks.rec_stages of MULTILPLE events.
    min : int
        minimum range of rec_stages.
    max : int
        maximum range of rec_stages.
    builder : awkward1.highlevel.ArrayBuilder
        awkward1 Array builder.
    """
    valid_stages = set(range(min, max + 1))
    for s in rec_stages:
        builder.begin_list()
        for i in s:
            num_stages = len(i)
            if num_stages != 0:
                found = 0
                for j in i:
                    if j in valid_stages:
                        found += 1
                if found == num_stages:
                    builder.append(1)
                else:
                    builder.append(0)
            else:
                builder.append(0)
        builder.end_list()


@nb.jit(nopython=True)
def _find_in_range_single(rec_stages, min, max, builder):
    """construct an awkward1 array with the same structure as tracks.rec_stages.
    When stages are within the range(min, max), the Array is filled with value 1, otherwise it is filled
    with value 0.

    Parameters
    ----------
    rec_stages : awkward1 Array
        tracks.rec_stages of a SINGLE event.
    min : int
        minimum range of rec_stages.
    max : int
        maximum range of rec_stages.
    builder : awkward1.highlevel.ArrayBuilder
        awkward1 Array builder.
    """

    builder.begin_list()
    valid_stages = set(range(min, max + 1))
    for s in rec_stages:
        num_stages = len(s)
        if num_stages != 0:
            found = 0
            for i in s:
                if i in valid_stages:
                    found += 1
            if found == num_stages:
                builder.append(1)
            else:
                builder.append(0)
        else:
            builder.append(0)
    builder.end_list()
