Unreleased changes
------------------


Version 1
---------
1.2.0 / 2024-06-24
~~~~~~~~~~~~~~~~~~
* Removed online format support (online events, timeslices and summary slices) in favour of
  the `KM3io.jl <https://git.km3net.de/common/KM3io.jl>`__` Julia Package.
* uproot 5 and awkward 2 are now required
* Python 3.7+ required

1.1.0 / 2024-03-14
~~~~~~~~~~~~~~~~~~
* A few astro helpers were added: azimuth(), zenith(), phi(), theta(), ...

1.0.2 / 2023-10-08
~~~~~~~~~~~~~~~~~~
* Deprecation fixes

1.0.1 / 2023-06-15
~~~~~~~~~~~~~~~~~~
* Minor changes

1.0.0 / 2023-02-27
~~~~~~~~~~~~~~~~~~
* API stabilised and v1 is now LTS
* ``gSeaGen`` reader removed, only supported until v0.29.2

Version 0
---------

0.29.2 / 2022-12-21
~~~~~~~~~~~~~~~~~~~
* Hotfix for AwkwardArray 2.0 incompatibility, now restricted to
  be <2.0

0.29.1 / 2022-12-01
~~~~~~~~~~~~~~~~~~~
* Added ``codemeta.json`` to the MANIFEST

0.29.0 / 2022-11-07
~~~~~~~~~~~~~~~~~~~
* Update km3net-definitions to 3.0.0

0.28.0 / 2022-11-02
~~~~~~~~~~~~~~~~~~~
* Update km3net-definitions to 2.2.0-16-gbef370c

0.27.3 / 2022-10-20
~~~~~~~~~~~~~~~~~~~
* Fixed ``km3io.tools.fitinf()`` which always returned the 0th element

0.27.2 / 2022-10-04
~~~~~~~~~~~~~~~~~~~
* Added dockerisation

0.27.1 / 2022-09-20
~~~~~~~~~~~~~~~~~~~
* Fixes the issue where files procued with newer Jpp v17+ versions
  errored due to a `header_uuid[16]` field

0.27.0 / 2022-07-20
~~~~~~~~~~~~~~~~~~~
* Adds the TimeConverter class to ``src/km3io/tools.py``
* Update km3net-dataformat requirement to version 0.3.6 or higher
* Update Black requirement to version 22.3.0 or higher, to prevent ``ImportError: cannot import name '_unicodefun' from 'click'``
* Remove ``requirements`` folder (all requirements are now configured in ``setup.cfg``)

0.26.1 / 2022-07-06
~~~~~~~~~~~~~~~~~~~
* The warning from OpenMP/Numba is now silenced

0.26.0 / 2022-06-27
~~~~~~~~~~~~~~~~~~~
* Added ``km3io.tools.is_nanobeacon()`` to check if the nanobeacon trigger bit is set
* Added ``km3io.tools.get_w2list_idx()`` to get the w2list index according to the
  simulation program
  
0.25.2 / 2022-03-27
~~~~~~~~~~~~~~~~~~~
* Fixes the version

0.25.1 / 2022-03-24
~~~~~~~~~~~~~~~~~~~
* the ``.counter`` field for ``mc_trks/mc_tracks`` is now accessible

0.25.0 / 2022-03-14
~~~~~~~~~~~~~~~~~~~
* uproot 4.2.2+ required, which fixes a regression problem when reading doubly nested
  structures
* Added a new, high-performance Summaryslice reader ``km3io.online.SummarysliceReader``
* The old ``km3io.OnlineReader.summarslices`` is now using the new ``SummarysliceReader``
  which has a slightly different API (but at least an order of magnitude better
  performance and much nicer high-level API thanks to AwkwardArrays)

0.24.1 / 2021-11-05
~~~~~~~~~~~~~~~~~~~
* The ``km3io.tools.is_bit_set()`` and all the related trigger mask checkers
  (``is_3dmuon()``...) are now compatible with Numba

0.24.0 / 2021-11-02
~~~~~~~~~~~~~~~~~~~
* The field ``.a`` (amplitude) for Hits is now accessible

0.23.1 / 2021-09-28
~~~~~~~~~~~~~~~~~~~
* KM3NeT Dataformat definition updated to 2.1.0+

0.23.0 / 2021-07-03
~~~~~~~~~~~~~~~~~~~
* ``km3io.acoustics`` was added which provides ``RawAcousticsReader`` to
  read -- wait for it -- raw acoustics data

0.22.0 / 2021-06-15
~~~~~~~~~~~~~~~~~~~
* Added ``km3io.tools.is_bit_set()`` along with some special methods to check
  if a given ``trigger_mask`` (of an event or a hit) has a specific trigger
  bit set, via ``km3io.tools.is_3dmuon``, ``km3io.tools.is_3dshower`` and
  ``km3io.tools.is_mxshower``

0.21.0 / 2021-04-08
~~~~~~~~~~~~~~~~~~~
* ``km3net-dataformat`` updated to v2.0.0-9-gbae3720
* mother ID and status are now read out for MC tracks

0.20.0 / 2021-02-18
~~~~~~~~~~~~~~~~~~~
* The fields ``.tdc``, ``.pos_{xyz}`` and ``.dir_{xyz}`` in ``.hits`` are
  now read by default.

0.19.6 / 2021-02-01
~~~~~~~~~~~~~~~~~~~
* Improved header readout

0.19.5 / 2021-02-01
~~~~~~~~~~~~~~~~~~~
* Adds access to ``mc_event_time``

0.19.4 / 2021-02-01
~~~~~~~~~~~~~~~~~~~
* Fixed parsing error when a MC header contains invalid attribute names.

0.19.3 / 2020-12-17
~~~~~~~~~~~~~~~~~~~
* Added ``Branch.arrays()`` for high-level access of ``uproot.TBranch.arrays()``

0.19.2 / 2020-12-15
~~~~~~~~~~~~~~~~~~~
* Suppress FutureWarnings from uproot3

0.19.1 / 2020-12-11
~~~~~~~~~~~~~~~~~~~
* Minor hotfixes and cosmetics

0.19.0 / 2020-12-11
~~~~~~~~~~~~~~~~~~~
* Major update, coming closer to v1.0
* Now everything but the online-file access is based on uproot4 and awkward1
* Contact us if you encounter any problem after upgrading!

0.18.1 / 2020-12-04
~~~~~~~~~~~~~~~~~~~
* Fixed imports due to the rename of uproot to uproot3, uproot4 to uproot,
  awkward to awkward0 and awkward1 to awkward
* Notice: the ``best_track*()`` functions are currently broken due to changes in
  awkward which has not been fixed yet

0.18.0 / 2020-11-12
~~~~~~~~~~~~~~~~~~~
* A new tool ``km3io.tools.is_cc()`` has been added which can be used to
  check if the events are of type CC 

0.17.1 / 2020-10-19
~~~~~~~~~~~~~~~~~~~
* Requires ``awkward1>=0.3.1`` from now on (fixes an array-shape mismatch bug)

0.17.0 / 2020-10-13
~~~~~~~~~~~~~~~~~~~
* Final ;) ``km3io.tools.best_track`` implementation which provides
  many different ways to chose the one and only "best track".
* Similar to ``km3net-dataformat/scripts/reconstruction.hh``, the
  following functions can be used to retrieve the best track according
  to the "standard definitions": ``km3io.tools.best_jmuon``, ``best_jshower``,
  ``best_dusjshower`` and ``best_aashower``

0.16.2 / 2020-10-07
~~~~~~~~~~~~~~~~~~~
* Adds ``.uuid`` attributes to ``OfflineReader`` and ``OnlineReader``

0.16.1 / 2020-09-30
~~~~~~~~~~~~~~~~~~~
* Fixed a bug in ``Branch.is_single``

0.16.0 / 2020-09-30
~~~~~~~~~~~~~~~~~~~
* Fixed the inconsistency of ``len()`` of mapped branches
  See https://git.km3net.de/km3py/km3io/-/issues/39#note_18429
* Introduced ``Branch.is_single`` to check if a single branch is
  selected

0.15.5 / 2020-09-30
~~~~~~~~~~~~~~~~~~~
* Fixed a tiny bug in ``km3io.tools.best_track``

0.15.4 / 2020-09-30
~~~~~~~~~~~~~~~~~~~
* Improved ``km3io.tools.best_track`` which now works nicely
  when passing events and improves the error reporting
* ``tracks.usr`` is now hidden (again) from the user

0.15.3 / 2020-09-25
~~~~~~~~~~~~~~~~~~~
* Updated KM3NeT definitions to v1.2.4

0.15.2 / 2020-09-23
~~~~~~~~~~~~~~~~~~~
* Fixed a bug where the last bit of HRV or FIFO were incorrectly
  masked when using ``km3io.online.get_channel_flags``

0.15.1 / 2020-07-15
~~~~~~~~~~~~~~~~~~~
* Added wheel packages for faster installation

0.15.0 / 2020-05-22
~~~~~~~~~~~~~~~~~~~
* Added reverse maps for index lookup of definitions
  ``km3io.definitions.fitparameters_idx`` etc.

0.14.2 / 2020-05-21
~~~~~~~~~~~~~~~~~~~
* Improved caching for awkward arrays in pumps

0.14.1 / 2020-05-21
~~~~~~~~~~~~~~~~~~~
* Improved caching for awkward arrays

0.14.0 / 2020-04-29
~~~~~~~~~~~~~~~~~~~
* ``events.mc_tracks.usr`` and ``events.mc_tracks.usr_names`` are now
  correctly parsed

0.13.0 / 2020-04-26
~~~~~~~~~~~~~~~~~~~
* ``km3io.tools.unique`` and ``km3io.tools.uniquecount`` were added to help
  working with unique elements (e.g. DOM IDs or channel IDs)
* Internal restructuring of ``.tools``, ROOT related stuff is moved
  to ``.rootio``

0.12.0 / 2020-04-26
~~~~~~~~~~~~~~~~~~~
* Added ``.close()`` to the Offline and Online reader classes
* The Offline and Online reader classes now support context managers
  (``with km3io.OfflineReader(filename) as r: ...``)

0.11.0 / 2020-04-19
~~~~~~~~~~~~~~~~~~~
* DAQ was renamed to online
* Several improviements, bugfixes etc.

0.10.0 / 2020-04-01
~~~~~~~~~~~~~~~~~~~
* The offline I/O has been refactored and now supports slicing à la numpy

0.9.1 / 2020-03-29
~~~~~~~~~~~~~~~~~~
* Added support for gSeaGen files

0.9.0 / 2020-03-03
~~~~~~~~~~~~~~~~~~
* Added support for the ``usr`` field of events

0.8.3 / 2020-02-25
~~~~~~~~~~~~~~~~~~
* The times of snapshot and triggered hits were parsed as big endian (standard)
  ROOT endianness, however, Jpp stores that as little endian with a custom
  streamer. This is now fixed...

0.8.2 / 2020-02-14
~~~~~~~~~~~~~~~~~~
* minor fixes

0.8.1 / 2020-02-10
~~~~~~~~~~~~~~~~~~
* update of reco data from offline files
* Documentation on how to read DAQ data

0.8.0 / 2020-01-23
~~~~~~~~~~~~~~~~~~
* Offline file headers are now accessible

0.7.0 / 2020-01-23
~~~~~~~~~~~~~~~~~~
* Reading of summary slice status information is now supported

0.6.3 / 2020-01-09
~~~~~~~~~~~~~~~~~~
* Bugfixes

0.6.2 / 2019-12-22
~~~~~~~~~~~~~~~~~~
* Fixes slicing of ``OfflineTracks``

0.6.1 / 2019-12-21
~~~~~~~~~~~~~~~~~~
* Minor cleanup

0.6.0 / 2019-12-21
~~~~~~~~~~~~~~~~~~
* Jpp things were renamed to DAQ things (;
* Reading of summary slices is done!

0.5.1 / 2019-12-18
~~~~~~~~~~~~~~~~~~
* Cosmetics

0.5.0 / 2019-12-16
~~~~~~~~~~~~~~~~~~
* Massive update of the aanet data format reader

0.4.0 / 2019-11-22
~~~~~~~~~~~~~~~~~~~
* First timeslice frame readout prototype

0.3.0 / 2019-11-19
~~~~~~~~~~~~~~~~~~~
* Preliminary Jpp timeslice reader prototype
* Updated ``AanetReader``
* Updated docs

0.2.1 / 2019-11-15
~~~~~~~~~~~~~~~~~~~
* Updated docs

0.2.0 / 2019-11-15
~~~~~~~~~~~~~~~~~~~
* ``JppReader`` added, which is able to read events!

0.1.0 / 2019-11-15
~~~~~~~~~~~~~~~~~~~
* First release
* Prototype implementation of the ``AanetReader``
