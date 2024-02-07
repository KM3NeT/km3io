"""
Reading Offline tracks
======================

The following example shows how to access tracks data in an offline ROOT file.

Note: the offline files used here were intentionaly reduced to 10 events.
"""

import km3io as ki
from km3net_testdata import data_path

#####################################################
# We open the file using the

f = ki.OfflineReader(data_path("offline/numucc.root"))

#####################################################
# To access offline tracks/mc_tracks data:

f.tracks
f.mc_tracks

#####################################################
# Note that no data is loaded in memory at this point, so printing
# tracks will only return how many sub-branches (corresponding to
# events) were found.

f.tracks

#####################################################
# same for mc hits

f.mc_tracks

#####################################################
# Accessing the tracks/mc_tracks keys
# -----------------------------------
# to explore the reconstructed tracks fields:

f.tracks.fields

#####################################################
# the same for MC tracks

f.mc_tracks.fields

#####################################################
# Accessing tracks data
# ---------------------
# each field will return a nested `awkward.Array` and load everything into
# memory, so be careful if you are working with larger files.

f.tracks.E

######################################################
# The z direction of all reconstructed tracks

f.tracks.dir_z

######################################################
# The likelihoods

f.tracks.lik


#####################################################
# To select just a single event or a subset of events, use the indices or slices.
# The following will access all tracks and their fields
# of the third event (0 is the first):

f[2].tracks

######################################################
# The z direction of all tracks in the third event:

f[2].tracks.dir_z


#####################################################
# while here, we select the first 3 events. Notice that all fields will return
# nested arrays, as we have seem above where all events were selected.

f[:3]

######################################################
# All tracks for the first three events

f[:3].tracks

######################################################
# The z directions of all tracks of the first three events

f[:3].tracks.dir_z

#####################################################
# or events from 3 and 5 (again, 0 indexing):


f[2:5]

######################################################
# the tracks of those events

f[2:5].tracks

######################################################
# and just the z directions of those

f[2:5].tracks.dir_z
