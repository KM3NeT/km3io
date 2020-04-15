"""
Reading Offline tracks
======================

The following example shows how to access tracks data in an offline ROOT file, which is
written by aanet software.

Note: the offline files used here were intentionaly reduced to 10 events.
"""
import km3io as ki

#####################################################
# To access offline tracks/mc_tracks data:

mc_tracks = ki.OfflineReader("samples/numucc.root").events.mc_tracks
tracks = ki.OfflineReader("samples/aanet_v2.0.0.root").events.tracks


#####################################################
# Note that not all data is loaded in memory, so printing
# tracks will only return how many elements (events) were found in
# the tracks branch of the file.

print(tracks)

#####################################################
# same for mc hits

print(mc_tracks)

#####################################################
# Accessing the tracks/mc_tracks keys
# -----------------------------------
# to explore the tracks keys:

keys = tracks.keys()
print(keys)

#####################################################
# to explore the mc_tracks keys:

mc_keys = mc_tracks.keys()
print(mc_keys)

#####################################################
# Accessing tracks data
# ---------------------
# to access data in `E` (tracks energy):

E = tracks.E
print(E)

#####################################################
# to access the likelihood:

likelihood = tracks.lik
print(likelihood)

#####################################################
# That's it! you can access any key of your interest in the tracks
# keys in the exact same way.

#####################################################
# Accessing the mc_tracks data
# ----------------------------
# similarly, you can access mc_tracks data in any key of interest by 
# following the same procedure as for tracks:

cos_zenith = mc_tracks.dir_z
print(cos_zenith)


#####################################################
# or:

dir_y = mc_tracks.dir_y
print(dir_y)


#####################################################
# item selection in tracks data
# -----------------------------
# tracks data can be selected as you would select an item from a numpy array.
# for example, to select E (energy) in the tracks corresponding to the first event:

print(tracks[0].E)

#####################################################
# or:

print(tracks.E[0])


#####################################################
# slicing of tracks
# -----------------
# to select a slice of tracks data:

print(tracks[0:3].E)

#####################################################
# or:

print(tracks.E[0:3])

#####################################################
# you can apply masks to tracks data as you would do with numpy arrays:

mask = tracks.lik > 100

print(tracks.lik[mask])

#####################################################
# or:

print(tracks.dir_z[mask])