The km3io Python package
========================

.. image:: https://git.km3net.de/km3py/km3io/badges/master/pipeline.svg
    :target: https://git.km3net.de/km3py/km3io/pipelines

.. image:: https://git.km3net.de/km3py/km3io/badges/master/coverage.svg
    :target: https://km3py.pages.km3net.de/km3io/coverage

.. image:: https://api.codacy.com/project/badge/Grade/0660338483874475ba04f324de2123ec
    :target: https://www.codacy.com/manual/tamasgal/km3io?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=KM3NeT/km3io&amp;utm_campaign=Badge_Grade

.. image:: https://examples.pages.km3net.de/km3badges/docs-latest-brightgreen.svg
    :target: https://km3py.pages.km3net.de/km3io

This software provides a set of Python classes to read KM3NeT ROOT files
without having ROOT, Jpp or aanet installed. It only depends on Python 3.5+ and the amazing `uproot <https://github.com/scikit-hep/uproot>`__ package and gives you access to the data via numpy arrays.

It's very easy to use and according to the `uproot <https://github.com/scikit-hep/uproot>`__ benchmarks, it is able to outperform the ROOT I/O performance. 

**Note:** Beware that this package is in the development phase, so the API will change until version ``1.0.0`` is released!

Installation
============

Install km3io using pip::

    pip install km3io 

To get the latest (stable) development release::

    pip install git+https://git.km3net.de/km3py/km3io.git

**Reminder:** km3io is **not** dependent on aanet, ROOT or Jpp!

Questions
=========

If you have a question about km3io, please proceed as follows:

- Read the documentation below.
- Explore the `examples <https://km3py.pages.km3net.de/km3io/examples.html>`__ in the documentation.
- Haven't you found an answer to your question in the documentation, post a git issue with your question showing us an example of what you have tried first, and what you would like to do.
- Have you noticed a bug, please post it in a git issue, we appreciate your contribution.

Tutorial
========

**Table of contents:**

* `Introduction <#introduction>`__

  * `Overview of daq files <#overview-of-daq-files>`__

  * `Overview of offline files <#overview-of-offline-files>`__

* `DAQ files reader <#daq-files-reader>`__

  * `Reading Events <#reading-events>`__

  * `Reading SummarySlices <#reading-summaryslices>`__

  * `Reading Timeslices <#reading-timeslices>`__

* `Offline files reader <#offline-file-reader>`__

  * `reading events data <#reading-events-data>`__

  * `reading usr data of events <#reading-usr-data-of-events>`__

  * `reading hits data <#reading-hits-data>`__

  * `reading tracks data <#reading-tracks-data>`__

  * `reading mc hits data <#reading-mc-hits-data>`__

  * `reading mc tracks data <#reading-mc-tracks-data>`__



Introduction
------------

Most of km3net data is stored in root files. These root files are either created with `Jpp <https://git.km3net.de/common/jpp>`__ or `aanet <https://git.km3net.de/common/aanet>`__ software. A root file created with 
`Jpp <https://git.km3net.de/common/jpp>`__ is often referred to as "a Jpp root file". Similarly, a root file created with `aanet <https://git.km3net.de/common/aanet>`__ is often referred to as "an aanet file". In km3io, an aanet root file will always be reffered to as an ``offline file``, while a Jpp root file will always be referred to as a ``daq file``.

km3io is a Python package that provides a set of classes (``DAQReader`` and ``OfflineReader``) to read both daq root files and offline root files without any dependency to aanet, Jpp or ROOT. 

Data in km3io is often returned as a "lazyarray", a "jagged lazyarray" or a `Numpy <https://docs.scipy.org/doc/numpy>`__ array. A lazyarray is an array-like object that reads data on demand! In a lazyarray, only the first and the last chunks of data are read in memory. A lazyarray can be used with all Numpy's universal `functions <https://docs.scipy.org/doc/numpy/reference/ufuncs.html>`__. Here is how a lazyarray looks like:

.. code-block:: python3

    # <ChunkedArray [5971 5971 5971 ... 5971 5971 5971] at 0x7fb2341ad810>


A jagged array, is a 2+ dimentional array with different arrays lengths. In other words, a jagged array is an array of arrays of different sizes. So a jagged lazyarray is simply a jagged array of lazyarrays with different sizes. Here is how a jagged lazyarray looks like:


.. code-block:: python3

    # <JaggedArray [[102 102 102 ... 11517 11518 11518] [] [101 101 102 ... 11518 11518 11518] ... [101 101 102 ... 11516 11516 11517] [] [101 101 101 ... 11517 11517 11518]] at 0x7f74b0ef8810>


