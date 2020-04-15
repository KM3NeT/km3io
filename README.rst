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

  * `Overview of online files <#overview-of-online-files>`__

  * `Overview of offline files <#overview-of-offline-files>`__

* `Online files reader <#online-files-reader>`__

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
`Jpp <https://git.km3net.de/common/jpp>`__ is often referred to as "a Jpp root file". Similarly, a root file created with `aanet <https://git.km3net.de/common/aanet>`__ is often referred to as "an aanet file". In km3io, an aanet root file will always be reffered to as an ``offline file``, while a Jpp ROOT file will always be referred to as a ``online file``.

km3io is a Python package that provides a set of classes (``OnlineReader`` and ``OfflineReader``) to read both online ROOT files and offline ROOT files without any dependency to aanet, Jpp or ROOT.

Data in km3io is often returned as a "lazyarray", a "jagged lazyarray" or a `Numpy <https://docs.scipy.org/doc/numpy>`__ array. A lazyarray is an array-like object that reads data on demand! In a lazyarray, only the first and the last chunks of data are read in memory. A lazyarray can be used with all Numpy's universal `functions <https://docs.scipy.org/doc/numpy/reference/ufuncs.html>`__. Here is how a lazyarray looks like:

.. code-block:: python3

    # <ChunkedArray [5971 5971 5971 ... 5971 5971 5971] at 0x7fb2341ad810>


A jagged array, is a 2+ dimentional array with different arrays lengths. In other words, a jagged array is an array of arrays of different sizes. So a jagged lazyarray is simply a jagged array of lazyarrays with different sizes. Here is how a jagged lazyarray looks like:


.. code-block:: python3

    # <JaggedArray [[102 102 102 ... 11517 11518 11518] [] [101 101 102 ... 11518 11518 11518] ... [101 101 102 ... 11516 11516 11517] [] [101 101 101 ... 11517 11517 11518]] at 0x7f74b0ef8810>


Overview of Online files
""""""""""""""""""""""""
Online files are written by the DataWriter (part of Jpp) and contain events, timeslices and summary slices.


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


Online files reader
-------------------

``km3io`` is able to read events, summary slices and timeslices. Timeslices are
currently only supported with split level of 2 or more, which means that reading
L0 timeslices is currently not working (but in progress).

Let's have a look at some ORCA data (``KM3NeT_00000044_00005404.root``)

Reading Events
""""""""""""""

To get a lazy ragged array of the events:

.. code-block:: python3

  import km3io
  f = km3io.OnlineReader("KM3NeT_00000044_00005404.root")


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
  <km3io.online.SummarySlices at 0x7effcc0e52b0>
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










