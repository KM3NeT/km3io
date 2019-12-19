"""
Reading DAQ Data
================

The following example shows how to access hits in a ROOT file which is coming
from the detector and written by the `JDataWriter` application.

Such a file is usually called "KM3NET_00000001_00000002.root", where the first
number is the detector ID and the second the run number.
"""
import km3io

#####################################################
# Accessing the event tree
# ------------------------
# Just pass a filename to the reader class and get access to the event tree
# with:

f = km3io.DAQReader("samples/daq_v1.0.0.root")

#####################################################
# Note that only some meta information is read into memory.
#
# Printing it will simply tell you how many events it has found. Again, nothing
# else is read yet:

print(f.events)
