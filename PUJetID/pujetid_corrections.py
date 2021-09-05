import pandas as pd
import numpy as np
from collections import OrderedDict
from correctionlib.schemav2 import Correction, Binning, Category, Formula, CorrectionSet
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import helperfunctionsv2 as hf
import gzip
import ROOT

bprintouts=False

infile = "PUID_80XTraining_EffSFandUncties.root"

def create_corr(year= "2016"):
    print("working on "+infile)
    inputFile = ROOT.TFile.Open(infile)

    correction_dict = {}
    for imiseff in range(2):
        miseff = "eff"
        if imiseff==1: miseff = "mis"
        
        listOfHistos = []
        if bprintouts: print("List of Workingpoints that are considered")
        for i in inputFile.GetListOfKeys(): 
            if "sf" not in i.GetName(): continue
            if "uncty" in i.GetName(): continue
            if year not in i.GetName(): continue
            if miseff not in i.GetName(): continue
            listOfHistos.append(i.GetName())
            if bprintouts: print(i)
   
        dataInfo = OrderedDict()
        dataInfo['Object'] = []
        dataInfo['workingPoint'] = []
        dataInfo['ptMin'] = []
        dataInfo['ptMax'] = []
        dataInfo['etaMin'] = []
        dataInfo['etaMax'] = []
        dataInfo['scaleFactor'] = []
        dataInfo['scaleFactorSystUncty_up'] = []
        dataInfo['scaleFactorSystUncty_down'] = []
        
        tmpHistos ={}
        tmpHistos_up ={}
        tmpHistos_down ={}
        for ih in listOfHistos:
            
            tmpHistos[ih] = inputFile.Get(ih)
            tmpHistos_up[ih] = inputFile.Get(ih+"_Systuncty")
            tmpHistos_down[ih] = inputFile.Get(ih+"_Systuncty")
            
            wp =ih.split('_')[-1:][0]
            print(wp)
            
    
            for ix in range( tmpHistos[ih].GetNbinsX()+2 ):      #### plus 2 for overflows
                for iy in range(tmpHistos[ih].GetNbinsY()+2):
                    dataInfo['workingPoint'].append(wp)
                    dataInfo['ptMin'].append(tmpHistos[ih].GetXaxis().GetBinLowEdge(ix) )
                    dataInfo['ptMax'].append(tmpHistos[ih].GetXaxis().GetBinUpEdge(ix) )
                    dataInfo['etaMin'].append(tmpHistos[ih].GetYaxis().GetBinLowEdge(iy) )
                    dataInfo['etaMax'].append(tmpHistos[ih].GetYaxis().GetBinUpEdge(iy) )
    
                    dataInfo['scaleFactor'].append(tmpHistos[ih].GetBinContent(ix,iy) )
                    dataInfo['Object'].append(ih )
                    dataInfo['scaleFactorSystUncty_up'].append(tmpHistos_up[ih].GetBinContent(ix,iy) )
                    dataInfo['scaleFactorSystUncty_down'].append(tmpHistos_down[ih].GetBinContent(ix,iy) )
            
            
        df = pd.DataFrame( dataInfo )
        df['ptMin'] = df['ptMin'].astype(float)
        df['ptMax'] = df['ptMax'].astype(float)
        df['etaMin'] = df['etaMin'].astype(float)
        df['etaMax'] = df['etaMax'].astype(float)
    
                
            
        if bprintouts: 
            print("Printing the data structure")
            print(df)
    
        print("Create data struction in json format")
        corr_pujetid = Correction.parse_obj(
            {
                "version": 1,
                "name": "PUJetID_"+miseff,
                "description": "Scale factor for PUJetID algorithm",
                "inputs": [
                    {"name": "eta", "type": "real"},
                    {"name": "pt", "type": "real"},
                    {"name": "systematic", "type": "string"},
                    {"name": "workingpoint", "type": "string", 'description': 'WP: Mistaggin rate of '}
                ],
                "output": {"name": "weight", "type": "real"},
                "data": hf.build_systs(df, True),
            }
        )
    
        if bprintouts: print(corr_pujetid)
        correction_dict[miseff] = corr_pujetid
 
    cset = CorrectionSet.parse_obj({
        "schema_version": 2,
        "corrections": [
            correction_dict[key] for key in correction_dict    ]
    })
    cset.json()
    with open(year+'_PUJetID.json', "w") as fout:
        fout.write(cset.json(exclude_unset=True, indent=4))
 


create_corr("2016")
create_corr("2017")
create_corr("2018")


from correctionlib import _core

#Download the correct JSON files 
evaluator = _core.CorrectionSet.from_file('2016_PUJetID.json')

valsf= evaluator["PUJetID_eff"].evaluate(-4.5,20.,"nom","L")
print("sf is:"+str(valsf))

valsf= evaluator["PUJetID_eff"].evaluate(-4.5,20.,"up","L")
print("sf up is:"+str(valsf))

valsf= evaluator["PUJetID_eff"].evaluate(-4.5,20.,"down","L")
print("sf down is:"+str(valsf))