Overview of DAQ files
"""""""""""""""""""""
DAQ files, or also called online files, are written by the DataWriter and
contain events, timeslics and summary slices.


Overview of offline files
"""""""""""""""""""""""""

Offline files contain data about events, hits and tracks. Based on aanet version 2.0.0 documentation, the following tables show the definitions, the types and the units of the branches founds in the events, hits and tracks trees. A description of the file header are also displayed.

.. csv-table:: events keys definitions and units
   :header: "type", "name", "definition"
   :widths: 20, 20, 80

    "int", "id", "offline event identifier"
    "int", "det_id", "detector identifier from DAQ"
    "int", "mc_id", "identifier of the MC event (as found in ascii or antcc file)"
    "int", "run_id", "DAQ run identifier"
    "int", "mc_run_id", "MC run identifier"
    "int", "frame_index", "from the raw data"
    "ULong64_t", "trigger_mask", "trigger mask from raw data (i.e. the trigger bits)"
    "ULong64_t", "trigger_counter", "trigger counter"
    "unsigned int", "overlays", "number of overlaying triggered events"
    "TTimeStamp", "t", "UTC time of the start of the timeslice the event came from"
    "vec Hit", "hits", "list of hits"
    "vec Trk", "trks", "list of reconstructed tracks (can be several because of prefits,showers, etc)"
    "vec double", "w", "MC: Weights w[0]=w1 & w[1]=w2 &  w[2]]=w3"
    "vec double", "w2list", "MC: factors that make up w[1]=w2"
    "vec double", "w3list", "MC: atmospheric flux information"
    "double", "mc_t", "MC: time of the mc event"
    "vec Hit", "mc_hits", "MC: list of MC truth hits"
    "vec Trk", "mc_trks", "MC: list of MC truth tracks"
    "string", "comment", "user can use this as he/she likes"
    "int", "index", "user can use this as he/she likes"


.. csv-table:: hits keys definitions and units
   :header: "type", "name", "definition"
   :widths: 20, 20, 80

    "int", "id", "hit id"
    "int", "dom_id", "module identifier from the data (unique in the detector)"
    "unsigned int", "channel_id", "PMT channel id {0,1, .., 31} local to module"
    "unsigned int", "tdc", "hit tdc (=time in ns)"
    "unsigned int", "tot", "tot value as stored in raw data (int for pyroot)"
    "int", "trig", "non-zero if the hit is a trigger hit"
    "int", "pmt_id", "global PMT identifier as found in evt files"
    "double", "t", "hit time (from calibration or MC truth)"
    "double", "a", "hit amplitude (in p.e.)"
    "vec", "pos", "hit position"
    "vec", "dir", "hit direction i.e. direction of the PMT"
    "double", "pure_t", "photon time before pmt simultion (MC only)"
    "double", "pure_a", "amptitude before pmt simution (MC only)"
    "int", "type", "particle type or parametrisation used for hit (mc only)"
    "int", "origin", "track id of the track that created this hit"
    "unsigned", "pattern_flags", "some number that you can use to flag the hit"


.. csv-table:: tracks keys definitions and units
   :header: "type", "name", "definition"
   :widths: 20, 20, 80

    "int", "id", "track identifier"
    "vec", "pos", "position of the track at time t"
    "vec", "dir", "track direction"
    "double", "t", "track time (when particle is at pos)"
    "double", "E", "Energy (either MC truth or reconstructed)"
    "double", "len", "length if applicable"
    "double", "lik", "likelihood or lambda value (for aafit: lambda)"
    "int", "type", "MC: particle type in PDG encoding"
    "int", "rec_type", "identifyer for the overall fitting algorithm/chain/strategy"
    "vec int", "rec_stages", "list of identifyers of succesfull fitting stages resulting in this track"
    "int", "status", "MC status code"
    "int", "mother_id", "MC id of the parent particle"
    "vec double", "fitinf", "place to store additional fit info for jgandalf see FitParameters.csv"
    "vec int", "hit_ids", "list of associated hit-ids (corresponds to Hit::id)"
    "vec double", "error_matrix", "(5x5) error covariance matrix (stored as linear vector)"
    "string", "comment", "user comment"


.. csv-table:: offline file header definitions
   :header: "name", "definition"
   :widths: 40, 80

    "DAQ", "livetime"
    "cut_primary cut_seamuon cut_in cut_nu", "Emin Emax cosTmin cosTmax"
    "generator physics simul", "program version date time"
    "seed", "program level iseed"
    "PM1_type_area", "type area TTS"
    "PDF", "i1 i2"
    "model", "interaction muon scattering numberOfEnergyBins"
    "can", "zmin zmax r"
    "genvol", "zmin zmax r volume numberOfEvents"
    "merge", "time gain"
    "coord_origin", "x y z"
    "translate", "x y z"
    "genhencut", "gDir Emin"
    "k40", "rate time"
    "norma", "primaryFlux numberOfPrimaries"
    "livetime", "numberOfSeconds errorOfSeconds"
    "flux", "type key file_1 file_2"
    "spectrum", "alpha"
    "fixedcan", "xcenter ycenter zmin zmax radius"
    "start_run", "run_id"


DAQ files reader
----------------

``km3io`` is able to read events, summary slices and timeslices (except the L0
slices, which is work in progress).

Let's have a look at some ORCA data (``KM3NeT_00000044_00005404.root``)

Reading Events
""""""""""""""

To get a lazy ragged array of the events:

.. code-block:: python3

  import km3io
  f = km3io.DAQReader("KM3NeT_00000044_00005404.root")


That's it, we created an object which gives access to all the events, but the
relevant data is still not loaded into the memory (lazy access)!
Now let's have a look at the hits data:

.. code-block:: python3

  >>> f.events
  Number of events: 17023
  >>> f.events[23].snapshot_hits.tot
  array([28, 22, 17, 29,  5, 27, 24, 26, 21, 28, 26, 21, 26, 24, 17, 28, 23,29, 27, 24, 23, 26, 29, 25, 18, 28, 24, 28, 26, 20, 25, 31, 28, 23, 26, 21, 30, 33, 27, 16, 23, 24, 19, 24, 27, 22, 23, 21, 25, 16, 28, 22, 22, 29, 24, 29, 24, 24, 25, 25, 21, 31, 26, 28, 30, 42, 28], dtype=uint8)

The resulting arrays are numpy arrays.

Reading SummarySlices
"""""""""""""""""""""

