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

* `Daq files reader <#daq-files-reader>`__

* `Offline files reader <#offline-file-reader>`__

Introduction
------------

Most of km3net data is stored in root files. These root files are either created with `Jpp <https://git.km3net.de/common/jpp>`__ or `aanet <https://git.km3net.de/common/aanet>`__ software. A root file created with 
`Jpp <https://git.km3net.de/common/jpp>`__ is often referred to as "a Jpp root file". Similarly, a root file created with `aanet <https://git.km3net.de/common/aanet>`__ is often referred to as "an aanet file". In km3io, an aanet root file will always be reffered to as an ``offline file``, while a Jpp root file will always be referred to as a ``daq file``.

km3io is a Python package that provides a set of classes (``DaqReader`` and ``OfflineReader``) to read both daq root files and offline root files without any dependency to aanet, Jpp or ROOT. 

Data in km3io is often returned as a "lazyarray", a "jagged lazyarray", "a jagged array" or a Numpy array. A lazyarray is an array-like object that reads data on demand! In a lazyarray, only the first and the last chunks of data are read in memory. A lazyarray can be used with all Numpy's universal `functions <https://docs.scipy.org/doc/numpy/referenceufuncs.html>`__. Here is how a lazyarray looks like:

.. code-block:: python3

    # <ChunkedArray [5971 5971 5971 ... 5971 5971 5971] at 0x7fb2341ad810>


A jagged array, is a 2+ dimentional array with different arrays lengths. In other words, a jagged array is an array of arrays of different sizes. So a jagged lazyarray is simply a jagged array of lazyarrays with different sizes. Here is how a jagged lazyarray looks like:


.. code-block:: python3

    # <JaggedArray [[102 102 102 ... 11517 11518 11518] [] [101 101 102 ... 11518 11518 11518] ... [101 101 102 ... 11516 11516 11517] [] [101 101 101 ... 11517 11517 11518]] at 0x7f74b0ef8810>


Overview of daq files
"""""""""""""""""""""
# info needed here

Overview of offline files
"""""""""""""""""""""""""

# info needed here

Daq files reader
----------------

# an update is needed here?

Currently only events (the ``KM3NET_EVENT`` tree) are supported but timeslices and summaryslices will be implemented very soon.

Let's have a look at some ORCA data (``KM3NeT_00000044_00005404.root``)

To get a lazy ragged array of the events:

.. code-block:: python3

  import km3io as ki
  events = ki.JppReader("KM3NeT_00000044_00005404.root").events


That's it! Now let's have a look at the hits data:

.. code-block:: python3

  events
  # Number of events: 17023
  events[23].snapshot_hits.tot
  # array([28, 22, 17, 29,  5, 27, 24, 26, 21, 28, 26, 21, 26, 24, 17, 28, 23,29, 27, 24, 23, 26, 29, 25, 18, 28, 24, 28, 26, 20, 25, 31, 28, 23, 26, 21, 30, 33, 27, 16, 23, 24, 19, 24, 27, 22, 23, 21, 25, 16, 28, 22, 22, 29, 24, 29, 24, 24, 25, 25, 21, 31, 26, 28, 30, 42, 28], dtype=uint8)


Offline files reader
--------------------

Let's have a look at some muons data from ORCA 4 lines simulations - run id 5971 (``datav6.0test.jchain.aanet.00005971.root``). 

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
