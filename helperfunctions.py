import pandas as pd
import numpy as np
from collections import OrderedDict
from correctionlib.schemav1 import Correction, Binning, Category, Formula

#### Here the logic is to go backwards. First check the SF, then filter with the ptbinning, etc.. TAKEN from https://gist.github.com/alefisico/2e190a8380f54cfbcd7c6c7baa58ce56

def build_SF(sf):
    print(sf)
    if len(sf) != 1:
        raise ValueError(sf)
    

    value = sf.iloc[0]["scaleFactor"]
    return float(value)

def build_ptbinning(sf):
    edges = sorted(set(sf['ptMin']) | set(sf['ptMax']))
    print(edges)
    return Binning.parse_obj({
        "nodetype": "binning",
        "edges": edges,
        "content": [
            build_SF(sf[(sf['ptMin'] >= lo) & (sf['ptMax'] <= hi)])
            for lo, hi in zip(edges[:-1], edges[1:])
        ]
    })

def build_etabinning(sf):
    edges = sorted(set(sf['etaMin']) | set(sf['etaMax']))
    return Binning.parse_obj({
        "nodetype": "binning",
        "edges": edges,
        "content": [
            build_ptbinning(sf[(sf['etaMin'] >= lo) & (sf['etaMax'] <= hi)])
            for lo, hi in zip(edges[:-1], edges[1:])
        ]
    })

def build_wptype(sf):
    keys = sorted(sf['workingPoint'].unique())
    return Category.parse_obj({
        "nodetype": "category",
        "keys": keys,
        "content": [
            build_etabinning(sf[sf['workingPoint'] == key])
            for key in keys
        ]
    })

def build_valueType(sf):
    keys = list(sf['valueType'].unique())
    return Category.parse_obj({
        "nodetype": "category",
        "keys": keys,
        "content": [
            build_wptype(sf[sf['valueType'] == key])
            for key in keys
        ]
    })

def build_year(sf):
    keys = list(sf['year'].unique())
    return Category.parse_obj({
        "nodetype": "category",
        "keys": keys,
        "content": [
            build_valueType(sf[sf['year'] == key])
            for key in keys
        ]
    })
