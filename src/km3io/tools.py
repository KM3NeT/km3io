#!/usr/bin/env python3
from collections import namedtuple
import numba as nb
import numpy as np
import awkward as ak

import km3io.definitions
from km3io.definitions import reconstruction as krec
from km3io.definitions import trigger as ktrg
from km3io.definitions import fitparameters as kfit
from km3io.definitions import w2list_genhen as kw2gen
from km3io.definitions import w2list_gseagen as kw2gsg


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
    return ak.fill_none(fit.mask[nonempty][..., fitparam], np.nan)


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

    tracks = apply_mask(tracks, m1)

    rec_stage_lengths = ak.num(tracks.rec_stages, axis=-1)
    max_rec_stage_length = ak.max(rec_stage_lengths, axis=axis)
    m2 = rec_stage_lengths == max_rec_stage_length
    tracks = apply_mask(tracks, m2)

    m3 = ak.argmax(tracks.lik, axis=axis, keepdims=True)

    out = apply_mask(tracks, m3)
    if original_ndim == 1:
        if isinstance(out, ak.Record):
            return select_first_entry_from_record(out)
        return out[0]
    return out[:, 0]


def apply_mask(record, mask):
    if isinstance(record, ak.Record):
        masked_record_data = {}
        for field in record.fields:
            value = record[field]
            masked_record_data[field] = value[mask]
        return ak.Record(masked_record_data)
    else:
        return record[mask]


def select_first_entry_from_record(record):
    assert isinstance(
        record, ak.Record
    ), f"Input has to be ak.Record, but is {type(record)}"

    first_entry_data = {}
    for field in record.fields:
        value = record[field]
        first_entry_data[field] = value[0]
    return ak.Record(first_entry_data)


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

            return ak.contents.NumpyArray(np_array)

        elif isinstance(layout, ak.contents.ListArray):
            if len(layout.stops) == 0:
                content = recurse(layout.content)
            else:
                content = recurse(layout.content[: np.max(layout.stops)])
            return type(layout)(layout.starts, layout.stops, content)

        elif isinstance(layout, ak.contents.ListOffsetArray):
            content = recurse(layout.content[: layout.offsets[-1]])
            return type(layout)(layout.offsets, content)

        elif isinstance(layout, ak.contents.RegularArray):
            content = recurse(layout.content)
            return ak.contents.RegularArray(content, layout.size)

        else:
            raise NotImplementedError(repr(arr))

    layout = ak.to_layout(arr, allow_record=True)
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


def has_jmuon(tracks):
    """Check if given tracks contain JMUON reconstruction."""
    m = mask(tracks.rec_stages, minmax=(krec.JMUONBEGIN, krec.JMUONEND))
    return ak.any(m, axis=m.ndim - 1)


def has_jshower(tracks):
    """Check if given tracks contain JSHOWER reconstruction."""
    m = mask(tracks.rec_stages, minmax=(krec.JSHOWERBEGIN, krec.JSHOWEREND))
    return ak.any(m, axis=m.ndim - 1)


def has_aashower(tracks):
    """Check if given tracks contain AASHOWER reconstruction."""
    m = mask(tracks.rec_stages, minmax=(krec.AASHOWERBEGIN, krec.AASHOWEREND))
    return ak.any(m, axis=m.ndim - 1)


def has_dusjshower(tracks):
    """Check if given tracks contain AASHOWER reconstruction."""
    m = mask(tracks.rec_stages, minmax=(krec.DUSJSHOWERBEGIN, krec.DUSJSHOWEREND))
    return ak.any(m, axis=m.ndim - 1)


def best_jmuon(tracks):
    """Select the best JMUON track."""
    return best_track(tracks, minmax=(krec.JMUONBEGIN, krec.JMUONEND))


def best_jshower(tracks):
    """Select the best JSHOWER track."""
    return best_track(tracks, minmax=(krec.JSHOWERBEGIN, krec.JSHOWEREND))


def best_aashower(tracks):
    """Select the best AASHOWER track."""
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


