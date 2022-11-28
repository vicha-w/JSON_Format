import correctionlib
import correctionlib.schemav2 as cs

### XY Correction for Type 1 PFMET for MC/simulation ###

metphicorrs = {}
metphicorrs["2016pre"] = {}
metphicorrs["2016post"] = {}
metphicorrs["2017"] = {}
metphicorrs["2018"] = {}

## x component parameters ##

# 2016
metphicorrs["2016pre"]["x"] = cs.FormulaRef(nodetype="formularef", index=0, parameters=[-0.188743, 0.136539])
metphicorrs["2016post"]["x"] = cs.FormulaRef(nodetype="formularef", index=0, parameters=[-0.153497, -0.231751])

# 2017
metphicorrs["2017"]["x"] = cs.FormulaRef(nodetype="formularef", index=0, parameters=[-0.300155, 1.90608])

# 2018
metphicorrs["2018"]["x"] = cs.FormulaRef(nodetype="formularef", index=0, parameters=[0.183518, 0.546754])

## y component parameters ##

# 2016
metphicorrs["2016pre"]["y"] = cs.FormulaRef(nodetype="formularef", index=0, parameters=[0.0127927, 0.117747])
metphicorrs["2016post"]["y"] = cs.FormulaRef(nodetype="formularef", index=0, parameters=[0.00731978, 0.243323])

# 2017
metphicorrs["2017"]["y"] = cs.FormulaRef(nodetype="formularef", index=0, parameters=[0.300213, -2.02232])

# 2018
metphicorrs["2018"]["y"] = cs.FormulaRef(nodetype="formularef", index=0, parameters=[0.192263, -0.42121])

for era in metphicorrs.keys():
    metphicorrs[era]["xy"] = [
        cs.FormulaRef(
            nodetype="formularef",
            index=0,
            parameters=(metphicorrs[era]["x"].parameters + metphicorrs[era]["y"].parameters),
        )
    ]
