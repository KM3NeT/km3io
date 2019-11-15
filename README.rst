The km3io Python package
========================

This software provides a set of Python classes to read KM3NeT ROOT files
without having ROOT, Jpp or aanet installed. It only depends on Python 3.5+ and
the amazing uproot package and gives you access to the data via numpy arrays.

It's very easy to use and according to the uproot benchmarks, it is able to
outperform the ROOT I/O performance. To install it::

    pip install km3io

Quick intro to read Jpp files
-----------------------------

Currently only events (the ``KM3NET_EVENT`` tree) are supported but timeslices
and summaryslices will be implemented very soon.

Let's have a look at some ORCA data (``KM3NeT_00000044_00005404.root``)

To get a lazy ragged array of the events::

    >>> import km3io as ki
    >>> events = ki.JppReader("KM3NeT_00000044_00005404.root").events

That's it! Now let's have a look at the hits data::

    >>> events
    Number of events: 17023
    >>> events[23].snapshot_hits.tot
    array([28, 22, 17, 29,  5, 27, 24, 26, 21, 28, 26, 21, 26, 24, 17, 28, 23,
           29, 27, 24, 23, 26, 29, 25, 18, 28, 24, 28, 26, 20, 25, 31, 28, 23,
           26, 21, 30, 33, 27, 16, 23, 24, 19, 24, 27, 22, 23, 21, 25, 16, 28,
           22, 22, 29, 24, 29, 24, 24, 25, 25, 21, 31, 26, 28, 30, 42, 28],
          dtype=uint8)

