import pandas as pd
import numpy as np
from collections import OrderedDict
from correctionlib.schemav1 import Correction, Binning, Category, Formula
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import helperfunctions as hf
from correctionlib.schemav1 import CorrectionSet
import gzip
import ROOT

bprintouts=True

infile = '2016TopTaggingScaleFactors.root'

inputFile = ROOT.TFile.Open(infile)

listOfHistos = []
for i in inputFile.GetListOfKeys(): 
    listOfHistos.append(i.GetName())
    print(i)



dataInfo = OrderedDict()
dataInfo['Object'] = []
dataInfo['workingPoint'] = []
dataInfo['ptMin'] = []
dataInfo['ptMax'] = []
dataInfo['scaleFactor'] = []
#dataInfo['scaleFactorSystUncty_up'] = []
#dataInfo['scaleFactorSystUncty_down'] = []


def create_corr(mode="mergedTop",year_="2016"):
    tmpHistos ={}
    for ih in listOfHistos:
        if "HOTVR" in ih: continue
        histname = "sf_"+mode+"_nominal"
        tmpHistos[ih] = inputFile.Get(ih+"/"+histname)

        # tmpHistos[ih+'_Systuncty'] = inputFile.Get(ih+'_Systuncty')
        wp =[ x for x in ih.split('_') if x.startswith("wp")]
        wp = wp[0] if len(wp) else "wp1"
        if "btag" in ih: wp+="_btag"
        for ix in range( tmpHistos[ih].GetNbinsX()+2 ):      #### plus 2 for overflows
            dataInfo['workingPoint'].append(wp)
            dataInfo['ptMin'].append(tmpHistos[ih].GetXaxis().GetBinLowEdge(ix) )
            dataInfo['ptMax'].append(tmpHistos[ih].GetXaxis().GetBinUpEdge(ix) )
            dataInfo['scaleFactor'].append(tmpHistos[ih].GetBinContent(ix) )
            dataInfo['Object'].append(ih )
            #dataInfo['scaleFactorSystUncty'].append(tmpHistos[ih+'_Systuncty'].GetBinContent(ix,iy) )


    dataInfo['valueType'] = ["effciency" for el in dataInfo["scaleFactor"]]
    dataInfo['year'] = [ year_ for el in dataInfo["scaleFactor"]]
    dataInfo['etaMin'] = ["-2.4" for el in dataInfo["scaleFactor"]]
    dataInfo['etaMax'] = ["2.4" for el in dataInfo["scaleFactor"]]
     
        
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
            "name": "Top tagging "+mode + " "+ year_,
            "description": "Scale factor for DeepAK8 algorithm (nominal and mass decorrelated)",
            "inputs": [
                {"name": "year", "type": "string", 'description': 'Data taking dataset'},
                {"name": "workingPoint", "type": "string", 'description': 'WP: Mistaggin rate of '},
                {"name": "valueType", "type": "string", "description": "Efficiency or misstag"},
                {"name": "eta", "type": "real"},
                {"name": "pt", "type": "real"},
                {"name": "scaleFactor", "type": "real", "description": "Scale Factor"},
            ],
            "output": {"name": "weight", "type": "real"},
            "data": hf.build_year(df),
        }
    )
    
    print(corr_toptagging)
    cset = CorrectionSet.parse_obj({
        "schema_version": 1,
        "corrections": [
            corr_toptagging    ]
    })
    cset.json()
    with open('Corr_Toptagging_'+mode+"_"+year_+'.json', "w") as fout:
        fout.write(cset.json(exclude_unset=True, indent=4))


create_corr()
