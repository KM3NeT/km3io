import os
import re
import unittest

from km3io.gseagen import GSGReader

SAMPLES_DIR = os.path.join(os.path.dirname(__file__), "samples")
GSG_FILE = os.path.join(SAMPLES_DIR, "gseagen.root")
GSG_READER = GSGReader(GSG_FILE)


class TestGSGHeader(unittest.TestCase):
    def setUp(self):
        self.header = GSG_READER.header

    def test_str_byte_type(self):
        assert isinstance(self.header['gSeaGenVer'], str)
        assert isinstance(self.header['GenieVer'], str)
        assert isinstance(self.header['gSeaGenVer'], str)
        assert isinstance(self.header['InpXSecFile'], str)
        assert isinstance(self.header['Flux1'], str)
        assert isinstance(self.header['Flux2'], str)

    def test_values(self):
        assert self.header["RunNu"] == 1
        assert self.header["RanSeed"] == 3662074
        self.assertAlmostEqual(self.header["NTot"], 1000.)
        self.assertAlmostEqual(self.header["EvMin"], 5.)
        self.assertAlmostEqual(self.header["EvMax"], 50.)
        self.assertAlmostEqual(self.header["CtMin"], -1.)
        self.assertAlmostEqual(self.header["CtMax"], 1.)
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
        self.assertAlmostEqual(self.header["SeaBottomRadius"], 6368000.)
        assert round(self.header["GlobalGenWeight"]-6.26910765e+08, 0) == 0
        self.assertAlmostEqual(self.header["RhoSW"], 1.03975)
        self.assertAlmostEqual(self.header["RhoSR"], 2.65)
        self.assertAlmostEqual(self.header["TGen"], 31556926.)
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
            self.assertAlmostEqual(x, y) for x, y in zip(
                event.E_tr,
                [0.00618, 4.88912206, 2.33667201, 1.0022909, 1.17186997])
        ]
        [
            self.assertAlmostEqual(x, y)
            for x, y in zip(event.Vx_tr, [
                -337.67895799, -337.67895799, -337.67895799, -337.67895799,
                -337.67895799
            ])
        ]
        [
            self.assertAlmostEqual(x, y)
            for x, y in zip(event.Vy_tr, [
                -203.90999969, -203.90999969, -203.90999969, -203.90999969,
                -203.90999969
            ])
        ]
        [
            self.assertAlmostEqual(x, y)
            for x, y in zip(event.Vz_tr, [
                416.08845294, 416.08845294, 416.08845294, 416.08845294,
                416.08845294
            ])
        ]
        [
            self.assertAlmostEqual(x, y)
            for x, y in zip(event.Dx_tr, [
                0.06766196, -0.63563065, -0.70627586, -0.76364544, -0.80562216
            ])
        ]
        [
            self.assertAlmostEqual(x, y) for x, y in zip(
                event.Dy_tr,
                [0.33938809, -0.4846643, 0.50569058, -0.04136113, 0.10913917])
        ]
        [
            self.assertAlmostEqual(x, y)
            for x, y in zip(event.Dz_tr, [
                -0.93820978, -0.6008945, -0.49543056, -0.64430963, -0.58228994
            ])
        ]
        [self.assertAlmostEqual(x, y) for x, y in zip(event.T_tr, 5 * [0.])]


