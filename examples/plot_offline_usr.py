"""
Reading usr data of events
==========================

To access the ``usr`` data of events, use the ``.usr`` property which behaves
like a dictionary and returns ``lazyarray``, compatible to the ``numpy.array``
interface. The available keys can be accessed either as attributes or via a
dictionary lookup:
"""

import km3io as ki
from km3net_testdata import data_path

#####################################################
# First, pass a filename to the `OfflineReader` class to open the file.
# Note that only some meta information is read into memory.

r = ki.OfflineReader(data_path("offline/usr-sample.root"))


#####################################################
# Accessing the usr fields:

print(r.events.usr_names.tolist())


#####################################################
# to access data of a specific key:

print(ki.tools.usr(r.events, "DeltaPosZ"))
