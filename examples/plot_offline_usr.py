"""
Reading usr data of events
==========================

To access the ``usr`` data of events, use the ``.usr`` property which behaves
like a dictionary and returns ``lazyarray``, compatible to the ``numpy.array``
interface. The available keys can be accessed either as attributes or via a
dictionary lookup:
"""
import km3io as ki

#####################################################
# First, pass a filename to the `OfflineReader` class to open the file.
# Note that only some meta information is read into memory.

r = ki.OfflineReader("samples/usr-sample.root")


#####################################################
# Accessing the usr data:

usr = r.events.usr
print(usr)


#####################################################
# to access data of a specific key, you can either do:

print(usr.DeltaPosZ)


#####################################################
# or

print(usr['RecoQuality'])