@nb.vectorize(("boolean(int64, int64)", "boolean(uint64, int64)"), nopython=True)
def is_bit_set(value, bit_position):
    """Returns true if a bit at the given position is 1.

    value: int or array([u]int64)
      The value to check, can be a single value or an array of values.
    bit_position: int
      0 for the first position, 1 for the second etc.
    """
    return bool(value & (1 << bit_position))


def is_3dshower(trigger_mask):
    """Returns True if the trigger mask contains the 3D shower flag.

    Parameters
    ----------
    trigger_mask : int or array(int)
      A value or an array of the trigger_mask, either of an event, or a hit.
    """
    return is_bit_set(trigger_mask, ktrg.JTRIGGER3DSHOWER)


def is_mxshower(trigger_mask):
    """Returns True if the trigger mask contains the MX shower flag.

    Parameters
    ----------
    trigger_mask : int or array(int)
      A value or an array of the trigger_mask, either of an event, or a hit.
    """
    return is_bit_set(trigger_mask, ktrg.JTRIGGERMXSHOWER)


def is_3dmuon(trigger_mask):
    """Returns True if the trigger mask contains the 3D muon flag.

    Parameters
    ----------
    trigger_mask : int or array(int)
      A value or an array of the trigger_mask, either of an event, or a hit.
    """
    return is_bit_set(trigger_mask, ktrg.JTRIGGER3DMUON)


def get_w2list_idx(f):
    """
    Get the correct w2list_idx for the given file, or None if there is none.

    Parameters
    ----------
    f : km3io.OfflineReader
        The file.

    """
    w2s_idx = {
        "genhen": km3io.definitions.w2list_genhen_idx,
        "gseagen": km3io.definitions.w2list_gseagen_idx,
    }
    sim_program = f.header.simul.program.lower()
    return w2s_idx.get(sim_program)


def is_nanobeacon(trigger_mask):
    """Returns True if the trigger mask contains the nano-beacon flag.

    Parameters
    ----------
    trigger_mask : int or array(int)
      A value or an array of the trigger_mask, either of an event, or a hit.
    """
    return is_bit_set(trigger_mask, ktrg.JTRIGGERNB)


class TimeConverter(object):
    """
    Auxiliary class to convert Monte Carlo hit times to DAQ/triggered hit times.
    """

    FRAME_TIME_NS = 1e8  # [ns]

    def __init__(self, event):

        self.__t0 = event.mc_t  # [ns]
        self.__t1 = self.get_time_of_frame(event.frame_index)  # [ns]

    def get_time_of_frame(self, frame_index):
        """
        Get start time of frame in ns since start of run for a given frame index

        Parameters
        ----------
        frame_index: int
          The index of the DAQ frame
        """

        if frame_index > 0:
            return (frame_index - 1) * self.FRAME_TIME_NS  # [ns]
        else:
            return 0  # [ns]

    def get_DAQ_time(self, t0):
        """
        Get DAQ/triggered hit time

        Parameters
        ----------
        t0: float or array(float)
          Simulated time [ns]
        """
        return t0 + (self.__t0 - self.__t1)  # [ns]

    def get_MC_time(self, t0):
        """
        Get Monte Carlo hit time

        Parameters
        ----------
        t0: float or array(float)
          DAQ/trigger hit time [ns]
        """
        return t0 - (self.__t0 - self.__t1)  # [ns]


def angle(v1, v2, normalized=False):
    """
    Compute the unsigned angle between two vectors. For a stacked input, the
    angle is computed pairwise. Inspired by the "vg" Python package.

    Parameters
    ----------
    v1 : np.array
        With shape `(3,)` or a `kx3` stack of vectors.
    v2 : np.array
        A vector or stack of vectors with the same shape as `v1`.
    normalized : bool
        By default, the vectors will be normalised unless `normalized` is `True`.

    Returns
    -------
    A float or a vector of floats with the angle in radians.

    """
    dot_products = np.einsum("ij,ij->i", v1.reshape(-1, 3), v2.reshape(-1, 3))

    if normalized:
        cosines = dot_products
    else:
        cosines = dot_products / magnitude(v1) / magnitude(v2)

    # The dot product can exceed 1 or -1 and arccos will fail unless we clip
    angles = np.arccos(np.clip(cosines, -1.0, 1.0))

    if v1.ndim == v2.ndim == 1:
        return angles[0]

    return angles


