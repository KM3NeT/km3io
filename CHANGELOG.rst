Unreleased changes
------------------

Version 0
---------
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
