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

infile = "PUID_106XTraining_ULRun2_EffSFandUncties_v1.root"

def create_corr(year= "2016"):
    print("working on "+infile)
    inputFile = ROOT.TFile.Open(infile)

    correction_dict = {}
    for imiseff in range(1):
        miseff = "eff"
#        if imiseff==1: miseff = "mis"
        
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
        dataInfo['MCEff'] = []
        
        tmpHistos ={}
        tmpHistos_up ={}
        tmpHistos_down ={}
        tmpHistos_MCEff ={}
        for ih in listOfHistos:
            
            tmpHistos[ih] = inputFile.Get(ih)
            tmpHistos_up[ih] = inputFile.Get(ih+"_Systuncty")
            tmpHistos_down[ih] = inputFile.Get(ih+"_Systuncty")
            tmpHistos_MCEff[ih] = inputFile.Get(ih.replace("sf","mc"))
            print (ih.replace("sf","mc"))
            
            wp =ih.split('_')[-1:][0]
            print(wp)
            
    
            for ix in range( tmpHistos[ih].GetNbinsX()+2 ):      #### plus 2 for overflows
                for iy in range(tmpHistos[ih].GetNbinsY()+2):
                    dataInfo['workingPoint'].append(wp)
                    dataInfo['ptMin'].append(tmpHistos[ih].GetXaxis().GetBinLowEdge(ix) )
                    dataInfo['ptMax'].append(tmpHistos[ih].GetXaxis().GetBinUpEdge(ix) )
                    dataInfo['etaMin'].append(tmpHistos[ih].GetYaxis().GetBinLowEdge(iy) )
                    dataInfo['etaMax'].append(tmpHistos[ih].GetYaxis().GetBinUpEdge(iy) )
    
                    if tmpHistos[ih].GetXaxis().GetBinLowEdge(ix) >= 50:
                        dataInfo['scaleFactor'].append(1 )
                    else:
                        dataInfo['scaleFactor'].append(tmpHistos[ih].GetBinContent(ix,iy) )
                    dataInfo['Object'].append(ih )
                    dataInfo['scaleFactorSystUncty_up'].append(tmpHistos_up[ih].GetBinContent(ix,iy) )
                    dataInfo['scaleFactorSystUncty_down'].append(tmpHistos_down[ih].GetBinContent(ix,iy) )
                    dataInfo['MCEff'].append(tmpHistos_MCEff[ih].GetBinContent(ix,iy) )
            
            
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
                "description": "Scale factor for PUJetID algorithm 80(80), 90(90) and 99(95)% efficiency for eta<2.5(>2.5) for quark jets",
                "inputs": [
                {"name": "eta", "type": "real", "description": "eta of the jet"},
                {"name": "pt", "type": "real", "description": "pT of the jet"},
                {"name": "systematic", "type": "string", "description": "systematics: nom, up, down, MCEff"},
                {"name": "workingpoint", "type": "string", "description": "Working point of the tagger you use"}
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
 


create_corr("UL2016_")
create_corr("UL2016APV")
create_corr("UL2017")
create_corr("UL2018")


from correctionlib import _core

#Download the correct JSON files 
evaluator = _core.CorrectionSet.from_file('UL2016__PUJetID.json')

valsf= evaluator["PUJetID_eff"].evaluate(-4.5,20.,"nom","L")
print("sf is:"+str(valsf))

valsf= evaluator["PUJetID_eff"].evaluate(-4.5,20.,"up","L")
print("sf up is:"+str(valsf))

valsf= evaluator["PUJetID_eff"].evaluate(-4.5,20.,"down","L")
print("sf down is:"+str(valsf))

valsf= evaluator["PUJetID_eff"].evaluate(-4.5,20.,"MCEff","L")
print("MCEff is:"+str(valsf))


valsf= evaluator["PUJetID_eff"].evaluate(-4.5,50.,"nom","L")
print("sf is:"+str(valsf))

valsf= evaluator["PUJetID_eff"].evaluate(-4.5,53.,"nom","L")
print("sf is:"+str(valsf))