The following example shows how to access summary slices, in particular the DOM
IDs of the slice with the index ``23``:

.. code-block:: python3

  >>> f.summaryslices
  <km3io.daq.SummarySlices at 0x7effcc0e52b0>
  >>> f.summaryslices.slices[23].dom_id
  array([806451572, 806455814, 806465101, 806483369, 806487219, 806487226,
       806487231, 808432835, 808435278, 808447180, 808447186, 808451904,
       808451907, 808469129, 808472260, 808472265, 808488895, 808488990,
       808489014, 808489117, 808493910, 808946818, 808949744, 808951460,
       808956908, 808959411, 808961448, 808961480, 808961504, 808961655,
       808964815, 808964852, 808964883, 808964908, 808969848, 808969857,
       808972593, 808972598, 808972698, 808974758, 808974773, 808974811,
       808974972, 808976377, 808979567, 808979721, 808979729, 808981510,
       808981523, 808981672, 808981812, 808981864, 808982005, 808982018,
       808982041, 808982066, 808982077, 808982547, 808984711, 808996773,
       808997793, 809006037, 809007627, 809503416, 809521500, 809524432,
       809526097, 809544058, 809544061], dtype=int32)

The ``.dtype`` attribute (or in general, <TAB> completion) is useful to find out
more about the field structure:

.. code-block:: python3

  >>> f.summaryslices.headers.dtype
  dtype([(' cnt', '<u4'), (' vers', '<u2'), (' cnt2', '<u4'), (' vers2',
  '<u2'), (' cnt3', '<u4'), (' vers3', '<u2'), ('detector_id', '<i4'), ('run',
  '<i4'), ('frame_index', '<i4'), (' cnt4', '<u4'), (' vers4', '<u2'),
  ('UTC_seconds', '<u4'), ('UTC_16nanosecondcycles', '<u4')])
  >>> f.summaryslices.headers.frame_index
  <ChunkedArray [162 163 173 ... 36001 36002 36003] at 0x7effccd4af10>

The resulting array is a ``ChunkedArray`` which is an extended version of a
numpy array and behaves like one.

Reading Timeslices
""""""""""""""""""

Timeslices are split into different streams since 2017 and ``km3io`` currently
supports everything except L0, i.e. L1, L2 and SN streams. The API is
work-in-progress and will be improved in future, however, all the data is
already accessible (although in ugly ways ;-)

To access the timeslice data:

.. code-block:: python3

  >>> f.timeslices
  Available timeslice streams: L1, SN
  >>> f.timeslices.stream("L1", 24).frames
  {806451572: <Table [<Row 1577843> <Row 1577844> ... <Row 1578147>],
   806455814: <Table [<Row 1578148> <Row 1578149> ... <Row 1579446>],
   806465101: <Table [<Row 1579447> <Row 1579448> ... <Row 1580885>],
   ...
  }

The frames are represented by a dictionary where the key is the ``DOM ID`` and
the value a numpy array of hits, with the usual fields to access the PMT
channel, time and ToT:

.. code-block:: python3

   >>> f.timeslices.stream("L1", 24).frames[806451572].dtype
   dtype([('pmt', 'u1'), ('tdc', '<u4'), ('tot', 'u1')])
   >>> f.timeslices.stream("L1", 24).frames[806451572].tot
   array([29, 21,  8, 29, 22, 20,  1, 37, 11, 22, 11, 22, 12, 20, 29, 94, 26,
          26, 18, 16, 13, 22,  6, 29, 24, 30, 14, 26, 12, 23,  4, 25,  6, 27,
           5, 13, 21, 28, 30,  4, 25, 10,  5,  6,  5, 17,  4, 27, 24, 25, 27,
          28, 32,  6,  3, 15,  3, 20, 33, 30, 30, 20, 28,  6,  7,  3, 14, 12,
          25, 27, 26, 25, 22, 21, 23,  6, 20, 21,  4,  4, 10, 24, 29, 12, 30,
           5,  3, 24, 15, 14, 25,  5, 27, 23, 26,  4, 28, 15, 34, 22,  4, 29,
          24, 26, 29, 23, 25, 28, 14, 31, 27, 26, 27, 28, 23, 54,  4, 25, 11,
          28, 25, 24,  7, 27, 28, 28, 18,  3, 13, 14, 38, 28,  4, 21, 16, 16,
           4, 21, 26, 21, 28, 64, 21,  1, 24, 21, 26, 26, 25,  4, 28, 11, 31,
          10, 24, 24, 28, 10,  6,  4, 20, 26, 18,  5, 18, 24,  5, 27, 23, 20,
          29, 20,  6, 18,  5, 24, 17, 28, 24, 15, 26, 27, 25,  9,  3, 18,  3,
          34, 29, 10, 25, 30, 28, 19, 26, 34, 27, 14, 17, 15, 26,  8, 19,  5,
          27, 13,  5, 27, 46,  3, 25, 13, 30,  9, 21, 12,  1, 32, 25,  8, 30,
           4, 24, 11,  3, 11, 27,  5, 13,  5, 16, 18,  3, 22, 10,  7, 32, 29,
          15, 20, 18, 16, 27,  5, 22,  4, 33,  5, 29, 24, 30,  7,  7, 25, 33,
           7, 20,  8, 30,  4,  4,  6, 26,  8, 24, 22, 12,  6,  3, 21, 28, 11,
          24, 27, 27,  6, 29,  5, 18, 11, 26,  5, 19, 32, 25,  4, 20, 35, 30,
           5,  3, 26, 30, 23, 28,  6, 25, 25,  5, 45, 23, 18, 29, 28, 23],
         dtype=uint8)



