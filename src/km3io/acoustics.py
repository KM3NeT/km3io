"""
This tookit provides an interface to read the raw acoustic binary data tipe as
produced by the Acoustic Data Filter (ADF).

The acoustic signals are acquired by the CLB with a 195312.5 Hz sampling
frequency (F_S) corresponding to a period of 5.12 microseconds (16 ns * 320).

The acoustic data filter processes the stream in segments (windows) of given
size. Two consecutive segments overlap by a given number of samples. These two
parameters are specified in the ADF configuration as:

  * DAQ_ADF_ANALYSIS_WINDOW_SIZE (typ.: 131072)
  * DAQ_ADF_ANALYSIS_WINDOW_OVERLAP (typ.: 7812)

Typical values are indicated but may change in the future.

When the ADF is set to dump the raw data, the overlapping segment is omitted
so the length of the data chunk is

  FRAME_LENGTH = DAQ_ADF_ANALYSIS_WINDOW_SIZE - DAQ_ADF_ANALYSIS_WINDOW_OVERLAP

Summary description of the raw acoustic data format.

- 4B: UTC seconds (UNIX timestamp);
- 4B: number of 16ns cycles;
- 4B: referred to as 'samples' corresponds to DAQ_ADF_ANALYSIS_WINDOW_SIZE
      (typ.: 131072).

Follows a sequence of 4B * FRAME_LENGTH audio samples. Each sample is 32 bit
float PCM value. FRAME_LENGTH cannot be reconstructed from
DAQ_ADF_ANALYSIS_WINDOW_SIZE without knowing DAQ_ADF_ANALYSIS_WINDOW_OVERLAP
so it has to be set by the user.

FRAME_LENGTH should be constant within the same file, so this approach will hold
(FRAME_LENGTH is configurable in the constructor).

Note: each file contains data from a single transducer and the DOM or base ID
is stored in the filename only. This is not a very good design but here it is
tentatively dealt with.

WARNING: data should be in general expected as ordered but may not be contiguous
in time.
"""

import numpy as np


F_S = 195312.5  # sampling frequency of the acoustic stream in the CLB


def get_dtype(FRAME_LENGTH):
    """Returns the data layout corresponding to FRAME_LENGTH"""
    DATA_TYPE = np.dtype(
        [
            ("utc_seconds", np.uint32),
            ("16ns_cycles", np.uint32),
            ("samples", np.uint32),
            ("frame", np.float32, FRAME_LENGTH),
        ]
    )
    return DATA_TYPE


class RawAcousticReader:
    def __init__(self, filepath, FRAME_LENGTH=123260):

        self.FRAME_LENGTH = FRAME_LENGTH
        DATA_TYPE = get_dtype(FRAME_LENGTH)

        with open(filepath) as acoufile:
            self._data = np.fromfile(acoufile, dtype=DATA_TYPE)
            """ extract CLB id from filename """
            """ split the extension and scan backwards the path """
            self._id = filepath.split(".")[-2][-24 : -16 + 1]

    @property
    def id(self):
        return self._id

    @property
    def pcm(self):
        """Get PCM data concatenating all frames. Data may not be not contiguous."""
        return self._data["frame"].flatten()

    @property
    def timestamps(self):
        return self._data["utc_seconds"], self._data["16ns_cycles"]

    @property
    def timebase(self):
        """
        Constructs sequence of times corresponding to each sample.
        For convenience, the time is stored as a double precision float.
        The resolution is not fixed (which is sub-optimal) but should always
        allow exact representation of the sample time.
        """
        sample_interval = 1 / F_S
        frame_duration = self.FRAME_LENGTH * sample_interval
        time_axis = np.arange(0, frame_duration, sample_interval)
        start_frame = self._data[0]
        n_samples = self.FRAME_LENGTH * len(self._data)

        timebase = np.zeros(n_samples, dtype=np.float64)

        for i, frame in enumerate(self._data):
            sample_range = slice(i * self.FRAME_LENGTH, (i + 1) * self.FRAME_LENGTH)
            timebase[sample_range] = (
                frame["utc_seconds"] + 16e-9 * frame["16ns_cycles"] + time_axis
            )

        return timebase

    def to_wav(self, filepath, gain_dB=0.0):
        """
        Write as wave, with optional gain.
        """
        from scipy.io import wavfile

        pcm = self.pcm
        if gain_dB != 0.0:
            pcm *= 10 ** (0.1 * gain_dB)
        wavfile.write(filepath, int(F_S), pcm)
