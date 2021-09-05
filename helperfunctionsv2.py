import pandas as pd
import numpy as np
from collections import OrderedDict
from correctionlib.schemav2 import Correction, Binning, Category, Formula



# 'unc' regulates if the scaleFactorSystUncty_up is an uncertainty or already the sf_up
# True: it is the uncertainty and in 'build_sf' we therefore need to add it to the sf
# False: it is already the SF_up so we do not need to add anything
def build_systs(sf,unc = True):
    return Category.parse_obj(
        {
            "nodetype": "category",
            "input": "systematic",
            "content": [
                {"key": "nom", "value": build_wp(sf)},
                {"key": "up", "value": build_wp(sf,syst="up",unc=unc)},
                {"key": "down", "value": build_wp(sf,syst="down",unc=unc)}
            ],
        }
    )


def build_wp(sf,syst = "nom",unc=True):
    keys = sorted(sf["workingPoint"].unique())
    return Category.parse_obj(
        {
            "nodetype": "category",
            "input": "workingpoint",
            "content": [
                {"key": key, "value": build_etabinning(sf[sf["workingPoint"] == key],syst,unc)}
                for key in keys
            ],
        }
    )


def build_etabinning(sf,syst,unc):
    edges = sorted(set(sf["etaMin"]) | set(sf["etaMax"]))
    return Binning.parse_obj(
        {
            "nodetype": "binning",
            "input": "eta",
            "edges": edges,
            "content": [
                build_ptbinning(sf[(sf["etaMin"] >= lo) & (sf["etaMax"] <= hi)],syst,unc)
                for lo, hi in zip(edges[:-1], edges[1:])
            ],
            "flow": "error",
        }
    )

def build_ptbinning(sf,syst,unc):
    edges = sorted(set(sf["ptMin"]) | set(sf["ptMax"]))
    return Binning.parse_obj(
        {
            "nodetype": "binning",
            "input": "pt",
            "edges": edges,
            "content": [
                build_sf(sf[(sf["ptMin"] >= lo) & (sf["ptMax"] <= hi)],syst,unc)
                for lo, hi in zip(edges[:-1], edges[1:])
            ],
            "flow": "clamp",
        }
    )


def build_sf(sf,syst,unc):
    if len(sf) != 1:
        raise ValueError(sf)

    value= -99
    if "nom" in syst:
        value = sf.iloc[0]["scaleFactor"]
    elif "up" in syst:
        if unc:
            value = sf.iloc[0]["scaleFactor"] * (1+sf.iloc[0]["scaleFactorSystUncty_up"])
        else:
            value = sf.iloc[0]["scaleFactorSystUncty_up"]
    elif "down" in syst:
        if unc:
            value = sf.iloc[0]["scaleFactor"] * (1-sf.iloc[0]["scaleFactorSystUncty_down"])
        else:
            value = sf.iloc[0]["scaleFactorSystUncty_down"]
    else:
        raise ValueError("No valid syst: nom, up, down")  
    

    return value

