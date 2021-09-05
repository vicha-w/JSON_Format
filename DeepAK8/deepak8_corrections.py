import pandas as pd
import numpy as np
from collections import OrderedDict
from correctionlib.schemav2 import Correction, Binning, Category, Formula, CorrectionSet
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import helperfunctionsv2 as hf
import gzip

bprintouts=False

infile = 'DeepAK8V2_Top_W_SFs.csv'
print("Read in "+infile)

data = pd.read_csv(infile, names=['Object','Year','version','MistaggingRate','pT_low','pT_high','SF','SF_lowerErr','SF_upperErr'],skipinitialspace=True)

data = data.iloc[1: , :]
if bprintouts: 
    print("Head of the CSV file that is read in")
    print(data.head())



dataInfo = OrderedDict()
dataInfo['Object'] = data.Object.values.tolist()
dataInfo['workingPoint'] = data.MistaggingRate.values.tolist()
dataInfo['year'] = data.Year.values.tolist()
dataInfo['valueType'] = data.version.values.tolist()
dataInfo['ptMin'] = data.pT_low.values.tolist()
dataInfo['ptMax'] = data.pT_high.values.tolist()
dataInfo['etaMin'] = ["-2.4" for el in data.pT_high.values.tolist()]
dataInfo['etaMax'] = ["2.4" for el in data.pT_high.values.tolist()]
dataInfo['scaleFactor'] = data.SF.values.tolist()
dataInfo['scaleFactorSystUncty_up'] = data.SF_lowerErr.values.tolist()
dataInfo['scaleFactorSystUncty_down'] = data.SF_upperErr.values.tolist()



df = pd.DataFrame( dataInfo )
df['ptMin'] = df['ptMin'].astype(int)
df['ptMax'] = df['ptMax'].astype(int)
df['scaleFactor'] = df['scaleFactor'].astype(float)
df['scaleFactorSystUncty_up'] = df['scaleFactorSystUncty_up'].astype(float)
df['scaleFactorSystUncty_down'] = df['scaleFactorSystUncty_down'].astype(float)

if bprintouts: 
    print("Printing the data structure")
    print(df)


#csv file has two particle W and top
def create_corr(particle="Top",year_="2016"):
    keys = df["valueType"].unique()
    if bprintouts: print(keys)

    correction_dict = {}

    for valuetype in keys:
        df_part = df[df["Object"]==particle]
        df_part =df_part[df_part["year"]==year_]
        df_part = df_part[df_part["valueType"]==valuetype]
            
        print("Create data struction in json format")
    
        corr_deepak8_part = Correction.parse_obj(
        {
            "version": 1,
            "name": "DeepAK8_"+particle+"_"+valuetype,
            "description": "Scale factor for DeepAK8 algorithm (nominal and mass decorrelated) for particle "+particle,
            "inputs": [
                {"name": "eta", "type": "real"},
                {"name": "pt", "type": "real"},
                {"name": "systematic", "type": "string"},
                {"name": "workingpoint", "type": "string"}
            ],
            "output": {"name": "weight", "type": "real"},
            "data": hf.build_systs(df_part),
        }
    )
        
        if bprintouts: print(corr_deepak8_part)
        correction_dict[valuetype] = corr_deepak8_part


    cset = CorrectionSet.parse_obj({
        "schema_version": 2,
        "corrections": [
            correction_dict[key] for key in correction_dict    ]
    })
    cset.json()
    with open(year_+'_DeepAK8_'+particle+'.json', "w") as fout:
        fout.write(cset.json(exclude_unset=True, indent=4))
        
    

create_corr("Top", "2016")
create_corr("W","2016")

create_corr("Top","2017")
create_corr("W","2017")

create_corr("Top","2018")
create_corr("W","2018")



from correctionlib import _core

#Download the correct JSON files 
evaluator = _core.CorrectionSet.from_file('2016_DeepAK8_Top.json')

valsf= evaluator["DeepAK8_Top_Nominal"].evaluate(2.0,450.,"nom","0p1")
print("sf is:"+str(valsf))

valsf= evaluator["DeepAK8_Top_Nominal"].evaluate(2.0,450.,"up","0p1")
print("sf up is:"+str(valsf))

valsf= evaluator["DeepAK8_Top_Nominal"].evaluate(2.0,450.,"down","0p1")
print("sf down is:"+str(valsf))

