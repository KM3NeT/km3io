#!/usr/bin/env python3
import unittest
import tempfile

import numpy as np
from km3net_testdata import data_path

from km3io.acoustics import RawAcousticReader


class TestRawAcousticReader(unittest.TestCase):
    def setUp(self):
        self.r = RawAcousticReader(
            data_path("acoustics/DOM_808956920_CH1_1608751683.bin")
        )

    def test_id(self):
        assert "808956920" == self.r.id

    def test_timestamps(self):
        assert np.allclose(
            [[1608751679, 1608751680], [47216000, 24159200]], self.r.timestamps
        )

    def test_pcm(self):
        assert np.allclose([0.00315881, 0.00326228, 0.00348866], self.r.pcm[:3])

    def test_timebase(self):
        assert 246520 == len(self.r.timebase)
        print(self.r.timebase[:3])
        assert np.allclose(
            [1.60875168e09, 1.60875168e09, 1.60875168e09], list(self.r.timebase[:3])
        )

    def test_to_wav(self):
        outfile = tempfile.NamedTemporaryFile(delete=True)
        self.r.to_wav(outfile)
