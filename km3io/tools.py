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
        KM3NeT-Dataformat (see km3io.definitions.fitparameters).
    tracks : ak.Array or km3io.rootio.Branch
        reconstructed tracks with .fitinf attribute

    Returns
    -------
    awkward1.Array
        awkward array of the values of the fit parameter requested. Missing
        values are set to NaN.
    """
    fit = tracks.fitinf
    nonempty = ak.num(fit, axis=-1) > 0
    return ak.fill_none(fit.mask[nonempty][..., 0], np.nan)


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

    out = count_nested(masked_tracks.rec_stages, axis=tracks.ndim - 1)

    return out


def best_track(tracks, startend=None, minmax=None, stages=None):
    """Best track selection.

    Parameters
    ----------
    tracks : awkward.Array
      A list of tracks or doubly nested tracks, usually from
      OfflineReader.events.tracks or subarrays of that, containing recunstructed
      tracks.
    startend: tuple(int, int), optional
      The required first and last stage in tracks.rec_stages.
    minmax: tuple(int, int), optional
      The range (minimum and maximum) value of rec_stages to take into account.
    stages : list or set, optional
      - list: the order of the rec_stages is respected.
      - set: a subset of required stages; the order is irrelevant.

    Returns
    -------
    awkward.Array or namedtuple
      Be aware that the dimensions are kept, which means that the final
      track attributes are nested when multiple events are passed in.
      If a single event (just a list of tracks) is provided, a named tuple
      with a single track and flat attributes is created.

    Raises
    ------
    ValueError
      When invalid inputs are specified.

    """
    inputs = (stages, startend, minmax)

    if sum(v is not None for v in inputs) != 1:
        raise ValueError("either stages, startend or minmax must be specified.")

    if stages is not None:
        if isinstance(stages, list):
            m1 = mask(tracks.rec_stages, sequence=stages)
        elif isinstance(stages, set):
            m1 = mask(tracks.rec_stages, atleast=list(stages))
        else:
            raise ValueError("stages must be a list or a set of integers")

    if startend is not None:
        m1 = mask(tracks.rec_stages, startend=startend)

    if minmax is not None:
        m1 = mask(tracks.rec_stages, minmax=minmax)

    try:
        original_ndim = tracks.ndim
    except AttributeError:
        original_ndim = 1
    axis = 1 if original_ndim == 2 else 0

    tracks = tracks[m1]

    rec_stage_lengths = ak.num(tracks.rec_stages, axis=-1)
    max_rec_stage_length = ak.max(rec_stage_lengths, axis=axis)
    m2 = rec_stage_lengths == max_rec_stage_length
    tracks = tracks[m2]

    m3 = ak.argmax(tracks.lik, axis=axis, keepdims=True)

    out = tracks[m3]
    if original_ndim == 1:
        if isinstance(out, ak.Record):
            return out[:, 0]
        return out[0]
    return out[:, 0]


def mask(arr, sequence=None, startend=None, minmax=None, atleast=None):
    """Return a boolean mask which mask each nested sub-array for a condition.

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

    An extensive discussion about this implementation can be found at:
    https://github.com/scikit-hep/awkward-1.0/issues/580
    Many thanks for Jim for the fruitful discussion and the final implementation.
    """
    inputs = (sequence, startend, minmax, atleast)

    if sum(v is not None for v in inputs) != 1:
        raise ValueError(
            "either sequence, startend, minmax or atleast must be specified."
        )

    def recurse(layout):
        if layout.purelist_depth == 2:
            if startend is not None:
                np_array = _mask_startend(ak.Array(layout), *startend)
            elif minmax is not None:
                np_array = _mask_minmax(ak.Array(layout), *minmax)
            elif sequence is not None:
                np_array = _mask_sequence(ak.Array(layout), np.array(sequence))
            elif atleast is not None:
                np_array = _mask_atleast(ak.Array(layout), np.array(atleast))

            return ak.layout.NumpyArray(np_array)

        elif isinstance(
            layout,
            (
                ak.layout.ListArray32,
                ak.layout.ListArrayU32,
                ak.layout.ListArray64,
            ),
        ):
            if len(layout.stops) == 0:
                content = recurse(layout.content)
            else:
                content = recurse(layout.content[: np.max(layout.stops)])
            return type(layout)(layout.starts, layout.stops, content)

        elif isinstance(
            layout,
            (
                ak.layout.ListOffsetArray32,
                ak.layout.ListOffsetArrayU32,
                ak.layout.ListOffsetArray64,
            ),
        ):
            content = recurse(layout.content[: layout.offsets[-1]])
            return type(layout)(layout.offsets, content)

        elif isinstance(layout, ak.layout.RegularArray):
            content = recurse(layout.content)
            return ak.layout.RegularArray(content, layout.size)

        else:
            raise NotImplementedError(repr(arr))

    layout = ak.to_layout(arr, allow_record=True, allow_other=False)
    return ak.Array(recurse(layout))


@nb.njit
def _mask_startend(arr, start, end):
    out = np.empty(len(arr), np.bool_)
    for i, subarr in enumerate(arr):
        out[i] = len(subarr) > 0 and subarr[0] == start and subarr[-1] == end
    return out


@nb.njit
def _mask_minmax(arr, min, max):
    out = np.empty(len(arr), np.bool_)
    for i, subarr in enumerate(arr):
        if len(subarr) == 0:
            out[i] = False
        else:
            for el in subarr:
                if el < min or el > max:
                    out[i] = False
                    break
            else:
                out[i] = True
    return out


@nb.njit
def _mask_sequence(arr, sequence):
    out = np.empty(len(arr), np.bool_)
    n = len(sequence)
    for i, subarr in enumerate(arr):
        if len(subarr) != n:
            out[i] = False
        else:
            for j in range(n):
                if subarr[j] != sequence[j]:
                    out[i] = False
                    break
            else:
                out[i] = True
    return out


@nb.njit
def _mask_atleast(arr, atleast):
    out = np.empty(len(arr), np.bool_)
    for i, subarr in enumerate(arr):
        for req_el in atleast:
            if req_el not in subarr:
                out[i] = False
                break
        else:
            out[i] = True
    return out


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

    # According to: https://wiki.km3net.de/index.php/Simulations/The_gSeaGen_code#Physics_event_entries
    # the interaction types are defined as follow:

    # INTER   Interaction type
    # 1       EM
    # 2       Weak[CC]
    # 3       Weak[NC]
    # 4       Weak[CC+NC+interference]
    # 5       NucleonDecay

    if all(len_w2lists <= 7):  # old nu file have w2list of len 7.
        # Checking the `cc` value in usr of the first mc_tracks,
        # which are the primary neutrinos and carry the event property.
        # This has been changed in 2020 to be a property in the w2list.
        # See https://git.km3net.de/common/km3net-dataformat/-/issues/23
        return usr(fobj.events.mc_tracks[:, 0], "cc") == 2

    else:
        # TODO: to be tested with a newly generated files with th eupdated
        # w2list definitionn.
        if "gseagen" in program.lower():
            return w2list[:, kw2gen.W2LIST_GSEAGEN_CC] == 2
        if "genhen" in program.lower():
            return w2list[:, kw2gen.W2LIST_GENHEN_CC] == 2
        else:
            raise NotImplementedError(
                f"don't know how to determine the CC-ness of {program} files."
            )


def usr(objects, field):
    """Return the usr-data for a given field.

    Parameters
    ----------
    objects : awkward.Array
      Events, tracks, hits or whatever objects which have usr and usr_names
      fields (e.g. OfflineReader().events).
    """
    if len(unique(ak.num(objects.usr_names))) > 1:
        # let's do it the hard way
        return ak.flatten(objects.usr[objects.usr_names == field])
    available_fields = objects.usr_names[0].tolist()
    idx = available_fields.index(field)
    return objects.usr[:, idx]
