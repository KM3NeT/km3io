#!/usr/bin/env python3
from collections import namedtuple
import numba as nb
import numpy as np
import awkward as ak
import uproot3

from km3io.definitions import reconstruction as krec
from km3io.definitions import trigger as ktrg
from km3io.definitions import fitparameters as kfit
from km3io.definitions import w2list_genhen as kw2gen
from km3io.definitions import w2list_gseagen as kw2gsg

# 110 MB based on the size of the largest basket found so far in km3net
BASKET_CACHE_SIZE = 110 * 1024 ** 2
BASKET_CACHE = uproot3.cache.ThreadSafeArrayCache(BASKET_CACHE_SIZE)


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
                "using the index chain {}".format(
                    repr(original_obj), depth, idx, indices
                )
            )
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
    return out[: entry_idx + 1]


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


def get_w2list_param(events, generator, param):
    """Get all the values of a specific parameter from the w2list
    in offline neutrino files.

    Parameters
    ----------
    events : km3io.offline.OfflineBranch
        events class in offline neutrino files.
    generator : str
        the name of the software generating neutrinos, it is either
        'genhen' or 'gseagen'.
    param : str
        the name of the parameters found in w2list as defined in the
        KM3NeT-Dataformat for both genhen and gseagen.

    Returns
    -------
    awkward.Array
        array of the values of interest.
    """
    w2list_gseagen_keys = set(kw2gsg.keys())
    w2list_genhen_keys = set(kw2gen.keys())

    if (generator == "gseagen") and param in w2list_gseagen_keys:
        return events.w2list[:, kw2gsg[param]]

    if generator == "genhen" and param in w2list_genhen_keys:
        return events.w2list[:, kw2gen[param]]


def fitinf(fitparam, tracks):
    """Access fit parameters in tracks.fitinf.

    Parameters
    ----------
    fitparam : int
        the fit parameter key according to fitparameters defined in
        KM3NeT-Dataformat.
    tracks : km3io.offline.OfflineBranch
        the tracks class. both full tracks branch or a slice of the
        tracks branch (example tracks[:, 0]) work.

    Returns
    -------
    awkward1.Array
        awkward array of the values of the fit parameter requested.
    """
    fit = tracks.fitinf
    index = fitparam
    if tracks.is_single and len(tracks) != 1:
        params = fit[count_nested(fit, axis=1) > index]
        out = params[:, index]

    if tracks.is_single and len(tracks) == 1:
        out = fit[index]

    else:
        if len(tracks[0]) == 1:  # case of tracks slice with 1 track per event.
            params = fit[count_nested(fit, axis=1) > index]
            out = params[:, index]
        else:
            params = fit[count_nested(fit, axis=2) > index]
            out = ak.Array([i[:, index] for i in params])

    return out


def count_nested(arr, axis=0):
    """Count elements in a nested awkward Array.

    Parameters
    ----------
    arr : awkward1.Array
        Array of data. Example tracks.fitinf or tracks.rec_stages.
    axis : int, optional
        axis = 0: to count elements in the outmost level of nesting.
        axis = 1: to count elements in the first level of nesting.
        axis = 2: to count elements in the second level of nesting.

    Returns
    -------
    awkward1.Array or int
        counts of elements found in a nested awkward1 Array.
    """
    if axis == 0:
        return ak.num(arr, axis=0)
    if axis == 1:
        return ak.num(arr, axis=1)
    if axis == 2:
        return ak.count(arr, axis=2)


def get_multiplicity(tracks, rec_stages):
    """Tracks selection based on specific reconstruction stages.

    Counts how many tracks with the specific reconstructions stages
    are found per event.

    Parameters
    ----------
    tracks : km3io.offline.OfflineBranch
        tracks or a subste of tracks.
    rec_stages : list
        Reconstruction stages (the ordering is respected) e.g. [1, 2, 3, 4, 5].

    Returns
    -------
    awkward1.Array
        tracks multiplicty.
    """
    masked_tracks = tracks[mask(tracks.rec_stages, sequence=rec_stages)]

    try:
        axis = tracks.ndim
    except AttributeError:
        axis = 0

    out = count_nested(masked_tracks.rec_stages, axis=axis)

    return out


