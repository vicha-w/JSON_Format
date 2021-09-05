import pandas as pd
import numpy as np
from collections import OrderedDict
from correctionlib.schemav2 import Correction, Binning, Category, Formula, CorrectionSet
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import helperfunctionsv2 as hf
import gzip

bprintouts=False

formular_nom = "(2.5626*x^3 - 3.2240*x^2 + 1.8687*x + 0.6770)"


def create_corr(year_="2016"):
    dataInfo = OrderedDict()
    dataInfo['ptMin'] = [0,30]
    dataInfo['ptMax'] = [30,1000]
    dataInfo['etaMin'] = ["-2.0" for el in dataInfo['ptMax']]
    dataInfo['etaMax'] = ["2.0" for el in dataInfo['ptMax']] 
    dataInfo['discrMin'] = ["0." for el in dataInfo['ptMax']]
    dataInfo['discrMax'] = ["1.0" for el in dataInfo['ptMax']] 
    dataInfo['formula'] = [formular_nom,formular_nom]
    diff = "abs("+formular_nom+" - 1)"
    dataInfo['formula_up'] = [formular_nom+"*(1+2*("+diff+"))",formular_nom +"*(1+"+diff+")"]
    dataInfo['formula_down'] = [formular_nom+"*(1-2*("+diff+"))",formular_nom +"*(1-"+diff+")"]
    
    
    df = pd.DataFrame( dataInfo )
    df['ptMin'] = df['ptMin'].astype(int)
    df['ptMax'] = df['ptMax'].astype(int)
    df['etaMin'] = df['ptMin'].astype(float)
    df['etaMax'] = df['ptMax'].astype(float)
    
    corr_qg_part = Correction.parse_obj(
        {
            "version": 1,
            "name": "Gluon_Pythia",
            "description": "Scale factor for gluons in pythia",
            "inputs": [
                {"name": "eta", "type": "real"},
                {"name": "pt", "type": "real"},
                {"name": "systematic", "type": "string"},
                {"name": "discriminant", "type": "real"}
            ],
            "output": {"name": "weight", "type": "real"},
            "data": hf.build_systs_formular(df),
    }
        )
    
    if bprintouts: print(corr_qg_part)
    
    
    
    cset = CorrectionSet.parse_obj({
    "schema_version": 2,
        "corrections": [
        corr_qg_part    ]
    })
    cset.json()
    with open(year_+'_QuarkGluon.json', "w") as fout:
        fout.write(cset.json(exclude_unset=True, indent=4))
        
    
        
create_corr("2016")
create_corr("2017")
create_corr("2018")

from correctionlib import _core

#Download the correct JSON files 
evaluator = _core.CorrectionSet.from_file('2016_QuarkGluon.json')

valsf= evaluator["Gluon_Pythia"].evaluate(1.0,20.,"nom",0.5)
print("sf is:"+str(valsf))

valsf= evaluator["Gluon_Pythia"].evaluate(1.0,20.,"up",0.5)
print("sf up is:"+str(valsf))

valsf= evaluator["Gluon_Pythia"].evaluate(1.0,20.,"down",0.5)
print("sf down is:"+str(valsf))

