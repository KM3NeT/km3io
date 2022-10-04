The km3io Python package
========================

.. image:: https://git.km3net.de/km3py/km3io/badges/master/pipeline.svg
    :target: https://git.km3net.de/km3py/km3io/pipelines

.. image:: https://git.km3net.de/km3py/km3io/badges/master/coverage.svg
    :target: https://km3py.pages.km3net.de/km3io/coverage

.. image:: https://git.km3net.de/examples/km3badges/-/raw/master/docs-latest-brightgreen.svg
    :target: https://km3py.pages.km3net.de/km3io

This software provides a set of Python classes to read KM3NeT ROOT files
without having ROOT, Jpp or aanet installed. It only depends on Python 3.5+ and the amazing `uproot <https://github.com/scikit-hep/uproot>`__ package and gives you access to the data via `numpy <https://www.numpy.org>`__ and `awkward <https://awkward-array.readthedocs.io>`__ arrays.

It's very easy to use and according to the `uproot <https://github.com/scikit-hep/uproot>`__ benchmarks, it is able to outperform the original ROOT I/O performance. 

**Note:** Beware that this package is in the development phase, so the API will change until version ``1.0.0`` is released!

Installation
============

Install km3io using pip::

    pip install km3io 

or conda::

    conda install km3io

To get the latest (stable) development release::

    pip install git+https://git.km3net.de/km3py/km3io.git

Docker::

    docker run -it docker.km3net.de/km3io

Singularity::

    wget https://sftp.km3net.de/singularity/km3io_v0.27.2.sif  # pick the version you like
    singularity shell km3io_v0.27.2.sif

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

The same concept applies to all other branches, including ``hits``, ``mc_hits``,
``mc_tracks``, ``t_sec`` etc.

Offline files reader
--------------------

In general an offline file has two attributes to access data: the header and the events. Let's start with the header.

Reading the file header
"""""""""""""""""""""""

To read an offline file start with opening it with the ``OfflineReader``:

.. code-block:: python3

  >>> import km3io
  >>> from km3net_testdata import data_path
  >>> f = km3io.OfflineReader(data_path("offline/numucc.root"))

Accessing is as easy as typing:

.. code-block:: python3

  >>> f.header
  <km3io.offline.Header at 0x7fcd81025990>

Printing it will give an overview of the structure:

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

To read the values in the header one can call them directly, as the structures
are simple ``namedtuple``-like objects:

.. code-block:: python3

  >>> f.header.DAQ.livetime
  394
  >>> f.header.cut_nu.Emin
  100
  >>> f.header.genvol.numberOfEvents
  100000


Reading offline events
""""""""""""""""""""""

Events are at the top level of an offline file, so that each branch of an event
is directly accessible at the ``OfflineReader`` instance. The ``.keys()`` method
can be used to list the available attributes. Notice that some of them are aliases
for backwards compatibility (like ``mc_tracks`` and ``mc_trks``). Another
backwards compatibility feature is the ``f.events`` attribute which is simply
mapping everything to ``f``, so that ``f.events.mc_tracks`` is the same as
``f.mc_tracks``.

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
  >>> f.tracks
  <Branch [10] path='trks'>
  >>> f.events.tracks
  <Branch [10] path='trks'>

The ``[10]`` denotes that there are ``10`` events available, each containing a sub-array of ``tracks``.

Using <TAB> completion gives an overview of available data. Alternatively the attribute `fields`
can be used on event-branches and to see what is available for reading.

.. code-block:: python3

  >>> f.tracks.fields
  ['id',
  'pos_x',
  'pos_y',
  'pos_z',
  'dir_x',
  'dir_y',
  'dir_z',
  't',
  'E',
  'len',
  'lik',
  'rec_type',
  'rec_stages',
  'fitinf']


Reading the reconstructed values like energy and direction of an event can be done with:

.. code-block:: python3

  >>> f.events.tracks.E
  <Array [[117, 117, 0, 0, 0, ... 0, 0, 0, 0, 0]] type='10 * var * float64'>

The ``Array`` in this case is an `awkward <https://awkward-array.readthedocs.io>`__ array with the data type
``10 * var * float64`` which means that there are ``10`` sub-arrays with ``var``iable lengths of type ``float64``.
Awkward arrays allow high-performance access to arrays which are not rectangular (in contrast to ``numpy``).
Read the documention of AwkwardArray to learn how to work with these structures efficiently. One example
to retrieve the energy of the very first reconstructed track for the first three events is:

.. code-block:: python3

  >>> f.events.tracks.E[:3, 0]
  <Array [117, 4.4e+03, 8.37] type='3 * float64'>

