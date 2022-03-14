#!/usr/bin/env python3
data = {
    "DAQ": "livetime",
    "seed": "program level iseed",
    "PM1_type_area": "type area TTS",
    "PDF": "i1 i2",
    "model": "interaction muon scattering numberOfEnergyBins",
    "can": "zmin zmax r",
    "genvol": "zmin zmax r volume numberOfEvents",
    "merge": "time gain",
    "coord_origin": "x y z",
    "translate": "x y z",
    "genhencut": "gDir Emin",
    "k40": "rate time",
    "norma": "primaryFlux numberOfPrimaries",
    "livetime": "numberOfSeconds errorOfSeconds",
    "flux": "type key file_1 file_2",
    "spectrum": "alpha",
    "fixedcan": "xcenter ycenter zmin zmax radius",
    "start_run": "run_id",
}

for key in "cut_primary cut_seamuon cut_in cut_nu".split():
    data[key] = "Emin Emax cosTmin cosTmax"

for key in "generator physics simul".split():
    data[key] = "program version date time"

for key in data.keys():
    data[key] = data[key].split()