# class TestDAQEvent(unittest.TestCase):
#     def setUp(self):
#         self.event = DAQ_FILE.events[0]
#
#     def test_str(self):
#         assert re.match(".*event.*96.*snapshot.*18.*triggered",
#                         str(self.event))
#
#     def test_repr(self):
#         assert re.match(".*event.*96.*snapshot.*18.*triggered",
#                         self.event.__repr__())
#
#
# class TestDAQEventsSnapshotHits(unittest.TestCase):
#     def setUp(self):
#         self.events = DAQ_FILE.events
#         self.lengths = {0: 96, 1: 124, -1: 78}
#         self.total_item_count = 298
#
#     def test_reading_snapshot_hits(self):
#         hits = self.events.snapshot_hits
#
#         for event_id, length in self.lengths.items():
#             assert length == len(hits[event_id].dom_id)
#             assert length == len(hits[event_id].channel_id)
#             assert length == len(hits[event_id].time)
#
#     def test_total_item_counts(self):
#         hits = self.events.snapshot_hits
#
#         assert self.total_item_count == sum(hits.dom_id.count())
#         assert self.total_item_count == sum(hits.channel_id.count())
#         assert self.total_item_count == sum(hits.time.count())
#
#     def test_data_values(self):
#         hits = self.events.snapshot_hits
#
#         self.assertListEqual([806451572, 806451572, 806455814],
#                              list(hits.dom_id[0][:3]))
#         self.assertListEqual([10, 13, 0], list(hits.channel_id[0][:3]))
#         self.assertListEqual([30733918, 30733916, 30733256],
#                              list(hits.time[0][:3]))
#
#     def test_channel_ids_have_valid_values(self):
#         hits = self.events.snapshot_hits
#
#         # channel IDs are always between [0, 30]
#         assert all(c >= 0 for c in hits.channel_id.min())
#         assert all(c < 31 for c in hits.channel_id.max())
#
#
# class TestDAQEventsTriggeredHits(unittest.TestCase):
#     def setUp(self):
#         self.events = DAQ_FILE.events
#         self.lengths = {0: 18, 1: 53, -1: 9}
#         self.total_item_count = 80
#
#     def test_data_lengths(self):
#         hits = self.events.triggered_hits
#
#         for event_id, length in self.lengths.items():
#             assert length == len(hits[event_id].dom_id)
#             assert length == len(hits[event_id].channel_id)
#             assert length == len(hits[event_id].time)
#             assert length == len(hits[event_id].trigger_mask)
#
#     def test_total_item_counts(self):
#         hits = self.events.triggered_hits
#
#         assert self.total_item_count == sum(hits.dom_id.count())
#         assert self.total_item_count == sum(hits.channel_id.count())
#         assert self.total_item_count == sum(hits.time.count())
#
#     def test_data_values(self):
#         hits = self.events.triggered_hits
#
#         self.assertListEqual([806451572, 806451572, 808432835],
#                              list(hits.dom_id[0][:3]))
#         self.assertListEqual([10, 13, 1], list(hits.channel_id[0][:3]))
#         self.assertListEqual([30733918, 30733916, 30733429],
#                              list(hits.time[0][:3]))
#         self.assertListEqual([16, 16, 4], list(hits.trigger_mask[0][:3]))
#
#     def test_channel_ids_have_valid_values(self):
#         hits = self.events.triggered_hits
#
#         # channel IDs are always between [0, 30]
#         assert all(c >= 0 for c in hits.channel_id.min())
#         assert all(c < 31 for c in hits.channel_id.max())
#
#
# class TestDAQTimeslices(unittest.TestCase):
#     def setUp(self):
#         self.ts = DAQ_FILE.timeslices
#
#     def test_data_lengths(self):
#         assert 3 == len(self.ts._timeslices["L1"][0])
#         assert 3 == len(self.ts._timeslices["SN"][0])
#         with self.assertRaises(KeyError):
#             assert 0 == len(self.ts._timeslices["L2"][0])
#         with self.assertRaises(KeyError):
#             assert 0 == len(self.ts._timeslices["L0"][0])
#
#     def test_streams(self):
#         self.ts.stream("L1", 0)
#         self.ts.stream("SN", 0)
#
#     def test_reading_frames(self):
#         assert 8 == len(self.ts.stream("SN", 1).frames[808447186])
#
#     def test_str(self):
#         s = str(self.ts)
#         assert "L1" in s
#         assert "SN" in s
#
#
# class TestDAQTimeslice(unittest.TestCase):
#     def setUp(self):
#         self.ts = DAQ_FILE.timeslices
#         self.n_frames = {"L1": [69, 69, 69], "SN": [64, 66, 68]}
#
#     def test_str(self):
#         for stream, n_frames in self.n_frames.items():
#             print(stream, n_frames)
#             for i in range(len(n_frames)):
#                 s = str(self.ts.stream(stream, i))
#                 assert re.match("{}.*{}".format(stream, n_frames[i]), s)
#
#
# class TestSummaryslices(unittest.TestCase):
#     def setUp(self):
#         self.ss = DAQ_FILE.summaryslices
#
#     def test_headers(self):
#         assert 3 == len(self.ss.headers)
#         self.assertListEqual([44, 44, 44], list(self.ss.headers.detector_id))
#         self.assertListEqual([6633, 6633, 6633], list(self.ss.headers.run))
#         self.assertListEqual([126, 127, 128],
#                              list(self.ss.headers.frame_index))
#         assert 806451572 == self.ss.slices[0].dom_id[0]
#
#     def test_slices(self):
#         assert 3 == len(self.ss.slices)
#
#     def test_rates(self):
#         assert 3 == len(self.ss.rates)
#
#     def test_fifo(self):
#         s = self.ss.slices[0]
#         dct_fifo_stat = {
#             808981510: True,
#             808981523: False,
#             808981672: False,
#             808974773: False
#         }
#         for dom_id, fifo_status in dct_fifo_stat.items():
#             frame = s[s.dom_id == dom_id]
#             assert any(get_channel_flags(frame.fifo[0])) == fifo_status
#
#     def test_has_udp_trailer(self):
#         s = self.ss.slices[0]
#         dct_udp_trailer = {
#             806451572: True,
#             806455814: True,
#             806465101: True,
#             806483369: True,
#             806487219: True,
#             806487226: True,
#             806487231: True,
#             808432835: True,
#             808435278: True,
#             808447180: True,
#             808447186: True
#         }
#         for dom_id, udp_trailer in dct_udp_trailer.items():
#             frame = s[s.dom_id == dom_id]
#             assert has_udp_trailer(frame.fifo[0]) == udp_trailer
#
#     def test_high_rate_veto(self):
#         s = self.ss.slices[0]
#         dct_high_rate_veto = {
#             808489014: True,
#             808489117: False,
#             808493910: True,
#             808946818: True,
#             808951460: True,
#             808956908: True,
#             808959411: True,
#             808961448: True,
#             808961480: True,
#             808961504: True,
#             808961655: False,
#             808964815: False,
#             808964852: True,
#             808969848: False,
#             808969857: True,
#             808972593: True,
#             808972598: True,
#             808972698: False,
#             808974758: False,
#             808974773: True,
#             808974811: True,
#             808974972: True,
#             808976377: True,
#             808979567: False,
#             808979721: False,
#             808979729: False,
#             808981510: True,
#             808981523: True,
#             808981672: False,
#             808981812: True,
#             808981864: False,
#             808982018: False
#         }
#         for dom_id, high_rate_veto in dct_high_rate_veto.items():
#             frame = s[s.dom_id == dom_id]
#             assert any(get_channel_flags(frame.hrv[0])) == high_rate_veto
#
#     def test_max_sequence_number(self):
#         s = self.ss.slices[0]
#         dct_seq_numbers = {
#             808974758: 18,
#             808974773: 26,
#             808974811: 25,
#             808974972: 41,
#             808976377: 35,
#             808979567: 20,
#             808979721: 17,
#             808979729: 25,
#             808981510: 35,
#             808981523: 27,
#             808981672: 17,
#             808981812: 34,
#             808981864: 18,
#             808982018: 21,
#             808982041: 27,
#             808982077: 32,
#             808982547: 20,
#             808984711: 26,
#             808996773: 31,
#             808997793: 21,
#             809006037: 26,
#             809007627: 18,
#             809503416: 28,
#             809521500: 31,
#             809524432: 21,
#             809526097: 23,
#             809544058: 21,
#             809544061: 23
#         }
#         for dom_id, max_sequence_number in dct_seq_numbers.items():
#             frame = s[s.dom_id == dom_id]
#             assert get_udp_max_sequence_number(
#                 frame.dq_status[0]) == max_sequence_number
#
#     def test_number_udp_packets(self):
#         s = self.ss.slices[0]
#         dct_n_packets = {
#             808451904: 27,
#             808451907: 22,
#             808469129: 20,
#             808472260: 21,
#             808472265: 22,
#             808488895: 20,
#             808488990: 20,
#             808489014: 28,
#             808489117: 22,
#             808493910: 26,
#             808946818: 23,
#             808951460: 37,
#             808956908: 33,
#             808959411: 36,
#             808961448: 28,
#             808961480: 24,
#             808961504: 28,
#             808961655: 20,
#             808964815: 20,
#             808964852: 28,
#             808969848: 21
#         }
#         for dom_id, n_udp_packets in dct_n_packets.items():
#             frame = s[s.dom_id == dom_id]
#             assert get_number_udp_packets(frame.dq_status[0]) == n_udp_packets
#
#     def test_hrv_flags(self):
#         s = self.ss.slices[0]
#         dct_hrv_flags = {
#             809524432: [
#                 False, False, False, False, False, False, False, False, False,
#                 False, False, False, False, False, False, False, False, False,
#                 False, False, False, False, False, False, False, False, False,
#                 False, False, False, False
#             ],
#             809526097: [
#                 False, False, False, False, False, False, False, False, False,
#                 False, False, False, False, False, False, False, False, False,
#                 True, False, False, False, False, False, False, False, True,
#                 False, False, False, False
#             ],
#             809544058: [
#                 False, False, False, False, False, False, False, False, False,
#                 False, False, False, False, False, False, False, False, False,
#                 False, False, False, False, False, False, False, False, False,
#                 False, False, False, False
#             ],
#             809544061: [
#                 False, True, False, False, False, True, False, False, False,
#                 False, False, False, False, False, False, True, False, False,
#                 False, False, False, True, False, False, False, False, False,
#                 False, False, False, False
#             ]
#         }
#         for dom_id, hrv_flags in dct_hrv_flags.items():
#             frame = s[s.dom_id == dom_id]
#             assert any([
#                 a == b
#                 for a, b in zip(get_channel_flags(frame.hrv[0]), hrv_flags)
#             ])
#
#     def test_fifo_flags(self):
#         s = self.ss.slices[0]
#         dct_fifo_flags = {
#             808982547: [
#                 False, False, False, False, False, False, False, False, False,
#                 False, False, False, False, False, False, False, False, False,
#                 False, False, False, False, False, False, False, False, False,
#                 False, False, False, False
#             ],
#             808984711: [
#                 False, False, False, False, False, False, False, False, False,
#                 False, False, False, False, False, False, False, False, False,
#                 False, False, False, False, False, False, False, False, False,
#                 False, False, False, False
#             ],
#             808996773: [
#                 False, False, False, False, False, False, False, False, False,
#                 False, False, False, False, False, False, False, False, False,
#                 False, False, False, False, False, False, False, False, False,
#                 False, False, False, False
#             ],
#             808997793: [
#                 False, False, False, False, False, False, False, False, False,
#                 False, False, False, False, False, False, False, False, False,
#                 False, False, False, False, False, False, False, False, False,
#                 False, False, False, False
#             ],
#             809006037: [
#                 False, False, False, False, False, False, False, False, False,
#                 False, False, False, False, False, False, False, False, False,
#                 False, False, False, False, False, False, False, False, False,
#                 False, False, False, False
#             ],
#             808981510: [
#                 False, False, False, False, False, False, False, False, False,
#                 False, False, False, False, False, True, True, False, False,
#                 False, True, False, True, True, True, True, True, True, False,
#                 False, True, False
#             ]
#         }
#         for dom_id, fifo_flags in dct_fifo_flags.items():
#             frame = s[s.dom_id == dom_id]
#             assert any([
#                 a == b
#                 for a, b in zip(get_channel_flags(frame.fifo[0]), fifo_flags)
#             ])
#
#     def test_str(self):
#         print(str(self.ss))
#
#
# class TestGetRate(unittest.TestCase):
#     def test_zero(self):
#         assert 0 == get_rate(0)
#
#     def test_some_values(self):
#         assert 2054 == get_rate(1)
#         assert 55987 == get_rate(123)
#         assert 1999999 == get_rate(255)
#
#     def test_vectorized_input(self):
#         self.assertListEqual([2054], list(get_rate([1])))
#         self.assertListEqual([2054, 2111, 2169], list(get_rate([1, 2, 3])))
