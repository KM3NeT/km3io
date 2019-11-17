The km3io Python package
========================

.. image:: https://git.km3net.de/km3py/km3io/badges/master/build.svg
    :target: https://git.km3net.de/km3py/km3io/pipelines

.. image:: https://git.km3net.de/km3py/km3io/badges/master/coverage.svg
    :target: https://km3py.pages.km3net.de/km3io/coverage

.. image:: https://api.codacy.com/project/badge/Grade/0660338483874475ba04f324de2123ec
    :target: https://www.codacy.com/manual/tamasgal/km3io?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=KM3NeT/km3io&amp;utm_campaign=Badge_Grade

.. image:: https://examples.pages.km3net.de/km3badges/docs-latest-brightgreen.svg
    :target: https://km3py.pages.km3net.de/km3io

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

Quick intro to read Aanet files
-------------------------------

Currently, only one Aanet event file can be read. The next version of km3io will be able to read multiple Aanet files (from the same simulation!). 

Let's have a look at some events data from ORCA 4 lines simulations - run id 5971 (``datav6.0test.jchain.aanet.00005971.root``)

To get a lazy ragged array of all data::

    >>> import km3io as ki
    >>> reader = ki.AanetReader('datav6.0test.jchain.aanet.00005971.root')

That's it! Now let's take a look at all the available branches in our file::

    >>> reader
    Number of events: 10
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
      trks.usr_data
      trks.usr_names
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
