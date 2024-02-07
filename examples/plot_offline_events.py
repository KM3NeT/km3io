"""
Reading Offline events
======================

The following example shows how to access events data in an offline ROOT file, which is
written by aanet software.

Note: the offline file used here has MC offline data and was intentionaly reduced
to 10 events.
"""

import km3io as ki
from km3net_testdata import data_path

#####################################################
# First, pass a filename to the `OfflineReader` class to open the file.
# Note that only some meta information is read into memory.

r = ki.OfflineReader(data_path("offline/numucc.root"))


#####################################################
# Accessing the file header
# -------------------------
# Note that not all file headers are supported, so don't be surprised if
# nothing is returned when the file header is called (this can happen if your file
# was produced with old versions of aanet).

h = r.header
print(h)


#####################################################
# Accessing the events data
# -------------------------
# Note that not all data is loaded in memory (again), so printing
# events will only return how many events were found in the file.

print(r.events)


#####################################################
# to explore the events keys:

keys = r.events.keys()
print(keys)

#####################################################
# to access the number of hits associated with each event:

n_hits = r.events.n_hits
print(n_hits)

#####################################################
# to access the number of tracks associated with each event:

n_tracks = r.events.n_tracks
print(n_tracks)

#####################################################
# to access the number of mc hits associated with each event:

n_mc_hits = r.events.n_mc_hits
print(n_mc_hits)

#####################################################
# to access the number of mc tracks associated with each event:

n_mc_tracks = r.events.n_mc_tracks
print(n_mc_tracks)

#####################################################
# to access the overlays:

overlays = r.events.overlays
print(overlays)

#####################################################
# That's it! you can access any key of your interest in the events
# keys in the exact same way.


#####################################################
# item selection in events data
# -----------------------------
# events can be selected as you would select an item from a numpy array.
# for example, to select the mc_hits in event 0:

print(r.events[0].mc_hits)

#####################################################
# or:

print(r.events.mc_hits[0])


#####################################################
# slicing of events
# -----------------
# you can select a slice of events data. For example, to select the number
# of mc hits in the first 5 events:

print(r.events.n_mc_hits[0:5])

#####################################################
# or:

print(r.events[0:5].n_mc_hits)


#####################################################
# you can apply masks to events data as you would do with numpy arrays.
# For example, to select the number of hits higher than 50:

mask = r.events.n_mc_hits > 50

print(r.events.n_mc_hits[mask])

#####################################################
# or:

print(r.events.n_mc_tracks[mask])
