# -*- coding: utf-8 -*-
"""
KM3NeT Data Definitions v2.0.0-9-gbae3720
https://git.km3net.de/common/km3net-dataformat
"""

# reconstruction
data = dict(
    JPP_RECONSTRUCTION_TYPE=4000,
    JMUONBEGIN=0,
    JMUONPREFIT=1,
    JMUONSIMPLEX=2,
    JMUONGANDALF=3,
    JMUONENERGY=4,
    JMUONSTART=5,
    JLINEFIT=6,
    JMUONEND=99,
    JSHOWERBEGIN=100,
    JSHOWERPREFIT=101,
    JSHOWERPOSITIONFIT=102,
    JSHOWERCOMPLETEFIT=103,
    JSHOWER_BJORKEN_Y=104,
    JSHOWERENERGYPREFIT=105,
    JSHOWERPOINTSIMPLEX=106,
    JSHOWERDIRECTIONPREFIT=107,
    JSHOWEREND=199,
    DUSJ_RECONSTRUCTION_TYPE=200,
    DUSJSHOWERBEGIN=200,
    DUSJSHOWERPREFIT=201,
    DUSJSHOWERPOSITIONFIT=202,
    DUSJSHOWERCOMPLETEFIT=203,
    DUSJSHOWEREND=299,
    AANET_RECONSTRUCTION_TYPE=101,
    AASHOWERBEGIN=300,
    AASHOWERFITPREFIT=302,
    AASHOWERFITPOSITIONFIT=303,
    AASHOWERFITDIRECTIONENERGYFIT=304,
    AASHOWEREND=399,
    JUSERBEGIN=1000,
    JMUONVETO=1001,
    JMUONPATH=1003,
    JMCEVT=1004,
    JUSEREND=1099,
    RECTYPE_UNKNOWN=-1,
    RECSTAGE_UNKNOWN=-1,
)
