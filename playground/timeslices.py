import uproot

uproot.__version__

f = uproot.open("jpp_v12.0.0.root")

tree = f["KM3NET_TIMESLICE_L1"]

tree.keys()

frames = tree[b'km3net_timeslice_L1'][b'KM3NETDAQ::JDAQTimeslice'][b'vector<KM3NETDAQ::JDAQSuperFrame>']

frames.show()
frames[b'vector<KM3NETDAQ::JDAQSuperFrame>.buffer'].show()
buffer = frames[b'vector<KM3NETDAQ::JDAQSuperFrame>.buffer']

buffer.array(uproot.asdebug)

# the 64 is kind of a ROOT header as you mentioned?

# The file contains 3 timeslices, and each of them consists of 69 frames
# the 69 however is not fixed, it can vary from slice to slice! Each frame
# consists of hits (vector of JDAQHit<6bytes>) and corresponds to an optical module
# which registers those.

# The first timeslice which contains exactly 49243 hits from various different
# optical modules
ts = buffer.array(uproot.asdebug)[0]

ts
len(ts)

# 295464 bytes - 6 bytes offset (don't yet understand why 6, but it works)
# give 295458 bytes of raw JDAQHit data, which makes sense, since we know
# that we have 49243 hits and 49243*6 == 295458

flat_array_of_hits = frames[b'vector<KM3NETDAQ::JDAQSuperFrame>.buffer'].array(
                uproot.asjagged(uproot.astable(
                    uproot.asdtype([("pmt", "u1"),
                                    ("tdc", "u4"),
                                    ("tot", "u1")])),
                                skipbytes=6))

ts_hits = flat_array_of_hits[0]
len(ts_hits)
ts_hits["tot"]

# The problem is now, that it's a flat array of hits, however, they should
# be grouped the module ID
# `.numberOfHits` and `.id` tells us more:

n_hits = frames[b'vector<KM3NETDAQ::JDAQSuperFrame>.numberOfHits'].array()[0]
n_hits

module_ids = frames[b'vector<KM3NETDAQ::JDAQSuperFrame>.id'].array()[0]
module_ids


# The first set of hits belong to module (`.id`) == 806451572, and consists
# of 984 hits

# Here is an inefficient loop to fill the hits:

hits = {}
idx = 0
for module_id, n_hits in zip(module_ids, n_hits):
    hits[module_id] = ts_hits[idx:idx+n_hits]
    idx += n_hits

# quick check against the PyROOT framework:
# [ins] In [15]: ts_hits[ts_hits.dom_id == 808972593]
# Out[15]: TimesliceHits <class 'km3pipe.dataclasses.Table'> (rows: 803)

len(hits[808972593])

# another check to see if the data is correct, expecting:
# [ins] In [16]: ts_hits[ts_hits.dom_id ==808972593].tot[:10]
# Out[16]: array([25, 31, 43, 21, 25, 24, 31, 25, 30, 23], dtype=uint8)
hits[808972593]["tot"][:10]

# perfect! But a bit "whacky" and inefficient ;)
# I am not so familiar with ragged arrays yet, but I am sure one can somehow
# pass this this structure to the flat array and get it in one shot or
# something like this?
# The module IDs are then just encoded by the index and one need another
# lookup in `.id` or so...