def best_track(tracks, startend=None, minmax=None, stages=None):
    """Best track selection.

    Parameters
    ----------
    tracks : km3io.offline.OfflineBranch
        Array of tracks or jagged array of tracks (multiple events).
    startend: tuple(int, int), optional
        The required first and last stage in tracks.rec_stages.
    minmax: tuple(int, int), optional
        The range (minimum and maximum) value of rec_stages to take into account.
    stages : list or set, optional
        - list: the order of the rec_stages is respected.
        - set: a subset of required stages; the order is irrelevant.

    Returns
    -------
    km3io.offline.OfflineBranch
        The best tracks based on the selection.

    Raises
    ------
    ValueError
        - too many inputs specified.
        - no inputs are specified.

    """
    inputs = (stages, startend, minmax)

    if all(v is None for v in inputs):
        raise ValueError("either stages, startend or minmax must be specified.")

    if stages is not None and (startend is not None or minmax is not None):
        raise ValueError("Please specify either a range or a set of rec stages.")

    if stages is not None and startend is None and minmax is None:
        if isinstance(stages, list):
            m1 = mask(tracks.rec_stages, sequence=stages)
        elif isinstance(stages, set):
            m1 = mask(tracks.rec_stages, atleast=list(stages))
        else:
            raise ValueError("stages must be a list or a set of integers")

    if startend is not None and minmax is None and stages is None:
        m1 = mask(tracks.rec_stages, startend=startend)

    if minmax is not None and startend is None and stages is None:
        m1 = mask(tracks.rec_stages, minmax=minmax)

    try:
        axis = tracks.ndim
    except AttributeError:
        axis = 0

    tracks = tracks[m1]

    rec_stage_lengths = ak.num(tracks.rec_stages, axis=axis + 1)
    max_rec_stage_length = ak.max(rec_stage_lengths, axis=axis)
    m2 = rec_stage_lengths == max_rec_stage_length
    tracks = tracks[m2]

    m3 = ak.argmax(tracks.lik, axis=axis, keepdims=True)

    out = tracks[m3]
    if isinstance(out, ak.highlevel.Record):
        return namedtuple("BestTrack", out.fields)(
            *[getattr(out, a)[0] for a in out.fields]
        )
    return out


def mask(arr, sequence=None, startend=None, minmax=None, atleast=None):
    """Return a boolean mask which check each nested sub-array for a condition.

    Parameters
    ----------
    arr : awkward.Array with ndim>=2
        The array to mask.
    startend: tuple(int, int), optional
        True for entries where the first and last element are matching the tuple.
    minmax: tuple(int, int), optional
        True for entries where each element is within the min-max-range.
    sequence : list(int), optional
        True for entries which contain the exact same elements (in that specific
        order)
    atleast : list(int), optional
        True for entries where at least the provided elements are present.
    """
    inputs = (sequence, startend, minmax, atleast)

    if all(v is None for v in inputs):
        raise ValueError(
            "either sequence, startend, minmax or atleast must be specified."
        )

    builder = ak.ArrayBuilder()
    # Numba has very limited recursion support, so this is hardcoded
    if arr.ndim == 2:
        _mask2d(arr, builder, sequence, startend, minmax, atleast)
    else:
        _mask3d(arr, builder, sequence, startend, minmax, atleast)
    return builder.snapshot()


def mask_alt(arr, start, end):
    nonempty = ak.num(arr, axis=-1) > 0
    mask = ((arr.mask[nonempty][..., 0] == start) & (arr.mask[nonempty][..., -1] == end))
    return ak.fill_none(mask, False)


@nb.njit
def _mask3d(arr, builder, sequence=None, startend=None, minmax=None, atleast=None):
    for subarray in arr:
        builder.begin_list()
        _mask2d(subarray, builder, sequence, startend, minmax, atleast)
        builder.end_list()


