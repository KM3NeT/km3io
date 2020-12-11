import os
import re
import unittest
import inspect
import awkward as ak

from km3net_testdata import data_path

from km3io.gseagen import GSGReader

GSG_READER = GSGReader(data_path("gseagen/gseagen.root"))

AWKWARD_STR_CLASSES = [
    s[1] for s in inspect.getmembers(ak.behaviors.string, inspect.isclass)
]


class TestGSGHeader(unittest.TestCase):
    def setUp(self):
        self.header = GSG_READER.header

    def test_str_byte_type(self):
        assert type(self.header["gSeaGenVer"]) in AWKWARD_STR_CLASSES
        assert type(self.header["GenieVer"]) in AWKWARD_STR_CLASSES
        assert type(self.header["gSeaGenVer"]) in AWKWARD_STR_CLASSES
        assert type(self.header["InpXSecFile"]) in AWKWARD_STR_CLASSES
        assert type(self.header["Flux1"]) in AWKWARD_STR_CLASSES
        assert type(self.header["Flux2"]) in AWKWARD_STR_CLASSES

    def test_values(self):
        assert self.header["RunNu"] == 1
        assert self.header["RanSeed"] == 3662074
        self.assertAlmostEqual(self.header["NTot"], 1000.0)
        self.assertAlmostEqual(self.header["EvMin"], 5.0)
        self.assertAlmostEqual(self.header["EvMax"], 50.0)
        self.assertAlmostEqual(self.header["CtMin"], -1.0)
        self.assertAlmostEqual(self.header["CtMax"], 1.0)
        self.assertAlmostEqual(self.header["Alpha"], 1.4)
        assert self.header["NBin"] == 1
        self.assertAlmostEqual(self.header["Can1"], 0.0)
        self.assertAlmostEqual(self.header["Can2"], 476.5)
        self.assertAlmostEqual(self.header["Can3"], 403.4)
        self.assertAlmostEqual(self.header["OriginX"], 0.0)
        self.assertAlmostEqual(self.header["OriginY"], 0.0)
        self.assertAlmostEqual(self.header["OriginZ"], 0.0)
        self.assertAlmostEqual(self.header["HRock"], 93.03036681)
        self.assertAlmostEqual(self.header["HSeaWater"], 684.39143353)
        self.assertAlmostEqual(self.header["RVol"], 611.29143353)
        self.assertAlmostEqual(self.header["HBedRock"], 0.0)
        self.assertAlmostEqual(self.header["NAbsLength"], 3.0)
        self.assertAlmostEqual(self.header["AbsLength"], 93.33)
        self.assertAlmostEqual(self.header["SiteDepth"], 2425.0)
        self.assertAlmostEqual(self.header["SiteLatitude"], 0.747)
        self.assertAlmostEqual(self.header["SiteLongitude"], 0.10763)
        self.assertAlmostEqual(self.header["SeaBottomRadius"], 6368000.0)
        assert round(self.header["GlobalGenWeight"] - 6.26910765e08, 0) == 0
        self.assertAlmostEqual(self.header["RhoSW"], 1.03975)
        self.assertAlmostEqual(self.header["RhoSR"], 2.65)
        self.assertAlmostEqual(self.header["TGen"], 31556926.0)
        assert not self.header["PropMode"]
        assert self.header["NNu"] == 2
        self.assertListEqual(self.header["NuList"].tolist(), [-14, 14])


