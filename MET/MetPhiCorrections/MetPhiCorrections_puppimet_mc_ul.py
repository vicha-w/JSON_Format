import correctionlib
import correctionlib.schemav2 as cs

### XY Correction for Type 1 PuppiMET for MC/simulation ###

metphicorrs = {}
metphicorrs["2016pre"] = {}
metphicorrs["2016post"] = {}
metphicorrs["2017"] = {}
metphicorrs["2018"] = {}

## x component parameters ##

# 2016
metphicorrs["2016pre"]["x"] = cs.FormulaRef(nodetype="formularef", index=0, parameters=[-0.0060447, -0.4183])
metphicorrs["2016post"]["x"] = cs.FormulaRef(nodetype="formularef", index=0, parameters=[-0.0058341, -0.395049])

# 2017
metphicorrs["2017"]["x"] = cs.FormulaRef(nodetype="formularef", index=0, parameters=[-0.0102265, -0.446416])

# 2018
metphicorrs["2018"]["x"] = cs.FormulaRef(nodetype="formularef", index=0, parameters=[-0.0214557, 0.969428])

## y component parameters ##

# 2016
metphicorrs["2016pre"]["y"] = cs.FormulaRef(nodetype="formularef", index=0, parameters=[0.008331, -0.0990046])
metphicorrs["2016post"]["y"] = cs.FormulaRef(nodetype="formularef", index=0, parameters=[0.00971595, -0.101288])

# 2017
metphicorrs["2017"]["y"] = cs.FormulaRef(nodetype="formularef", index=0, parameters=[0.0198663, 0.243182])

# 2018
metphicorrs["2018"]["y"] = cs.FormulaRef(nodetype="formularef", index=0, parameters=[0.0167134, 0.199296])

for era in metphicorrs.keys():
    metphicorrs[era]["xy"] = [
        cs.FormulaRef(
            nodetype="formularef",
            index=0,
            parameters=(metphicorrs[era]["x"].parameters + metphicorrs[era]["y"].parameters),
        )
    ]