Online files reader
-------------------

``km3io`` is able to read events, summary slices and timeslices. Timeslices are
currently only supported with split level of 2 or more, which means that reading
L0 timeslices is not working at the moment (but is in progress).

Let's have a look at some online data.

Reading online events
"""""""""""""""""""""

Now we use the ``OnlineReader`` to create our file object.

.. code-block:: python3

  import km3io
  f = km3io.OnlineReader(data_path("online/km3net_online.root"))


That's it, we created an object which gives access to all the events, but the
relevant data is still not loaded into the memory (lazy access)!
The structure is different compared to the ``OfflineReader``
because online files contain additional branches at the top level
(summaryslices and timeslices).

.. code-block:: python3

  >>> f.events
  Number of events: 3
  >>> f.events.snapshot_hits[1].tot[:10]
  array([27, 24, 21, 17, 22, 15, 24, 30, 19, 15], dtype=uint8)
  >>> f.events.triggered_hits[1].channel_id[:10]
  array([ 2,  3, 16, 22, 23,  0,  2,  3,  4,  5], dtype=uint8)

The resulting arrays are numpy arrays. The indexing convention is: the first indexing
corresponds to the event, the second to the branch and consecutive ones to the
optional dimensions of the arrays. In the last step we accessed the PMT channel IDs
of the first 10 hits of the second event.

Reading SummarySlices
"""""""""""""""""""""

The following example shows how to access summary slices. The summary slices are
returned in chunks to be more efficient with the I/O. The default chunk-size is
1000. In the example file we only have three summaryslices, so there is only a single
chunk. The first index passed to the summaryslices reader is corresponding to the
chunk and the second to the index of the summaryslice in that chunk.

.. code-block:: python3

  >>> f.summaryslices
  <SummarysliceReader 3 items, step_size=1000 (1 chunk)>
  >>> f.summaryslices[0]
  SummarysliceChunk(headers=<Array [{' cnt': 671088704, ... ] type='3 * {" cnt": uint32, " vers": uint16, " ...'>, slices=<Array [[{dom_id: 806451572, ... ch30: 48}]] type='3 * var * {"dom_id": int32, "...'>)
  >>> f.summaryslices[0].headers
  <Array [{' cnt': 671088704, ... ] type='3 * {" cnt": uint32, " vers": uint16, " ...'>
  >>> f.summaryslices[0].slices[2]
  <Array [{dom_id: 806451572, ... ch30: 48}] type='68 * {"dom_id": int32, "dq_stat...'>
  >>> f.summaryslices[0].slices[2].dom_id
  <Array [806451572, 806455814, ... 809544061] type='68 * int32'>
  >>> f.summaryslices[0].slices[2].ch23
  <Array [48, 43, 46, 54, 83, ... 51, 51, 52, 50] type='68 * uint8'>

Reading Timeslices
""""""""""""""""""

Timeslices are split into different streams since 2017 and ``km3io`` currently
supports everything except L0, i.e. L1, L2 and SN streams. The API is
work-in-progress and will be improved in future, however, all the data is
already accessible (although in ugly ways ;-)

To access the timeslice data, you need to specify which timeslice stream
to read:

.. code-block:: python3

  >>> f.timeslices
  Available timeslice streams: SN, L1
  >>> f.timeslices.stream("L1", 0).frames
  {806451572: <Table [<Row 0> <Row 1> <Row 2> ... <Row 981> <Row 982> <Row 983>] at 0x00014c167340>,
  806455814: <Table [<Row 984> <Row 985> <Row 986> ... <Row 1985> <Row 1986> <Row 1987>] at 0x00014c5f4760>,
  806465101: <Table [<Row 1988> <Row 1989> <Row 1990> ... <Row 2236> <Row 2237> <Row 2238>] at 0x00014c5f45e0>,
  806483369: <Table [<Row 2239> <Row 2240> <Row 2241> ... <Row 2965> <Row 2966> <Row 2967>] at 0x00014c12b910>,
  ...
  809544061: <Table [<Row 48517> <Row 48518> <Row 48519> ... <Row 49240> <Row 49241> <Row 49242>] at 0x00014ca57100>}

The frames are represented by a dictionary where the key is the ``DOM ID`` and
the value an awkward array of hits, with the usual fields to access the PMT
channel, time and ToT:

.. code-block:: python3

   >>> f.timeslices.stream("L1", 0).frames[809524432].dtype
   dtype([('pmt', 'u1'), ('tdc', '<u4'), ('tot', 'u1')])
   >>> f.timeslices.stream("L1", 0).frames[809524432].tot
  array([25, 27, 28, ..., 29, 22, 28], dtype=uint8)



