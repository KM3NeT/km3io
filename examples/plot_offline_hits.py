"""
Reading Offline hits
====================

The following example shows how to access hits data in an offline ROOT file, which is
written by aanet software.

Note: the offline file used here has MC offline data and was intentionaly reduced
to 10 events.
"""
import km3io as ki

#####################################################
# To access offline hits/mc_hits data:

mc_hits = ki.OfflineReader("samples/numucc.root").events.mc_hits
hits = ki.OfflineReader("samples/aanet_v2.0.0.root").events.hits


#####################################################
# Note that not all data is loaded in memory, so printing
# hits will only return how many elements (events) were found in
# the hits branch of the file.

print(hits)

#####################################################
# same for mc hits

print(mc_hits)

#####################################################
# Accessing the hits/mc_hits keys
# -------------------------------
# to explore the hits keys:

keys = hits.keys()
print(keys)

#####################################################
# to explore the mc_hits keys:

mc_keys = mc_hits.keys()
print(mc_keys)

#####################################################
# Accessing hits data
# -------------------------
# to access data in dom_id:

dom_ids = hits.dom_id
print(dom_ids)

#####################################################
# to access the channel ids:

channel_ids = hits.channel_id
print(channel_ids)

#####################################################
# That's it! you can access any key of your interest in the hits
# keys in the exact same way.

#####################################################
# Accessing the mc_hits data
# --------------------------
# similarly, you can access mc_hits data in any key of interest by 
# following the same procedure as for hits:

mc_pmt_ids = mc_hits.pmt_id
print(mc_pmt_ids)


#####################################################
# to access the mc_hits time:
mc_t = mc_hits.t
print(mc_t)

#####################################################
# item selection in hits data
# ---------------------------
# hits data can be selected as you would select an item from a numpy array.
# for example, to select DOM ids in the hits corresponding to the first event:

print(hits[0].dom_id)

#####################################################
# or:

print(hits.dom_id[0])

#####################################################
# slicing of hits
# ---------------
# to select a slice of hits data:

print(hits[0:3].channel_id)

#####################################################
# or:

print(hits.channel_id[0:3])

#####################################################
# you can apply masks to hits data as you would do with numpy arrays:

mask = hits.channel_id > 10

print(hits.channel_id[mask])

#####################################################
# or:

print(hits.dom_id[mask])