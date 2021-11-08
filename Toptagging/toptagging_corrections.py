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

# this script depends on the 'infile' name. The root file should be inside this folder and is calles 'YEAR_TopTaggingScaleFactors.root'
# it runs over three modes 'mergedTop', 'semimerged', 'notmerged'


def create_corr(year_="UL17"):
    correction_dict ={}
    for i in range(1):
        postfix = ""
        if i==1:
            postfix = "_NoMassCut"
        #TopTaggingScaleFactors_RunIISummer19UL17_PUPPIv15.root
        infile = 'TopTaggingScaleFactors_RunIISummer19'+year_+'_PUPPIv15'+postfix+'.root'
        
        print("working on " + infile)
        inputFile = ROOT.TFile.Open(infile)
        
        modes = ['FullyMerged', 'NotMerged']
    
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
            wp_string = ""
            for ih in listOfHistos:

                histname = mode+"_tot"
                tmpHistos[ih] = inputFile.Get(ih+"/"+histname)
        
                wp=""
                if "HOTVR" in ih: wp = "HOTVR"
                else:
                    wp =[ x for x in ih.split('_') if x.startswith("wp")]
                    wp = wp[0] if len(wp) else "wp1"
                tag = [ x for x in ih.split('_') if x.startswith(("v","l","m","t"))]
                tag = "_"+tag[0] if len(tag) else ""
                taucut = [ x[2:] for x in ih.split('_') if x.startswith(("wp"))]
                taucut = taucut[0] if len(taucut) else ""
                misid = [ x for x in ih.split('_') if x.startswith(("mis"))]
                misid = misid[0] if len(misid) else ""
                wp+=tag
                if "btag" in ih: wp+="_btag"
           
                if "btag" not in wp:
                    if "HOTVR" in wp:
                        wp_string+= wp+f"(tau32<0.56), "
                    else:
                        wp_string+= wp+f"[_btag](tau32<{taucut.replace('p','.')}, {tag[1:]}, mis = {misid.replace('mis','').replace('p','.')}), "

                for ix in range( tmpHistos[ih].GetN() ):      
                    dataInfo['workingPoint'].append(wp)
                    x = ctypes.c_double(0.)
                    y = ctypes.c_double(0.)
                    tmpHistos[ih].GetPoint(ix,x,y)
                    dataInfo['ptMin'].append(x.value-tmpHistos[ih].GetErrorXlow(ix) )
                    dataInfo['ptMax'].append(x.value+tmpHistos[ih].GetErrorXhigh(ix) )
                    dataInfo['scaleFactor'].append(y.value )
                    dataInfo['Object'].append(ih )
                    dataInfo['scaleFactorSystUncty_up'].append(y.value+tmpHistos[ih].GetErrorYhigh(ix) )
                    dataInfo['scaleFactorSystUncty_down'].append(y.value-tmpHistos[ih].GetErrorYlow(ix) )

                ###### adding one last bin until pT~inf to keept the last SF
                dataInfo['workingPoint'].append(wp)
                x = ctypes.c_double(0.)
                y = ctypes.c_double(0.)
                tmpHistos[ih].GetPoint(tmpHistos[ih].GetN()-1,x,y)
                dataInfo['ptMin'].append(x.value+tmpHistos[ih].GetErrorXlow(tmpHistos[ih].GetN()-1) )
                dataInfo['ptMax'].append(float('inf') )
                dataInfo['scaleFactor'].append(y.value )
                dataInfo['Object'].append(ih )
                dataInfo['scaleFactorSystUncty_up'].append(y.value+tmpHistos[ih].GetErrorYhigh(tmpHistos[ih].GetN()-1) )
                dataInfo['scaleFactorSystUncty_down'].append(y.value-tmpHistos[ih].GetErrorYlow(tmpHistos[ih].GetN()-1) )

        

            dataInfo['year'] = [ year_ for el in dataInfo["scaleFactor"]]
            if "16" in year_:
                dataInfo['etaMin'] = ["-2.4" for el in dataInfo["scaleFactor"]]
                dataInfo['etaMax'] = ["2.4" for el in dataInfo["scaleFactor"]]
            else:
                dataInfo['etaMin'] = ["-2.5" for el in dataInfo["scaleFactor"]]
                dataInfo['etaMax'] = ["2.5" for el in dataInfo["scaleFactor"]]
                
             
                
            df = pd.DataFrame( dataInfo )
            # df['ptMin'] = df['ptMin'].astype(int)
            # df['ptMax'] = df['ptMax'].astype(int)
            df['ptMin'] = df['ptMin'].astype(float)
            df['ptMax'] = df['ptMax'].astype(float)

        
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
                        # TODO: change the WP, add misidentification and tau requirement
                        {"name": "workingpoint", "type": "string", 'description': 'Working point of the tagger you use [with DeepCSV loose]: '+wp_string+' (from https://twiki.cern.ch/twiki/bin/view/CMS/JetTopTagging)'}
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


#create_corr("UL16")
create_corr("UL17")
create_corr("UL18")

from correctionlib import _core

#Download the correct JSON files 
evaluator = _core.CorrectionSet.from_file('UL17_Toptagging.json')

valsf= evaluator["Top_tagging_PUPPI_FullyMerged"].evaluate(2.0,450.,"nom","wp0p38_vt")
print("sf is:"+str(valsf))

valsf= evaluator["Top_tagging_PUPPI_FullyMerged"].evaluate(2.0,450.,"up","wp0p38_vt")
print("sf up is:"+str(valsf))

valsf= evaluator["Top_tagging_PUPPI_FullyMerged"].evaluate(2.0,450.,"down","wp0p38_vt")
print("sf down is:"+str(valsf))

###### testing special cases
print("testing out of pT range: pT>1000 GeV")
valsf= evaluator["Top_tagging_PUPPI_FullyMerged"].evaluate(2.0,2000.,"nom","wp0p38_vt")
print("sf is:"+str(valsf))

# print("testing out of pT range: pT<200 GeV")
# valsf= evaluator["Top_tagging_PUPPI_FullyMerged"].evaluate(2.0,200.,"nom","wp0p38_vt")
# print("sf is:"+str(valsf))