Offline files reader
--------------------

Let's have a look at some muons data from ORCA 4 lines simulations - run id 5971 (``datav6.0test.jchain.aanet.00005971.root``). 

**Note:** this file was cropped to 10 events only, so don't be surprised in this tutorial if you see few events in the file.

First, let's read our file:

.. code-block:: python3

  >>> import km3io as ki
  >>> file = 'my_file.root'
  >>> r = ki.OfflineReader(file)
  <km3io.offline.OfflineReader at 0x7f24cc2bd550>

and that's it! Note that `file` can be either an str of your file path, or a path-like object. 

To read the file header:

.. code-block:: python3

    >>> r.header
    DAQ             394
    PDF             4      58
    XSecFile        
    can             0 1027 888.4
    can_user        0.00 1027.00  888.40
    coord_origin    0 0 0
    cut_in          0 0 0 0
    cut_nu          100 1e+08 -1 1
    cut_primary     0 0 0 0
    cut_seamuon     0 0 0 0
    decay           doesnt happen
    detector        NOT
    drawing         Volume
    end_event       
    genhencut       2000 0
    genvol          0 1027 888.4 2.649e+09 100000
    kcut            2
    livetime        0 0
    model           1       2       0       1      12
    muon_desc_file  
    ngen            0.1000E+06
    norma           0 0
    nuflux          0       3       0 0.500E+00 0.000E+00 0.100E+01 0.300E+01
    physics         GENHEN 7.2-220514 181116 1138
    seed            GENHEN 3  305765867         0         0
    simul           JSirene 11012 11/17/18 07
    sourcemode      diffuse
    spectrum        -1.4
    start_run       1
    target          isoscalar
    usedetfile      false
    xlat_user       0.63297
    xparam          OFF
    zed_user        0.00 3450.00

**Note:** not all file header types are supported, so don't be surprised when you get the following warning

.. code-block:: python3

    /home/zineb/km3net/km3net/km3io/km3io/offline.py:341: UserWarning: Your file header has an unsupported format
    warnings.warn("Your file header has an unsupported format")

To explore all the available branches in our offline file: 

.. code-block:: python3

  >>> r.keys
  Events keys are:
        id
        det_id
        mc_id
        run_id
        mc_run_id
        frame_index
        trigger_mask
        trigger_counter
        overlays
        hits
        trks
        w
        w2list
        w3list
        mc_t
        mc_hits
        mc_trks
        comment
        index
        flags
        t.fSec
        t.fNanoSec
  Hits keys are:
        hits.id
        hits.dom_id
        hits.channel_id
        hits.tdc
        hits.tot
        hits.trig
        hits.pmt_id
        hits.t
        hits.a
        hits.pos.x
        hits.pos.y
        hits.pos.z
        hits.dir.x
        hits.dir.y
        hits.dir.z
        hits.pure_t
        hits.pure_a
        hits.type
        hits.origin
        hits.pattern_flags
  Tracks keys are:
        trks.fUniqueID
        trks.fBits
        trks.id
        trks.pos.x
        trks.pos.y
        trks.pos.z
        trks.dir.x
        trks.dir.y
        trks.dir.z
        trks.t
        trks.E
        trks.len
        trks.lik
        trks.type
        trks.rec_type
        trks.rec_stages
        trks.status
        trks.mother_id
        trks.fitinf
        trks.hit_ids
        trks.error_matrix
        trks.comment
  Mc hits keys are:
        mc_hits.id
        mc_hits.dom_id
        mc_hits.channel_id
        mc_hits.tdc
        mc_hits.tot
        mc_hits.trig
        mc_hits.pmt_id
        mc_hits.t
        mc_hits.a
        mc_hits.pos.x
        mc_hits.pos.y
        mc_hits.pos.z
        mc_hits.dir.x
        mc_hits.dir.y
        mc_hits.dir.z
        mc_hits.pure_t
        mc_hits.pure_a
        mc_hits.type
        mc_hits.origin
        mc_hits.pattern_flags
  Mc tracks keys are:
        mc_trks.fUniqueID
        mc_trks.fBits
        mc_trks.id
        mc_trks.pos.x
        mc_trks.pos.y
        mc_trks.pos.z
        mc_trks.dir.x
        mc_trks.dir.y
        mc_trks.dir.z
        mc_trks.t
        mc_trks.E
        mc_trks.len
        mc_trks.lik
        mc_trks.type
        mc_trks.rec_type
        mc_trks.rec_stages
        mc_trks.status
        mc_trks.mother_id
        mc_trks.fitinf
        mc_trks.hit_ids
        mc_trks.error_matrix
        mc_trks.comment

In an offline file, there are 5 main trees with data: 

* events tree
* hits tree
* tracks tree
* mc hits tree
* mc tracks tree

with km3io, these trees can be accessed with a simple tab completion: 

.. image:: https://git.km3net.de/km3py/km3io/raw/master/examples/pictures/reader.png

In the following, we will explore each tree using km3io package. 

reading events data
"""""""""""""""""""

to read data in events tree with km3io: 

.. code-block:: python3

  >>> r.events
  <OfflineEvents: 10 parsed events>

to get the total number of events in the events tree:

.. code-block:: python3

  >>> len(r.events)
  10

the branches stored in the events tree in an offline file can be easily accessed with a tab completion as seen below:

.. image:: https://git.km3net.de/km3py/km3io/raw/master/examples/pictures/events.png