@nb.njit
def _mask_startend(arr, builder, start, end):
    for els in arr:
        if len(els) > 0 and els[0] == start and els[-1] == end:
            builder.boolean(True)
        else:
            builder.boolean(False)


@nb.njit
def _mask_minmax(arr, builder, min, max):
    for els in arr:
        for el in els:
            if el < min or el > max:
                builder.boolean(False)
                break
        else:
            builder.boolean(True)


@nb.njit
def _mask_sequence(arr, builder, sequence):
    n = len(sequence)
    for els in arr:
        if len(els) != n:
            builder.boolean(False)
        else:
            for i in range(n):
                if els[i] != sequence[i]:
                    builder.boolean(False)
                    break
            else:
                builder.boolean(True)


@nb.njit
def _mask_atleast(arr, builder, atleast):
    for els in arr:
        for e in atleast:
            if e not in els:
                builder.boolean(False)
                break
        else:
            builder.boolean(True)


@nb.njit
def _mask2d(arr, builder, sequence=None, startend=None, minmax=None, atleast=None):
    if startend is not None:
        _mask_startend(arr, builder, *startend)
    elif minmax is not None:
        _mask_minmax(arr, builder, *minmax)
    elif sequence is not None:
        _mask_sequence(arr, builder, sequence)
    elif atleast is not None:
        _mask_atleast(arr, builder, atleast)


def best_jmuon(tracks):
    """Select the best JMUON track."""
    return best_track(tracks, minmax=(krec.JMUONBEGIN, krec.JMUONEND))


def best_jshower(tracks):
    """Select the best JSHOWER track."""
    return best_track(tracks, minmax=(krec.JSHOWERBEGIN, krec.JSHOWEREND))


def best_aashower(tracks):
    """Select the best AASHOWER track. """
    return best_track(tracks, minmax=(krec.AASHOWERBEGIN, krec.AASHOWEREND))


def best_dusjshower(tracks):
    """Select the best DISJSHOWER track."""
    return best_track(tracks, minmax=(krec.DUSJSHOWERBEGIN, krec.DUSJSHOWEREND))


def is_cc(fobj):
    """Determin if events are a result of a Charged Curent interaction (CC)
    or a Neutral Curent interaction (NC).

    Parameters
    ----------
    fobj : km3io.offline.OfflineReader
        offline neutrino file object.

    Returns
    -------
    awkward1.highlevel.Array
        a mask where True corresponds to an event resulting from a CC interaction.

    Raises
    ------
    ValueError
        if the simulations program used to generate the neutrino file is neither gseagen nor genhen.
    """
    program = fobj.header.simul.program
    w2list = fobj.events.w2list
    len_w2lists = ak.num(w2list, axis=1)

    if all(len_w2lists <= 7):  # old nu file have w2list of len 7.
        usr_names = fobj.events.mc_tracks.usr_names
        usr_data = fobj.events.mc_tracks.usr
        mask_cc_flag = usr_names[:, 0] == b"cc"
        inter_ID = usr_data[:, 0][mask_cc_flag]
        out = ak.flatten(inter_ID == 2)  # 2 is the interaction ID for CC.

    else:
        if "gseagen" in program.lower():

            # According to: https://wiki.km3net.de/index.php/Simulations/The_gSeaGen_code#Physics_event_entries
            # the interaction types are defined as follow:

            # INTER   Interaction type
            # 1       EM
            # 2       Weak[CC]
            # 3       Weak[NC]
            # 4       Weak[CC+NC+interference]
            # 5       NucleonDecay

            cc_flag = w2list[:, kw2gsg.W2LIST_GSEAGEN_CC]
            out = cc_flag > 0  # to be tested with a newly generated nu file.
        if "genhen" in program.lower():
            cc_flag = w2list[:, kw2gen.W2LIST_GENHEN_CC]
            out = cc_flag > 0
        else:
            raise ValueError(f"simulation program {program} is not implemented.")

    return out
