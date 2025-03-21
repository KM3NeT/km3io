# -*- coding: utf-8 -*-
"""
KM3NeT Data Definitions v3.6.0
https://git.km3net.de/common/km3net-dataformat
"""

# root
data = dict(
    TTREE_ONLINE_TIMESLICE=    "KM3NET_TIMESLICE"   ,
    TTREE_ONLINE_TIMESLICEL0=  "KM3NET_TIMESLICE_L0",
    TTREE_ONLINE_TIMESLICEL1=  "KM3NET_TIMESLICE_L1",
    TTREE_ONLINE_TIMESLICEL2=  "KM3NET_TIMESLICE_L2",
    TTREE_ONLINE_TIMESLICESN=  "KM3NET_TIMESLICE_SN",
    TTREE_ONLINE_SUMMARYSLICE= "KM3NET_SUMMARYSLICE",
    TTREE_ONLINE_EVENT=        "KM3NET_EVENT"       ,
    TTREE_OFFLINE_EVENT=       "E"                  ,
    TTREE_OSC_OPENDATA_NU=     "binned_nu_response" ,
    TTREE_OSC_OPENDATA_DATA=   "binned_data"        ,
    TTREE_OSC_OPENDATA_MUONS=  "binned_muon"        ,
    TBRANCH_ONLINE_TIMESLICE=    "KM3NET_TIMESLICE"   ,
    TBRANCH_ONLINE_TIMESLICEL0=  "km3net_timeslice_L0",
    TBRANCH_ONLINE_TIMESLICEL1=  "km3net_timeslice_L1",
    TBRANCH_ONLINE_TIMESLICEL2=  "km3net_timeslice_L2",
    TBRANCH_ONLINE_TIMESLICESN=  "km3net_timeslice_SN",
    TBRANCH_ONLINE_SUMMARYSLICE= "KM3NET_SUMMARYSLICE",
    TBRANCH_ONLINE_EVENT=        "KM3NET_EVENT"       ,
    TBRANCH_OFFLINE_EVENT=       "Evt"                ,
    COMPRESSION_LEVEL_ONLINE_TIMESLICE=    0,
    COMPRESSION_LEVEL_ONLINE_TIMESLICEL0=  0,
    COMPRESSION_LEVEL_ONLINE_TIMESLICEL1=  2,
    COMPRESSION_LEVEL_ONLINE_TIMESLICEL2=  2,
    COMPRESSION_LEVEL_ONLINE_TIMESLICESN=  2,
    COMPRESSION_LEVEL_ONLINE_SUMMARYSLICE= 1,
    COMPRESSION_LEVEL_ONLINE_EVENT=        0,
    COMPRESSION_LEVEL_OFFLINE_EVENT=       1,
    BASKET_SIZE_ONLINE_TIMESLICE=      5000000,
    BASKET_SIZE_ONLINE_TIMESLICEL0=  500000000,
    BASKET_SIZE_ONLINE_TIMESLICEL1=    5000000,
    BASKET_SIZE_ONLINE_TIMESLICEL2=    5000000,
    BASKET_SIZE_ONLINE_TIMESLICESN=    5000000,
    BASKET_SIZE_ONLINE_SUMMARYSLICE=   5000000,
    BASKET_SIZE_ONLINE_EVENT=          5000000,
    BASKET_SIZE_OFFLINE_EVENT=         5000000,
    SPLIT_LEVEL_ONLINE_TIMESLICE=    1,
    SPLIT_LEVEL_ONLINE_TIMESLICEL0=  2,
    SPLIT_LEVEL_ONLINE_TIMESLICEL1=  2,
    SPLIT_LEVEL_ONLINE_TIMESLICEL2=  2,
    SPLIT_LEVEL_ONLINE_TIMESLICESN=  2,
    SPLIT_LEVEL_ONLINE_SUMMARYSLICE= 1,
    SPLIT_LEVEL_ONLINE_EVENT=        1,
    SPLIT_LEVEL_OFFLINE_EVENT=       4,
    AUTOFLUSH_LEVEL_ONLINE_TIMESLICE=    1000,
    AUTOFLUSH_LEVEL_ONLINE_TIMESLICEL0=  1000,
    AUTOFLUSH_LEVEL_ONLINE_TIMESLICEL1=  1000,
    AUTOFLUSH_LEVEL_ONLINE_TIMESLICEL2=  1000,
    AUTOFLUSH_LEVEL_ONLINE_TIMESLICESN=  1000,
    AUTOFLUSH_LEVEL_ONLINE_SUMMARYSLICE= 1000,
    AUTOFLUSH_LEVEL_ONLINE_EVENT=        1000,
    AUTOFLUSH_LEVEL_OFFLINE_EVENT=        500,
)
