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

Currently, only one Aanet event file can be read. The next version of km3io
will be able to read multiple Aanet files (from the same simulation!). Data
is always returned as a "lazyarray". A lazyarray is an array-like object that
reads data on demand. Here, only the first and last chunks of data are read in
memory, and not all data in the array. The output can be used with all Numpy's
universal functions <https://docs.scipy.org/doc/numpy/reference/ufuncs.html>.

Let's have a look at some events data from ORCA 4 lines simulations - run id
5971 (``datav6.0test.jchain.aanet.00005971.root``)

To get a lazy ragged array of all data::

    >>> import km3io as ki
    >>> reader = ki.AanetReader('datav6.0test.jchain.aanet.00005971.root')

That's it! Now let's take a look at all the available branches in our file::

    >>> reader
    Number of events: 145028
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

Now that you have seen all the available branches, you can choose any key from
the above (key refers to a branch name) and display the corresponding data. For
example, we will check that we are indeed reading data from the run 5971::

    >>> reader['run_id']
    <ChunkedArray [5971 5971 5971 ... 5971 5971 5971] at 0x7fb2341ad810>

Let's look at the number of hits and tracks in the event number 5::

    >>> reader[5]['hits']
    60
    >>> reader[5]['trks']
    56

So event 5 has exactly 60 hits and 56 tracks. Let's explore in more details
hits and tracks data in event 5::

    >>> reader['hits.dom_id'][5]
    array([806455814, 806487219, 806487219, 806487219, 806487226, 808432835,
       808432835, 808432835, 808432835, 808432835, 808432835, 808432835,
       808451904, 808451904, 808451907, 808451907, 808469129, 808469129,
       808469129, 808493910, 808949744, 808949744, 808951460, 808951460,
       808956908, 808961655, 808964908, 808969848, 808969857, 808972593,
       808972593, 808972598, 808972598, 808972698, 808972698, 808974758,
       808974811, 808976377, 808981510, 808981523, 808981812, 808982005,
       808982005, 808982018, 808982077, 808982077, 808982547, 809007627,
       809521500, 809521500, 809521500, 809524432, 809526097, 809526097,
       809526097, 809526097, 809526097, 809526097, 809526097, 809544058],
      dtype=int32)

One can access the dom_id for the first hit in event 5 as follows:: 

    >>> reader['hits.dom_id'][5][0]
    806455814

Now let's read tracks data in event 5::

    >>> reader['trks.dir.z'][5]
    array([-0.60246049, -0.60246049, -0.60246049, -0.51420541, -0.5475772 ,
       -0.5772408 , -0.56068238, -0.64907684, -0.67781799, -0.66565114,
       -0.63014839, -0.64566464, -0.62691012, -0.58465493, -0.59287533,
       -0.63655091, -0.63771247, -0.73446841, -0.7456636 , -0.70941246,
       -0.66312268, -0.66312268, -0.56806477, -0.56806477, -0.66312268,
       -0.66312268, -0.74851077, -0.74851077, -0.66312268, -0.74851077,
       -0.56806477, -0.74851077, -0.66312268, -0.74851077, -0.56806477,
       -0.66312268, -0.56806477, -0.66312268, -0.56806477, -0.56806477,
       -0.66312268, -0.74851077, -0.66312268, -0.93501626, -0.56806477,
       -0.74851077, -0.66312268, -0.56806477, -0.82298389, -0.74851077,
       -0.66312268, -0.56806477, -0.82298389, -0.56806477, -0.66312268,
       -0.97094183])

One can access the 'trks.dir.z' for the first track in event 5 as follows::

    >>> reader['trks.dir.z'][5][0]
    -0.60246049