to get data from the events tree, chose any branch of interest with the tab completion, the following is a non exaustive set of examples. 

to get event ids:

.. code-block:: python3

    >>> r.events.id
    <ChunkedArray [1 2 3 ... 8 9 10] at 0x7f249eeb6f10>

to get detector ids:

.. code-block:: python3

    >>> r.events.det_id
    <ChunkedArray [44 44 44 ... 44 44 44] at 0x7f249eeba050>

to get frame_index:

.. code-block:: python3

    >>> r.events.frame_index
    <ChunkedArray [182 183 202 ... 185 185 204] at 0x7f249eeba410>

to get snapshot hits:

.. code-block:: python3

    >>> r.events.hits
    <ChunkedArray [176 125 318 ... 84 255 105] at 0x7f249eebaa10>

to illustrate the strength of this data structure, we will play around with `r.events.hits` using Numpy universal `functions <https://docs.scipy.org/doc/numpy/reference/ufuncs.html>`__. 

.. code-block:: python3

    >>> import numpy as np
    >>> np.log(r.events.hits)
    <ChunkedArray [5.170483995038151 4.8283137373023015 5.762051382780177 ... 4.430816798843313 5.541263545158426 4.653960350157523] at 0x7f249b8ebb90>

to get all data from one specific event (for example event 0):

.. code-block:: python3

    >>> r.events[0]
    offline event:
          id                  :               1
          det_id              :              44
          mc_id               :               0
          run_id              :            5971
          mc_run_id           :               0
          frame_index         :             182
          trigger_mask        :              22
          trigger_counter     :               0
          overlays            :              60
          hits                :             176
          trks                :              56
          w                   :              []
          w2list              :              []
          w3list              :              []
          mc_t                :             0.0
          mc_hits             :               0
          mc_trks             :               0
          comment             :             b''
          index               :               0
          flags               :               0
          t_fSec              :      1567036818
          t_fNanoSec          :       200000000

to get a specific value from event 0, for example the number of overlays:

.. code-block:: python3

    >>> r.events[0].overlays
    60

or the number of hits: 

.. code-block:: python3

    >>> r.events[0].hits
    176


reading usr data of events
""""""""""""""""""""""""""

To access the ``usr`` data of events, use the ``.usr`` property which behaves
like a dictionary and returns ``lazyarray``, compatible to the ``numpy.array``
interface. The available keys can be accessed either as attributes or via a
dictionary lookup:

.. code-block:: python3

    >>> import km3io
    >>> f = km3io.OfflineReader("tests/samples/usr-sample.root")
    >>> f.usr
    <km3io.offline.Usr at 0x7efd53a41eb0>
    >>> print(f.usr)
    RecoQuality: [85.45957235835593 68.74744265572737 50.18704013646688]
    RecoNDF: [37.0 37.0 29.0]
    CoC: [118.6302815337638 44.33580521344907 99.93916717621543]
    ToT: [825.0 781.0 318.0]
    ChargeAbove: [176.0 278.0 53.0]
    ChargeBelow: [649.0 503.0 265.0]
    ChargeRatio: [0.21333333333333335 0.3559539052496799 0.16666666666666666]
    DeltaPosZ: [37.51967774166617 -10.280346193553832 13.67595659707355]
    FirstPartPosZ: [135.29499707179326 41.46665612378939 107.39596803432326]
    LastPartPosZ: [97.77531933012709 51.747002317343224 93.72001143724971]
    NSnapHits: [51.0 107.0 98.0]
    NTrigHits: [30.0 32.0 14.0]
    NTrigDOMs: [7.0 11.0 7.0]
    NTrigLines: [6.0 5.0 4.0]
    NSpeedVetoHits: [0.0 0.0 0.0]
    NGeometryVetoHits: [0.0 0.0 0.0]
    ClassficationScore: [0.16863382173469108 0.17944356593281038 0.08155750660727408]
    >>> f.usr.DeltaPosZ
    <ChunkedArray [37.51967774166617 -10.280346193553832 13.67595659707355] at 0x7efd54013eb0>
    >>> f.usr['RecoQuality']
    <ChunkedArray [85.45957235835593 68.74744265572737 50.18704013646688] at 0x7efd54034b50>


