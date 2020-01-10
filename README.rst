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

* `Offline files reader <#offline-file-reader>`__

  * `reading events data <#reading-events-data>`__

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


Overview of daq files
"""""""""""""""""""""
# info needed here

Overview of offline files
"""""""""""""""""""""""""

# info needed here

DAQ files reader
----------------

# an update is needed here?

Currently only events (the ``KM3NET_EVENT`` tree) are supported but timeslices and summaryslices will be implemented very soon.

Let's have a look at some ORCA data (``KM3NeT_00000044_00005404.root``)

To get a lazy ragged array of the events:

.. code-block:: python3

  import km3io as ki
  events = ki.DAQReader("KM3NeT_00000044_00005404.root").events


That's it! Now let's have a look at the hits data:

.. code-block:: python3

  >>> events
  Number of events: 17023
  >>> events[23].snapshot_hits.tot
  array([28, 22, 17, 29,  5, 27, 24, 26, 21, 28, 26, 21, 26, 24, 17, 28, 23,29, 27, 24, 23, 26, 29, 25, 18, 28, 24, 28, 26, 20, 25, 31, 28, 23, 26, 21, 30, 33, 27, 16, 23, 24, 19, 24, 27, 22, 23, 21, 25, 16, 28, 22, 22, 29, 24, 29, 24, 24, 25, 25, 21, 31, 26, 28, 30, 42, 28], dtype=uint8)


Offline files reader
--------------------

Let's have a look at some muons data from ORCA 4 lines simulations - run id 5971 (``datav6.0test.jchain.aanet.00005971.root``). 

**Note:** this file was cropped to 10 events only, so don't be surprised in this tutorial if you see few events in the file.

First, let's read our file:

.. code-block:: python3

  >>> import km3io as ki
  >>> file = 'datav6.0test.jchain.aanet.00005971.root'
  >>> r = ki.OfflineReader(file)
  <km3io.aanet.OfflineReader at 0x7f24cc2bd550>

and that's it! Note that `file` can be either an str of your file path, or a path-like object. 

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

    >>>r[0].hits[0]
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

    >>>r[0].hits[0].dom_id
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

    >>>r[0].tracks[0]
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

    >>>r[0].tracks[0].lik
    294.6407542676734


reading mc hits data
""""""""""""""""""""

to read mc hits data:

.. code-block:: python3

    >>>r.mc_hits
    <OfflineHits: 10 parsed elements>

that's it! All branches in mc hits tree can be accessed in the exact same way described in the section `reading hits data <#reading-hits-data>`__ . All data is easily accesible and if you are stuck, hit tab key to see all the available branches:

.. image:: https://git.km3net.de/km3py/km3io/raw/master/examples/pictures/mc_hits.png

reading mc tracks data
""""""""""""""""""""""

to read mc tracks data:

.. code-block:: python3

    >>>r.mc_tracks
    <OfflineTracks: 10 parsed elements>

that's it! All branches in mc tracks tree can be accessed in the exact same way described in the section `reading tracks data <#reading-tracks-data>`__ . All data is easily accesible and if you are stuck, hit tab key to see all the available branches:

.. image:: https://git.km3net.de/km3py/km3io/raw/master/examples/pictures/mc_tracks.png
