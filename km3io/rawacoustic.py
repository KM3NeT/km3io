import numpy as np

'''
Layout of the raw acoustic binary data tipe as produced by the Acoustic Data Filter (ADF). 

WARNING: the output of the acoustic data filter may change in the future!

The first two integer fields represent the time as: UTC seconds (UNIX timestamp) + number of 16ns cycles.

The third integer field, 'samples', is undocumented, possibly unused or deprecated.

The fourth field is a sequence of FRAME_LENGTH audio samples. Each sample is 32 bit float PCM value.

It is not clear whether FRAME_LENGTH constant or depends on the ADF configuration. So far its value never changed.

As long as FRAME_LENGTH is constant within the same file, this approach will hold (FRAME_LENGTH can be made configurable in the constructor).

Samples are acquired with a 195312.5 Hz sampling frequency (F_S). Note that this corresponds to a period of 5.12 microseconds (320 16ns-cycles)

Each file contains data from a single transducer and the DOM or base ID is stored in the filename only. This is not a very good design but we deal with it.

WARNING: data shoild be ordered but may not be contiguous in time.
'''

FRAME_LENGTH = 123260
DATA_TYPE    = np.dtype( [('utc_seconds', np.uint32),
                       ('16ns_cycles', np.uint32),
                       ('samples'    , np.uint32),
                       ('frame', np.float32, FRAME_LENGTH)] )
F_S          = 195312.5

class RawAcousticReader():

    def __init__(self, filepath):
        with open(filepath) as acoufile:
            self._data = np.fromfile(acoufile, dtype=DATA_TYPE)
            '''extract 8 characters starting from the 5th'''
            self._id   = filepath.split('/')[-1][4:1+12] 

    @property
    def ID(self):
        return self._id

    @property
    def pcm(self):
        ''' Get PCM data concatenating all frames. Data may not be not contiguous.'''
        return self._data['frame'].flatten()

    @property
    def timestamps():
        return self._data['utc_seconds'], self._data['16ns_cycles']
    
    @property
    def timebase(self, zero_time = 0.0):
        '''
        Constructs sequence of times corresponding to each sample.
        For convenience, the time is stored as a double precision float.
        The resolution is not fixed (which is sub-optimal) but should always allow exact representation of the sample time.
        A zero_time can be set to get times relative to a given one.
        '''
        sample_interval = 1 / F_S
        frame_duration  = FRAME_LENGTH * sample_interval
        time_axis       = np.arange(0, frame_duration, sample_interval)
        start_frame     = self._data[0]
        n_samples       = FRAME_LENGTH * len(self._data)
        
        timebase = np.zeros(n_samples, dtype=np.float64)
    
        for i, frame in enumerate(self._data):
            sample_range = slice(i * FRAME_LENGTH, (i + 1) * FRAME_LENGTH)
            timebase[sample_range] = (frame['utc_seconds'] - zero_time) + 16e-9 * frame['16ns_cycles'] + time_axis

        return timebase
        
