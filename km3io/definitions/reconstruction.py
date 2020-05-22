# -*- coding: utf-8 -*-
"""
KM3NeT Data Definitions v1.1.2
https://git.km3net.de/common/km3net-dataformat
"""

# reconstruction
data = {
    "JPP_RECONSTRUCTION_TYPE": 4000,
    "JMUONFIT": 0,
    "JMUONBEGIN": 0,
    "JMUONPREFIT": 1,
    "JMUONSIMPLEX": 2,
    "JMUONGANDALF": 3,
    "JMUONENERGY": 4,
    "JMUONSTART": 5,
    "JLINEFIT": 6,
    "JMUONEND": 99,
    "JSHOWERFIT": 100,
    "JSHOWERBEGIN": 100,
    "JSHOWERPREFIT": 101,
    "JSHOWERPOSITIONFIT": 102,
    "JSHOWERCOMPLETEFIT": 103,
    "JSHOWER_BJORKEN_Y": 104,
    "JSHOWEREND": 199,
    "DUSJSHOWERFIT": 200,
    "DUSJBEGIN": 200,
    "DUSJPREFIT": 201,
    "DUSJPOSITIONFIT": 202,
    "JDUSJCOMPLETEFIT": 203,
    "DUSJEND": 299,
    "AASHOWERFIT": 300,
    "AASHOWERBEGIN": 300,
    "AASHOWERCOMPLETEFIT": 301,
    "AASHOWEREND": 399,
    "JUSERBEGIN": 1000,
    "JMUONVETO": 1001,
    "JMUONPATH": 1003,
    "JMCEVT": 1004,
    "JUSEREND": 1099,
    "RECTYPE_UNKNOWN": -1,
    "RECSTAGE_UNKNOWN": -1,
}

data_r = {v: k for k, v in data.items()}