reading hits data
"""""""""""""""""

to read data in hits tree with km3io:

.. code-block:: python3

    >>> r.hits
    <OfflineHits: 10 parsed elements>

this shows that in our offline file, there are 10 events, with each event is associated a hits trees. 

to have access to all data in a specific branche from the hits tree, you can use the tab completion:

.. image:: https://git.km3net.de/km3py/km3io/raw/master/examples/pictures/hits.png

to get ALL the dom ids in all hits trees in our offline file:

.. code-block:: python3

    >>> r.hits.dom_id
    <ChunkedArray [[806451572 806451572 806451572 ... 809544061 809544061 809544061] [806451572 806451572 806451572 ... 809524432 809526097 809544061] [806451572 806451572 806451572 ... 809544061 809544061 809544061] ... [806451572 806455814 806465101 ... 809526097 809544058 809544061] [806455814 806455814 806455814 ... 809544061 809544061 809544061] [806455814 806455814 806455814 ... 809544058 809544058 809544061]] at 0x7f249eebac50>

to get ALL the time over threshold (tot) in all hits trees in our offline file:

.. code-block:: python3

    >>> r.hits.tot
    <ChunkedArray [[24 30 22 ... 38 26 23] [29 26 22 ... 26 28 24] [27 19 13 ... 27 24 16] ... [22 22 9 ... 27 32 27] [30 32 17 ... 30 24 29] [27 41 36 ... 29 24 28]] at 0x7f249eec9050>


if you are interested in a specific event (let's say event 0), you can access the corresponding hits tree by doing the following:

.. code-block:: python3

    >>> r[0].hits
    <OfflineHits: 176 parsed elements>

notice that now there are 176 parsed elements (as opposed to 10 elements parsed when r.hits is called). This means that in event 0 there are 176 hits! To get the dom ids from this event:

.. code-block:: python3

    >>> r[0].hits.dom_id
    array([806451572, 806451572, 806451572, 806451572, 806455814, 806455814,
       806455814, 806483369, 806483369, 806483369, 806483369, 806483369,
       806483369, 806483369, 806483369, 806483369, 806483369, 806487219,
       806487226, 806487231, 806487231, 808432835, 808435278, 808435278,
       808435278, 808435278, 808435278, 808447180, 808447180, 808447180,
       808447180, 808447180, 808447180, 808447180, 808447180, 808447186,
       808451904, 808451904, 808472265, 808472265, 808472265, 808472265,
       808472265, 808472265, 808472265, 808472265, 808488895, 808488990,
       808488990, 808488990, 808488990, 808488990, 808489014, 808489014,
       808489117, 808489117, 808489117, 808489117, 808493910, 808946818,
       808949744, 808951460, 808951460, 808951460, 808951460, 808951460,
       808956908, 808956908, 808959411, 808959411, 808959411, 808961448,
       808961448, 808961504, 808961504, 808961655, 808961655, 808961655,
       808964815, 808964815, 808964852, 808964908, 808969857, 808969857,
       808969857, 808969857, 808969857, 808972593, 808972698, 808972698,
       808972698, 808974758, 808974758, 808974758, 808974758, 808974758,
       808974758, 808974758, 808974758, 808974758, 808974758, 808974758,
       808974773, 808974773, 808974773, 808974773, 808974773, 808974972,
       808974972, 808976377, 808976377, 808976377, 808979567, 808979567,
       808979567, 808979721, 808979721, 808979721, 808979721, 808979721,
       808979721, 808979721, 808979729, 808979729, 808979729, 808981510,
       808981510, 808981510, 808981510, 808981672, 808981672, 808981672,
       808981672, 808981672, 808981672, 808981672, 808981672, 808981672,
       808981672, 808981672, 808981672, 808981672, 808981672, 808981672,
       808981672, 808981672, 808981812, 808981812, 808981812, 808981864,
       808981864, 808982005, 808982005, 808982005, 808982018, 808982018,
       808982018, 808982041, 808982041, 808982077, 808982077, 808982547,
       808982547, 808982547, 808997793, 809006037, 809524432, 809526097,
       809526097, 809544061, 809544061, 809544061, 809544061, 809544061,
       809544061, 809544061], dtype=int32

to get all data of a specific hit (let's say hit 0) from event 0:

.. code-block:: python3

    >>> r[0].hits[0]
    offline hit:
          id                  :               0
          dom_id              :       806451572
          channel_id          :               8
          tdc                 :               0
          tot                 :              24
          trig                :               1
          pmt_id              :               0
          t                   :      70104010.0
          a                   :             0.0
          pos_x               :             0.0
          pos_y               :             0.0
          pos_z               :             0.0
          dir_x               :             0.0
          dir_y               :             0.0
          dir_z               :             0.0
          pure_t              :             0.0
          pure_a              :             0.0
          type                :               0
          origin              :               0
          pattern_flags       :               0

to get a specific value from hit 0 in event 0, let's say for example the dom id:

.. code-block:: python3

    >>> r[0].hits[0].dom_id
    806451572

reading tracks data
"""""""""""""""""""

to read data in tracks tree with km3io:

.. code-block:: python3

    >>> r.tracks
    <OfflineTracks: 10 parsed elements>

this shows that in our offline file, there are 10 parsed elements (events), each event is associated with tracks data. 

to have access to all data in a specific branche from the tracks tree, you can use the tab completion:

.. image:: https://git.km3net.de/km3py/km3io/raw/master/examples/pictures/tracks.png

to get ALL the cos(zenith angle) in all tracks tree in our offline file:

.. code-block:: python3

    >>> r.tracks.dir_z
    <ChunkedArray [[-0.872885221293917 -0.872885221293917 -0.872885221293917 ... -0.6631226836266504 -0.5680647731737454 -0.5680647731737454] [-0.8351996698137462 -0.8351996698137462 -0.8351996698137462 ... -0.7485107718446855 -0.8229838871876581 -0.239315690284641] [-0.989148723802379 -0.989148723802379 -0.989148723802379 ... -0.9350162572437829 -0.88545604390297 -0.88545604390297] ... [-0.5704611045902105 -0.5704611045902105 -0.5704611045902105 ... -0.9350162572437829 -0.4647231989130516 -0.4647231989130516] [-0.9779941383490359 -0.9779941383490359 -0.9779941383490359 ... -0.88545604390297 -0.88545604390297 -0.8229838871876581] [-0.7396916780974963 -0.7396916780974963 -0.7396916780974963 ... -0.6631226836266504 -0.7485107718446855 -0.7485107718446855]] at 0x7f249eed2090>

to get ALL the tracks likelihood in our offline file:

.. code-block:: python3

    >>> r.tracks.lik
    <ChunkedArray [[294.6407542676734 294.6407542676734 294.6407542676734 ... 67.81221253265059 67.7756405143316 67.77250505700384] [96.75133289411137 96.75133289411137 96.75133289411137 ... 39.21916536442286 39.184645826013806 38.870325146341884] [560.2775306614813 560.2775306614813 560.2775306614813 ... 118.88577278801066 118.72271313687405 117.80785995187605] ... [71.03251451148226 71.03251451148226 71.03251451148226 ... 16.714140573909347 16.444395245214945 16.34639241716669] [326.440133294878 326.440133294878 326.440133294878 ... 87.79818671079849 87.75488082571873 87.74839444768625] [159.77779654216795 159.77779654216795 159.77779654216795 ... 33.8669134999348 33.821631538334984 33.77240735670646]] at 0x7f249eed2590>


if you are interested in a specific event (let's say event 0), you can access the corresponding tracks tree by doing the following:

.. code-block:: python3

    >>> r[0].tracks
    <OfflineTracks: 56 parsed elements>

notice that now there are 56 parsed elements (as opposed to 10 elements parsed when r.tracks is called). This means that in event 0 there is data about 56 possible tracks! To get the tracks likelihood from this event:

.. code-block:: python3

    >>> r[0].tracks.lik
    array([294.64075427, 294.64075427, 294.64075427, 291.64653113,
       291.27392663, 290.69031512, 289.19290546, 289.08449217,
       289.03373947, 288.19030836, 282.92343367, 282.71527118,
       282.10762402, 280.20553861, 275.93183966, 273.01809111,
       257.46433694, 220.94357656, 194.99426403, 190.47809685,
        79.95235686,  78.94389763,  78.90791169,  77.96122466,
        77.9579604 ,  76.90769883,  75.97546175,  74.91530508,
        74.9059469 ,  72.94007716,  72.90467038,  72.8629316 ,
        72.81280833,  72.80229533,  72.78899435,  71.82404165,
        71.80085542,  71.71028058,  70.91130096,  70.89150223,
        70.85845637,  70.79081796,  70.76929743,  69.80667603,
        69.64058976,  68.93085058,  68.84304037,  68.83154232,
        68.79944298,  68.79019375,  68.78581291,  68.72340328,
        67.86628937,  67.81221253,  67.77564051,  67.77250506])

to get all data of a specific track (let's say track 0) from event 0:

.. code-block:: python3

    >>> r[0].tracks[0]
    offline track:
          fUniqueID                      :                           0
          fBits                          :                    33554432
          id                             :                           1
          pos_x                          :            445.835395997812
          pos_y                          :           615.1089636184813
          pos_z                          :           125.1448339836911
          dir_x                          :          0.0368711082700674
          dir_y                          :        -0.48653048395923415
          dir_z                          :          -0.872885221293917
          t                              :           70311446.46401498
          E                              :           99.10458562488608
          len                            :                         0.0
          lik                            :           294.6407542676734
          type                           :                           0
          rec_type                       :                        4000
          rec_stages                     :                [1, 3, 5, 4]
          status                         :                           0
          mother_id                      :                          -1
          hit_ids                        :                          []
          error_matrix                   :                          []
          comment                        :                           0
          JGANDALF_BETA0_RAD             :        0.004957442219414389
          JGANDALF_BETA1_RAD             :        0.003417848024252858
          JGANDALF_CHI2                  :          -294.6407542676734
          JGANDALF_NUMBER_OF_HITS        :                       142.0
          JENERGY_ENERGY                 :           99.10458562488608
          JENERGY_CHI2                   :     1.7976931348623157e+308
          JGANDALF_LAMBDA                :      4.2409761837248484e-12
          JGANDALF_NUMBER_OF_ITERATIONS  :                        10.0
          JSTART_NPE_MIP                 :           24.88469697331908
          JSTART_NPE_MIP_TOTAL           :           55.88169412579765
          JSTART_LENGTH_METRES           :           98.89582506402911
          JVETO_NPE                      :                         0.0
          JVETO_NUMBER_OF_HITS           :                         0.0
          JENERGY_MUON_RANGE_METRES      :           344.9767431592819
          JENERGY_NOISE_LIKELIHOOD       :         -333.87773581129136
          JENERGY_NDF                    :                      1471.0
          JENERGY_NUMBER_OF_HITS         :                       101.0

to get a specific value from track 0 in event 0, let's say for example the liklihood:

.. code-block:: python3

    >>> r[0].tracks[0].lik
    294.6407542676734

to get the reconstruction parameters, first take a look at the available reconstruction keys: 

.. code-block:: python3

    >>> r.best_reco.dtype.names
    ['JGANDALF_BETA0_RAD',
     'JGANDALF_BETA1_RAD',
     'JGANDALF_CHI2',
     'JGANDALF_NUMBER_OF_HITS',
     'JENERGY_ENERGY',
     'JENERGY_CHI2',
     'JGANDALF_LAMBDA',
     'JGANDALF_NUMBER_OF_ITERATIONS',
     'JSTART_NPE_MIP',
     'JSTART_NPE_MIP_TOTAL',
     'JSTART_LENGTH_METRES',
     'JVETO_NPE',
     'JVETO_NUMBER_OF_HITS',
     'JENERGY_MUON_RANGE_METRES',
     'JENERGY_NOISE_LIKELIHOOD',
     'JENERGY_NDF',
     'JENERGY_NUMBER_OF_HITS']

the keys above can also be accessed with a tab completion:

.. image:: https://git.km3net.de/km3py/km3io/raw/master/examples/pictures/reco.png

to get a numpy `recarray <https://docs.scipy.org/doc/numpy/reference/generated/numpy.recarray.html>`__ of all fit data of the best reconstructed track:

.. code-block:: python3

    >>> r.best_reco

to get an array of a parameter of interest, let's say `'JENERGY_ENERGY'`:

.. code-block:: python3

    >>> r.best_reco['JENERGY_ENERGY']
    array([1141.87137899, 4708.16378575,  499.7243005 ,  103.54680875,
        208.6103912 , 1336.52338666,  998.87632267, 1206.54345674,
         16.28973662])

**Note**: In km3io, the best fit is defined as the track fit with the maximum reconstruction stages. When "nan" is returned, it means that the reconstruction parameter of interest is not found. for example, in the case of muon simulations: if `[1, 2]` are the reconstruction stages, then only the fit parameters corresponding to the stages `[1, 2]` are found in the Offline files, the remaining fit parameters corresponding to the stages `[3, 4, 5]` are all filled with nan.

to get a numpy recarray of the fit data of tracks with specific reconstruction stages, let's say `[1, 2, 3, 4, 5]` in the case of a muon track reconstruction: 

.. code-block:: python3

    >>> r.get_reco_fit([1, 2, 3, 4, 5])

again, to get the reconstruction parameters names: 

.. code-block:: python3

    >>> r.get_reco_fit([1, 2, 3, 4, 5]).dtype.names
    ('JGANDALF_BETA0_RAD',
     'JGANDALF_BETA1_RAD',
     'JGANDALF_CHI2',
     'JGANDALF_NUMBER_OF_HITS',
     'JENERGY_ENERGY',
     'JENERGY_CHI2',
     'JGANDALF_LAMBDA',
     'JGANDALF_NUMBER_OF_ITERATIONS',
     'JSTART_NPE_MIP',
     'JSTART_NPE_MIP_TOTAL',
     'JSTART_LENGTH_METRES',
     'JVETO_NPE',
     'JVETO_NUMBER_OF_HITS',
     'JENERGY_MUON_RANGE_METRES',
     'JENERGY_NOISE_LIKELIHOOD',
     'JENERGY_NDF',
     'JENERGY_NUMBER_OF_HITS')

to get the reconstruction data of interest, for example ['JENERGY_ENERGY']: 

.. code-block:: python3

    >>> r.get_reco_fit([1, 2, 3, 4, 5])['JENERGY_ENERGY']
    array([1141.87137899, 4708.16378575,  499.7243005 ,  103.54680875,
        208.6103912 , 1336.52338666,  998.87632267, 1206.54345674,
         16.28973662])

to get a dictionary of the corresponding hits data (for example dom ids and hits ids)

.. code-block:: python3

    >>> r.get_reco_hits([1,2,3,4,5], ["dom_id", "id"]))
    {'dom_id': <ChunkedArray [[102 102 102 ... 11517 11518 11518] [101 101 101 ... 11517 11518 11518] [101 101 102 ... 11518 11518 11518] [101 102 102 ... 11516 11517 11518] [101 101 102 ... 11517 11518 11518] [101 101 102 ... 11517 11517 11518] [101 101 102 ... 11516 11516 11517] ...] at 0x7f553ab7f3d0>,
    'id': <ChunkedArray [[0 0 0 ... 0 0 0] [0 0 0 ... 0 0 0] [0 0 0 ... 0 0 0] [0 0 0 ... 0 0 0] [0 0 0 ... 0 0 0] [0 0 0 ... 0 0 0] [0 0 0 ... 0 0 0] ...] at 0x7f553ab7f890>}

to get a dictionary of the corresponding tracks data (for example position x and y)

.. code-block:: python3

    >>> r.get_reco_tracks([1, 2, 3, 4, 5], ["pos_x", "pos_y"])

    {'pos_x': array([-647.39638136,  448.98490051,  451.12336854,  174.23666051,207.24223984, -460.75770881, -522.58197621,  324.16230509,
            -436.2319534 ]),
     'pos_y': array([-138.62068609,   77.58887593,  251.08805881, -114.60614519, 143.61947974,   86.85012087, -263.14983599, -203.14263572,
             467.75113594])}

to get a dictionary of the corresponding events data (for example det_id and run_id)

.. code-block:: python3

    >>> r.get_reco_events([1, 2, 3, 4, 5], ["run_id", "det_id"])

    {'run_id': <ChunkedArray [1 1 1 1 1 1 1 ...] at 0x7f553b5b2710>,
     'det_id': <ChunkedArray [20 20 20 20 20 20 20 ...] at 0x7f5558030750>}

**Note**: When the reconstruction stages of interest are not found in all your data file, an error is raised.


reading mc hits data
""""""""""""""""""""

to read mc hits data:

.. code-block:: python3

    >>> r.mc_hits
    <OfflineHits: 10 parsed elements>

that's it! All branches in mc hits tree can be accessed in the exact same way described in the section `reading hits data <#reading-hits-data>`__ . All data is easily accesible and if you are stuck, hit tab key to see all the available branches:

.. image:: https://git.km3net.de/km3py/km3io/raw/master/examples/pictures/mc_hits.png

reading mc tracks data
""""""""""""""""""""""

to read mc tracks data:

.. code-block:: python3

    >>> r.mc_tracks
    <OfflineTracks: 10 parsed elements>

that's it! All branches in mc tracks tree can be accessed in the exact same way described in the section `reading tracks data <#reading-tracks-data>`__ . All data is easily accesible and if you are stuck, hit tab key to see all the available branches:

.. image:: https://git.km3net.de/km3py/km3io/raw/master/examples/pictures/mc_tracks.png