def magnitude(v):
    """
    Calculates the magnitude of a vector or array of vectors.

    Parameters
    ----------
    v : np.array
        With shape `(3,)` or `kx3` stack of vectors.

    Returns
    -------
    A float or a vector of floats with the magnitudes.
    """
    if v.ndim == 1:
        return np.linalg.norm(v)
    elif v.ndim == 2:
        return np.linalg.norm(v, axis=1)
    else:
        ValueError("Unsupported dimensions")


def theta(v):
    """Neutrino direction in polar coordinates.

    Parameters
    ----------
    v : array (x, y, z)

    Notes
    -----
    Downgoing event: theta = 180deg
    Horizont: 90deg
    Upgoing: theta = 0

    Angles in radians.

    """
    v = np.atleast_2d(v)
    dir_z = v[:, 2]
    return theta_separg(dir_z)


def theta_separg(dir_z):
    return np.arccos(dir_z)


def phi(v):
    """Neutrino direction in polar coordinates.

    Parameters
    ----------
    v : array (x, y, z)


    Notes
    -----
    ``phi``, ``theta`` is the opposite of ``zenith``, ``azimuth``.

    Angles in radians.

    """
    v = np.atleast_2d(v)
    dir_x = v[:, 0]
    dir_y = v[:, 1]
    return phi_separg(dir_x, dir_y)


def phi_separg(dir_x, dir_y):
    p = np.arctan2(dir_y, dir_x)
    p[p < 0] += 2 * np.pi
    return p


def zenith(v):
    """Return the zenith angle in radians.

    Parameters
    ----------
    v : array (x, y, z)


    Notes
    -----
    Defined as 'Angle respective to downgoing'.
    Downgoing event: zenith = 0
    Horizont: 90deg
    Upgoing: zenith = 180deg

    """
    return angle_between((0, 0, -1), v)


def azimuth(v):
    """Return the azimuth angle in radians.

    Parameters
    ----------
    v : array (x, y, z)


    Notes
    -----
    ``phi``, ``theta`` is the opposite of ``zenith``, ``azimuth``.

    This is the 'normal' azimuth definition -- beware of how you
    define your coordinates. KM3NeT defines azimuth
    differently than e.g. SLALIB, astropy, the AAS.org

    """
    v = np.atleast_2d(v)
    azi = phi(v) - np.pi
    azi[azi < 0] += 2 * np.pi
    if len(azi) == 1:
        return azi[0]
    return azi


def angle_between(v1, v2, axis=0):
    """Returns the angle in radians between vectors 'v1' and 'v2'.

    If axis=1 it evaluates the angle between arrays of vectors.

    Examples
    --------
    >>> angle_between((1, 0, 0), (0, 1, 0))
    1.5707963267948966
    >>> angle_between((1, 0, 0), (1, 0, 0))
    0.0
    >>> angle_between((1, 0, 0), (-1, 0, 0))
    3.141592653589793
    >>> v1 = np.array([[1, 0, 0], [1, 0, 0]])
    >>> v2 = np.array([[0, 1, 0], [-1, 0, 0]])
    >>> angle_between(v1, v2, axis=1)
    array([1.57079633, 3.14159265])

    """
    if axis == 0:
        v1_u = unit_vector(v1)
        v2_u = unit_vector(v2)
        # Don't use `np.dot`, does not work with all shapes
        return np.arccos(np.clip(np.inner(v1_u, v2_u), -1, 1))
    elif axis == 1:
        return angle(v1, v2)  # returns angle in deg
    else:
        raise ValueError("unsupported axis")


def unit_vector(vector, **kwargs):
    """Returns the unit vector of the vector."""
    vector = np.array(vector)
    out_shape = vector.shape
    vector = np.atleast_2d(vector)
    unit = vector / np.linalg.norm(vector, axis=1, **kwargs)[:, None]
    return unit.reshape(out_shape)
