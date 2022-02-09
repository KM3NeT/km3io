"""
Reading Online Data
===================

The following example shows how to access hits in a ROOT file which is coming
from the detector and written by the `JDataWriter` application.

Such a file is usually called "KM3NET_00000001_00000002.root", where the first
number is the detector ID and the second the run number.
"""
import km3io as ki
from km3net_testdata import data_path

#####################################################
# Accessing the event tree
# ------------------------
# Just pass a filename to the reader class and get access to the event tree
# with:


f = ki.OnlineReader(data_path("online/km3net_online.root"))

#####################################################
# Note that only some meta information is read into memory.
#
# Printing it will simply tell you how many events it has found. Again, nothing
# else is read yet:

print(f.events)

#####################################################
# Now let's look at the hits data:

print(f.events[0].snapshot_hits.tot)

#####################################################
# the resulting arrays are numpy arrays.

#####################################################
# Reading SummarySlices
# ---------------------
# The following example shows how to access summary slices, in particular the DOM
# IDs of the slice with the index 0.
# The current implementation of the summaryslice I/O uses a chunked reading for
# better performance, which means that when you iterate through the `.slices`,
# you'll get chunks of summaryslices in each iteration instead of a single one.
#
# In the example below, we simulate a single iteration by using the `break`
# keyword and then use the data which has been "pulled out" of the ROOT file.


for chunk in f.summaryslices:
    break

#####################################################
# `chunk` now contains the first set of summaryslices so `chunk.slice[0]` refers
# to the first summaryslice in the ROOT file. To access e.g. the DOM IDs, use
# the `.dom_id` attribute

dom_ids = chunk.slices[0].dom_id

print(dom_ids)

#####################################################
# The .type attribute (or in general, <TAB> completion) is useful to find out
# more about the field structure:

print(chunk.slices.type)

#####################################################
# Similar to the summaryslice data, the headers can be accessed the same way
# To read the frame index of all summaryslices in the obtained chunk:

print(chunk.headers.frame_index)

#####################################################
# To be continued...
