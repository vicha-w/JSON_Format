import pandas as pd
import numpy as np
from collections import OrderedDict
from correctionlib.schemav2 import Correction, Binning, Category, Formula, CorrectionSet
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import helperfunctionsv2 as hf
import gzip
import re

bprintouts=False

#######
#
# This script is only for EOY SF. For UL the json format will be produced as an output of the fitting code
#
######
import Run2SF 


dataInfo = OrderedDict()
dataInfo['workingPoint'] = [key for key in sorted(Run2SF.SF)]
dataInfo['year'] = [key[:4] for key in sorted(Run2SF.SF)]
dataInfo['ptMin'] = ['200' for el in dataInfo['workingPoint']]
dataInfo['ptMax'] = ['1000' for el in dataInfo['workingPoint']]
dataInfo['etaMin'] = ["-2.4" for el in dataInfo['workingPoint']]
dataInfo['etaMax'] = ["2.4" for el in dataInfo['workingPoint']]
dataInfo['scaleFactor'] = [Run2SF.SF[key] for key in sorted(Run2SF.SF)]
dataInfo['scaleFactorSystUncty_up'] =  [Run2SF.SFerrors[key] for key in sorted(Run2SF.SF)]
dataInfo['scaleFactorSystUncty_down'] = [Run2SF.SFerrors[key] for key in sorted(Run2SF.SF)]


df = pd.DataFrame( dataInfo )
df['ptMin'] = df['ptMin'].astype(int)
df['ptMax'] = df['ptMax'].astype(int)
df['scaleFactor'] = df['scaleFactor'].astype(float)
df['scaleFactorSystUncty_up'] = df['scaleFactorSystUncty_up'].astype(float)
df['scaleFactorSystUncty_down'] = df['scaleFactorSystUncty_down'].astype(float)

def create_corr(year = "2016"):

    correction_dict = {}

    for wp in df["workingPoint"].unique():
        if year not in wp: continue
        df_part = df[df["year"]==year]
        df_part = df_part[df_part["workingPoint"]==wp]

        print("Create data structure in json format")
        numbers = re.findall(r'\d+',wp)
        puppivschs="PUPPI"
        if "CHS" in wp: puppivschs="CHS"
        hpvslp="HP"
        if "LP" in wp: hpvslp="LP"
        tau21req = "no tau21 reqruiement"
        if len(numbers)>1:
            tau21req = "tau21<0."+str(numbers[1])
            if "LP"in wp: tau21req = "tau21>0."+str(numbers[1])
        taudecorr = ""
        if "DDT" in wp: 
            taudecorr="(decorrelated tau21 = tau21DDT)"
            tau21req = "tau21DDT" + tau21req[5:]
        description = "Scale factor for W tagging for "+taudecorr+" ("+wp+"): year="+str(numbers[0])+", "+hpvslp+", "+ tau21req+", "+puppivschs
        if "JMS" in wp: description = "Jet mass scale SF for "+year+" for wp "+wp+": "+taudecorr+" "+tau21req + " "+puppivschs
        if "JMR" in wp: description = "Jet mass resolution SF for "+year+" for wp "+wp+": "+taudecorr+" "+tau21req + " "+puppivschs
        print(description)

        corr_wtagging_part = Correction.parse_obj(
        {
            "version": 1,
            "name": "Wtagging_"+wp,
            "description": description,
            "inputs": [
                {"name": "eta", "type": "real", "description": "eta of the jet"},
                {"name": "pt", "type": "real", "description": "pT of the jet"},
                {"name": "systematic", "type": "string", "description": "systematics: nom, up, down"},
                {"name": "workingpoint", "type": "string", "description": "Working point of the tagger you use (tau21 requirement)"}
            ],
            "output": {"name": "weight", "type": "real"},
            "data": hf.build_systs(df_part),
        }
    )
        
        if bprintouts: print(corr_wtagging_part)
        correction_dict[wp] = corr_wtagging_part


    cset = CorrectionSet.parse_obj({
        "schema_version": 2,
        "corrections": [
            correction_dict[key] for key in correction_dict    ]
    })
    cset.json()
    with open(year+'_Wtagging.json', "w") as fout:
        fout.write(cset.json(exclude_unset=True, indent=4))
        


create_corr("2016")
create_corr("2017")
create_corr("2018")


from correctionlib import _core

#Download the correct JSON files 
evaluator = _core.CorrectionSet.from_file('2016_Wtagging.json')

valsf= evaluator["Wtagging_2016HP43DDT"].evaluate(2.0,450.,"nom","2016HP43DDT")
print("sf is:"+str(valsf))

valsf= evaluator["Wtagging_2016HP43DDT"].evaluate(2.0,450.,"up","2016HP43DDT")
print("sf up is:"+str(valsf))

valsf= evaluator["Wtagging_2016HP43DDT"].evaluate(2.0,450.,"down","2016HP43DDT")
print("sf down is:"+str(valsf))

