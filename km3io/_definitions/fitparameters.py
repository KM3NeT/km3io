# -*- coding: utf-8 -*-
"""
KM3NeT Data Definitions v2.0.0
https://git.km3net.de/common/km3net-dataformat
"""

# fitparameters
data = dict(
    #jmuon chain
    JGANDALF_BETA0_RAD=0,
    JGANDALF_BETA1_RAD=1,
    JGANDALF_CHI2=2,
    JGANDALF_NUMBER_OF_HITS=3,
    JENERGY_ENERGY=4,
    JENERGY_CHI2=5,
    JGANDALF_LAMBDA=6,
    JGANDALF_NUMBER_OF_ITERATIONS=7,
    JSTART_NPE_MIP=8,
    JSTART_NPE_MIP_TOTAL=9,
    JSTART_LENGTH_METRES=10,
    JVETO_NPE=11,
    JVETO_NUMBER_OF_HITS=12,
    JENERGY_MUON_RANGE_METRES=13,
    JENERGY_NOISE_LIKELIHOOD=14,
    JENERGY_NDF=15,
    JENERGY_NUMBER_OF_HITS=16,
    JCOPY_Z_M=17,
    
    #jshowerfit chain
    JSHOWERFIT_ENERGY=4,

    #aashowerfit chain
    AASHOWERFIT_ENERGY=0,
    AASHOWERFIT_NUMBER_OF_HITS=1,
)