class TestGSGEvents(unittest.TestCase):
    def setUp(self):
        self.events = GSG_READER.events

    def test_event_single_values(self):
        event = self.events[0]
        assert 1 == event.iEvt
        self.assertAlmostEqual(event.PScale, 1.0)
        assert event.TargetA == 28
        assert event.TargetZ == 14
        assert event.InterId == 2
        assert event.ScattId == 3
        self.assertAlmostEqual(event.Bx, 0.21398980096236023)
        self.assertAlmostEqual(event.By, 0.7736389792036026)
        assert event.VerInCan == 0
        self.assertAlmostEqual(event.WaterXSec, 9.814545541159586e-42)
        self.assertAlmostEqual(event.WaterIntLen, 169191612204.44382)
        self.assertAlmostEqual(event.PEarth, 0.9998206835107583)
        self.assertAlmostEqual(event.ColumnDepth, 31352421806833.758)
        self.assertAlmostEqual(event.XSecMean, 9.49810757204515e-42)
        self.assertAlmostEqual(event.Agen, 934842.6115446005)
        self.assertAlmostEqual(event.WGen, 480360599.4207591)
        self.assertAlmostEqual(event.WEvt, 5.629637364719835)
        self.assertAlmostEqual(event.E_nu, 29.210801854810974)
        assert event.Pdg_nu == -14
        self.assertAlmostEqual(event.Vx_nu, 202.86806811399845)
        self.assertAlmostEqual(event.Vy_nu, 226.64032038584787)
        self.assertAlmostEqual(event.Vz_nu, -0.5526929982180058)
        self.assertAlmostEqual(event.Dx_nu, -0.7554430076659393)
        self.assertAlmostEqual(event.Dy_nu, 0.3034298552575011)
        self.assertAlmostEqual(event.Dz_nu, 0.5807204018346965)
        self.assertAlmostEqual(event.T_nu, 0.0)
        self.assertAlmostEqual(event.E_pl, 6.648776215872709)
        assert event.Pdg_pl == -13
        self.assertAlmostEqual(event.Vx_pl, 202.86806811399845)
        self.assertAlmostEqual(event.Vy_pl, 226.64032038584787)
        self.assertAlmostEqual(event.Vz_pl, -0.5526929982180058)
        self.assertAlmostEqual(event.Dx_pl, -0.8781745795144783)
        self.assertAlmostEqual(event.Dy_pl, 0.2818890466120743)
        self.assertAlmostEqual(event.Dz_pl, 0.3864556550171106)
        self.assertAlmostEqual(event.T_pl, 0.0)
        assert event.NTracks == 1

    def test_event_list_values(self):
        event = self.events[1]
        self.assertListEqual(event.Id_tr.tolist(), [4, 5, 10, 11, 12])
        self.assertListEqual(event.Pdg_tr.tolist(), [22, -13, 2112, -211, 111])
        [
            self.assertAlmostEqual(x, y)
            for x, y in zip(
                event.E_tr, [0.00618, 4.88912206, 2.33667201, 1.0022909, 1.17186997]
            )
        ]
        [
            self.assertAlmostEqual(x, y)
            for x, y in zip(
                event.Vx_tr,
                [
                    -337.67895799,
                    -337.67895799,
                    -337.67895799,
                    -337.67895799,
                    -337.67895799,
                ],
            )
        ]
        [
            self.assertAlmostEqual(x, y)
            for x, y in zip(
                event.Vy_tr,
                [
                    -203.90999969,
                    -203.90999969,
                    -203.90999969,
                    -203.90999969,
                    -203.90999969,
                ],
            )
        ]
        [
            self.assertAlmostEqual(x, y)
            for x, y in zip(
                event.Vz_tr,
                [416.08845294, 416.08845294, 416.08845294, 416.08845294, 416.08845294],
            )
        ]
        [
            self.assertAlmostEqual(x, y)
            for x, y in zip(
                event.Dx_tr,
                [0.06766196, -0.63563065, -0.70627586, -0.76364544, -0.80562216],
            )
        ]
        [
            self.assertAlmostEqual(x, y)
            for x, y in zip(
                event.Dy_tr,
                [0.33938809, -0.4846643, 0.50569058, -0.04136113, 0.10913917],
            )
        ]
        [
            self.assertAlmostEqual(x, y)
            for x, y in zip(
                event.Dz_tr,
                [-0.93820978, -0.6008945, -0.49543056, -0.64430963, -0.58228994],
            )
        ]
        [self.assertAlmostEqual(x, y) for x, y in zip(event.T_tr, 5 * [0.0])]
