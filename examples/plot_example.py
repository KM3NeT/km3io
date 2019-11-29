"""
Reading DAQ Data (Jpp)
======================

The following example shows how to access hits in a ROOT file which is coming
from the detector and written by the `JDataWriter` application.
"""
import km3io

#####################################################
# Accessing the event tree
# ------------------------
# Just pass a filename to the reader class and get access to the event tree
# with:

events = km3io.JppReader("samples/jpp_v12.0.0.root").events

#####################################################
# Note that only some meta information is read into memory.
#
# Printing it will simply tell you how many events it has found. Again, nothing
# else is read yet:

print(events)
