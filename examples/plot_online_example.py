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
# IDs of the slice with the index 0:

dom_ids = f.summaryslices.slices[0].dom_id

print(dom_ids)

#####################################################
# The .dtype attribute (or in general, <TAB> completion) is useful to find out
# more about the field structure:

print(f.summaryslices.headers.dtype)

#####################################################
# To read the frame index:

print(f.summaryslices.headers.frame_index)

#####################################################
# The resulting array is a ChunkedArray which is an extended version of a
# numpy array and behaves like one.

#####################################################
# Reading TimeSlices
# ------------------
# To be continued.
#
