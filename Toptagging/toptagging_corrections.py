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

# this script depends on the 'infile' name. The root file should be inside this folder and is calles 'YEAR_TopTaggingScaleFactors.root'
# it runs over three modes 'mergedTop', 'semimerged', 'notmerged'


def create_corr(year_="2016"):
    correction_dict ={}
    for i in range(2):
        postfix = ""
        if i==1:
            postfix = "_NoMassCut"

        infile = year_+'TopTaggingScaleFactors'+postfix+'.root'
        
        print("working on " + infile)
        inputFile = ROOT.TFile.Open(infile)
        
        modes = ['mergedTop', 'semimerged', 'notmerged']
    
        listOfHistos = []
        if bprintouts: print("List of Workingpoints that are considered")
        for i in inputFile.GetListOfKeys(): 
            listOfHistos.append(i.GetName())
            if bprintouts: print(i)
        
        
        for mode in modes:
    
            dataInfo = OrderedDict()
            dataInfo['Object'] = []
            dataInfo['workingPoint'] = []
            dataInfo['ptMin'] = []
            dataInfo['ptMax'] = []
            dataInfo['scaleFactor'] = []
            dataInfo['scaleFactorSystUncty_up'] = []
            dataInfo['scaleFactorSystUncty_down'] = []
    
            tmpHistos ={}
            tmpHistos_up ={}
            tmpHistos_down ={}
            for ih in listOfHistos:

                histname = "sf_"+mode+"_nominal"
                tmpHistos[ih] = inputFile.Get(ih+"/"+histname)
                tmpHistos_up[ih] = inputFile.Get(ih+"/"+histname.replace("nominal","up"))
                tmpHistos_down[ih] = inputFile.Get(ih+"/"+histname.replace("nominal","down"))
        
                wp=""
                if "HOTVR" in ih: wp = "HOTVR"
                else:
                    wp =[ x for x in ih.split('_') if x.startswith("wp")]
                    wp = wp[0] if len(wp) else "wp1"
                if "btag" in ih: wp+="_btag"
                for ix in range( tmpHistos[ih].GetNbinsX()+2 ):      #### plus 2 for overflows
                    dataInfo['workingPoint'].append(wp)
                    dataInfo['ptMin'].append(tmpHistos[ih].GetXaxis().GetBinLowEdge(ix) )
                    dataInfo['ptMax'].append(tmpHistos[ih].GetXaxis().GetBinUpEdge(ix) )
                    dataInfo['scaleFactor'].append(tmpHistos[ih].GetBinContent(ix) )
                    dataInfo['Object'].append(ih )
                    dataInfo['scaleFactorSystUncty_up'].append(tmpHistos_up[ih].GetBinContent(ix) )
                    dataInfo['scaleFactorSystUncty_down'].append(tmpHistos_down[ih].GetBinContent(ix) )
        
        
            dataInfo['year'] = [ year_ for el in dataInfo["scaleFactor"]]
            if "16" in year_:
                dataInfo['etaMin'] = ["-2.4" for el in dataInfo["scaleFactor"]]
                dataInfo['etaMax'] = ["2.4" for el in dataInfo["scaleFactor"]]
            else:
                dataInfo['etaMin'] = ["-2.5" for el in dataInfo["scaleFactor"]]
                dataInfo['etaMax'] = ["2.5" for el in dataInfo["scaleFactor"]]
                
             
                
            df = pd.DataFrame( dataInfo )
            df['ptMin'] = df['ptMin'].astype(int)
            df['ptMax'] = df['ptMax'].astype(int)
            
        
            if bprintouts: 
                print("Printing the data structure")
                print(df)
        
            print("Create data struction in json format")
            corr_toptagging = Correction.parse_obj(
                {
                    "version": 1,
                    "name": "Top_tagging_PUPPI_"+mode+postfix,
                    "description": "Scale factor for Top tagging algorithm",
                    "inputs": [
                {"name": "eta", "type": "real", "description": "eta of the jet"},
                {"name": "pt", "type": "real", "description": "pT of the jet"},
                {"name": "systematic", "type": "string", "description": "systematics: nom, up, down"},
                        {"name": "workingpoint", "type": "string", 'description': 'Working point of the tagger you use'}
                    ],
                    "output": {"name": "weight", "type": "real"},
                    "data": hf.build_systs(df, False),
                }
            )
            
            if bprintouts: print(corr_toptagging)
            correction_dict[mode+postfix] = corr_toptagging
    

    cset = CorrectionSet.parse_obj({
        "schema_version": 2,
        "corrections": [
            correction_dict[key] for key in correction_dict    ]
    })
    cset.json()
    with open(year_+'_Toptagging.json', "w") as fout:
        fout.write(cset.json(exclude_unset=True, indent=4))


create_corr("2016")
create_corr("2017")
create_corr("2018")

from correctionlib import _core

#Download the correct JSON files 
evaluator = _core.CorrectionSet.from_file('2016_Toptagging.json')

valsf= evaluator["Top_tagging_PUPPI_mergedTop"].evaluate(2.0,450.,"nom","wp1")
print("sf is:"+str(valsf))

valsf= evaluator["Top_tagging_PUPPI_mergedTop"].evaluate(2.0,450.,"up","wp1")
print("sf up is:"+str(valsf))

valsf= evaluator["Top_tagging_PUPPI_mergedTop"].evaluate(2.0,450.,"down","wp1")
print("sf down is:"+str(valsf))
