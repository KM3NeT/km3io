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


Introduction
------------

Most of km3net data is stored in root files. These root files are created using the `KM3NeT Dataformat library <https://git.km3net.de/common/km3net-dataformat>`__
A ROOT file created with
`Jpp <https://git.km3net.de/common/jpp>`__ is an "online" file and all other software usually produces "offline" files.

km3io is a Python package that provides a set of classes: ``OnlineReader``, ``OfflineReader`` and a special class to read gSeaGen files. All of these ROOT files can be read installing any other software like Jpp, aanet or ROOT.

Data in km3io is returned as ``awkward.Array`` which is an advance Numpy-like container type to store
contiguous data for high performance computations.
Such an ``awkward.Array`` supports any level of nested arrays and records which can have different lengths, in contrast to Numpy where everything has to be rectangular.

The example is shown below shows the array which contains the ``dir_z`` values
of each track of the first 4 events. The type ``4 * var * float64`` means that
it has 4 subarrays with variable lengths of type ``float64``:

.. code-block:: python3

    >>> import km3io
    >>> from km3net_testdata import data_path
    >>> f = km3io.OfflineReader(data_path("offline/numucc.root"))
    >>> f[:4].tracks.dir_z
    <Array [[0.213, 0.213, ... 0.229, 0.323]] type='4 * var * float64'>

The same concept applies to everything, including ``hits``, ``mc_hits``,
``mc_tracks``, ``t_sec`` etc.

Offline files reader
--------------------

In general an offline file has two methods to fetch data: the header and the events. Let's start with the header.

Reading the file header
"""""""""""""""""""""""

To read an offline file start with opening it with an OfflineReader:

.. code-block:: python3

  >>> import km3io
  >>> from km3net_testdata import data_path
  >>> f = km3io.OfflineReader(data_path("offline/numucc.root"))

Calling the header can be done with:

.. code-block:: python3

  >>> f.header
  <km3io.offline.Header at 0x7fcd81025990>

and provides lazy access. In offline files the header is unique and can be printed

.. code-block:: python3

  >>> print(f.header)
  MC Header:
  DAQ(livetime=394)
  PDF(i1=4, i2=58)
  can(zmin=0, zmax=1027, r=888.4)
  can_user: can_user(field_0=0.0, field_1=1027.0, field_2=888.4)
  coord_origin(x=0, y=0, z=0)
  cut_in(Emin=0, Emax=0, cosTmin=0, cosTmax=0)
  cut_nu(Emin=100, Emax=100000000.0, cosTmin=-1, cosTmax=1)
  cut_primary(Emin=0, Emax=0, cosTmin=0, cosTmax=0)
  cut_seamuon(Emin=0, Emax=0, cosTmin=0, cosTmax=0)
  decay: decay(field_0='doesnt', field_1='happen')
  detector: NOT
  drawing: Volume
  genhencut(gDir=2000, Emin=0)
  genvol(zmin=0, zmax=1027, r=888.4, volume=2649000000.0, numberOfEvents=100000)
  kcut: 2
  livetime(numberOfSeconds=0, errorOfSeconds=0)
  model(interaction=1, muon=2, scattering=0, numberOfEnergyBins=1, field_4=12)
  ngen: 100000.0
  norma(primaryFlux=0, numberOfPrimaries=0)
  nuflux: nuflux(field_0=0, field_1=3, field_2=0, field_3=0.5, field_4=0.0, field_5=1.0, field_6=3.0)
  physics(program='GENHEN', version='7.2-220514', date=181116, time=1138)
  seed(program='GENHEN', level=3, iseed=305765867, field_3=0, field_4=0)
  simul(program='JSirene', version=11012, date='11/17/18', time=7)
  sourcemode: diffuse
  spectrum(alpha=-1.4)
  start_run(run_id=1)
  target: isoscalar
  usedetfile: false
  xlat_user: 0.63297
  xparam: OFF
  zed_user: zed_user(field_0=0.0, field_1=3450.0)

To read the values in the header one can call them directly:

.. code-block:: python3

  >>> f.header.DAQ.livetime
  394
  >>> f.header.cut_nu.Emin
  100
  >>> f.header.genvol.numberOfEvents
  100000


Reading events
""""""""""""""

To start reading events call the events method on the file:

.. code-block:: python3

  >>> f
  OfflineReader (10 events)
  >>> f.keys()
  {'comment', 'det_id', 'flags', 'frame_index', 'hits', 'id', 'index',
  'mc_hits', 'mc_id', 'mc_run_id', 'mc_t', 'mc_tracks', 'mc_trks',
  'n_hits', 'n_mc_hits', 'n_mc_tracks', 'n_mc_trks', 'n_tracks',
  'n_trks', 'overlays', 'run_id', 't_ns', 't_sec', 'tracks',
  'trigger_counter', 'trigger_mask', 'trks', 'usr', 'usr_names',
  'w', 'w2list', 'w3list'}

Like the online reader lazy access is used. Using <TAB> completion gives an overview of available data. Alternatively the method `keys` can be used on events and it's data members containing a structure to see what is available for reading.

Reading the reconstructed values like energy and direction of an event can be done with:

.. code-block:: python3

  >>> f.events.tracks.E
  <Array [[117, 117, 0, 0, 0, ... 0, 0, 0, 0, 0]] type='10 * var * float64'>

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



