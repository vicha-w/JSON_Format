import pandas as pd
import numpy as np
from collections import OrderedDict
from correctionlib.schemav2 import Correction, Binning, Category, Formula, CorrectionSet
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import helperfunctionsv2 as hf
import gzip
import ROOT
import ctypes

bprintouts=False

###
#
# This script, does not yet provid an uncertainty. The syst 'up'/'down' will just be the nominal value
#
###

def create_corr(year):
    infile = "puppiCorr.root"
    
    inputFile = ROOT.TFile.Open(infile)
    

    histname_central = "puppiJECcorr_reco_0eta1v3"
    histname_forward = "puppiJECcorr_reco_1v3eta2v5"
    histname_gen = "puppiJECcorr_gen"

    hist_central = inputFile.Get(histname_central)
    hist_forward = inputFile.Get(histname_forward)
    hist_gen = inputFile.Get(histname_gen)

    result_string_central = hist_central.GetTitle()
    result_string_forward = hist_forward.GetTitle()
    result_string_gen = hist_gen.GetTitle()

    for ipar in range(0,hist_central.GetNpar()): result_string_central = result_string_central.replace("["+str(ipar)+"]",str(hist_central.GetParameter(ipar)))
    for ipar in range(0,hist_forward.GetNpar()): result_string_forward = result_string_forward.replace("["+str(ipar)+"]",str(hist_forward.GetParameter(ipar)))
    for ipar in range(0,hist_gen.GetNpar()): result_string_gen = result_string_gen.replace("["+str(ipar)+"]",str(hist_gen.GetParameter(ipar)))

    result_central = ROOT.TF1("central","("+result_string_central+")*("+result_string_gen+")")
    result_forward = ROOT.TF1("forward","("+result_string_forward+")*("+result_string_gen+")")
    
    dataInfo = OrderedDict()
    if "2016" in year:
        dataInfo['etaMin'] = ['-2.4','-1.3','1.3']
        dataInfo['etaMax'] = ['-1.3','1.3','2.4']
    else:
        dataInfo['etaMin'] = ['-2.5','-1.3','1.3']
        dataInfo['etaMax'] = ['-1.3','1.3','2.5']

    xmax, xmin = ctypes.c_double(0),ctypes.c_double(0)
    hist_central.GetRange(xmin,xmax)
    dataInfo['ptMin'] = [xmin.value for el in dataInfo['etaMin']]
    dataInfo['ptMax'] = [xmax.value for el in dataInfo['etaMin']]

    dataInfo['formula'] = [result_string_forward, result_string_central, result_string_forward]


    df = pd.DataFrame( dataInfo )
    df['ptMin'] = df['ptMin'].astype(int)
    df['ptMax'] = df['ptMax'].astype(int)
    df['etaMin'] = df['etaMin'].astype(float)
    df['etaMax'] = df['etaMax'].astype(float)
    
    corr_softdrop_part = Correction.parse_obj(
        {
            "version": 1,
            "name": "JMS",
            "description": "SoftDrop mass scale correction",
            "inputs": [
                {"name": "eta", "type": "real", "description": "eta of the jet"},
                {"name": "pt", "type": "real", "description": "pT of the jet"},
                {"name": "systematic", "type": "string", "description": "systematics: nom, up, down"},
               
            ],
            "output": {"name": "weight", "type": "real"},
            "data": hf.build_systs_formular(df,False),
    }
        )
    
    if bprintouts: print(corr_softdrop_part)


    cset = CorrectionSet.parse_obj({
    "schema_version": 2,
        "corrections": [
        corr_softdrop_part    ]
    })
    cset.json()
    with open(year+'_softdrop.json', "w") as fout:
        fout.write(cset.json(exclude_unset=True, indent=4))
        
    
        
create_corr("2016")
create_corr("2017")
create_corr("2018")

from correctionlib import _core

#Download the correct JSON files 
evaluator = _core.CorrectionSet.from_file('2016_softdrop.json')

valsf= evaluator["JMS"].evaluate(1.0,200.,"nom")
print("sf is:"+str(valsf))

valsf= evaluator["JMS"].evaluate(1.0,200.,"up")
print("sf up is:"+str(valsf))

valsf= evaluator["JMS"].evaluate(1.0,200.,"down")
print("sf down is:"+str(valsf))

