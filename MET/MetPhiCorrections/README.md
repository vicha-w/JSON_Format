
# MET Phi Corrections

This part of the repository is dedicated to MET Phi Corrections. These corrections currently exist for Run II UL and allow to improve the phi modulation observed in MET (mainly in PFMET) by recalculating the MET quantities using the corrections. The corrections are based on https://lathomas.web.cern.ch/lathomas/METStuff/XYCorrections/XYMETCorrection_withUL17andUL18andUL16.h . The phi-corrected pt and phi of MET are calculated using the phi-uncorrected values of those quantities, the number of primary vertices (npvs) and on era-dependent fixed parameters ([0], [1], [2], [3]).
The calculation essentially goes like this:
```
corrected_px = uncorrected_px+correction_x
corrected_py = uncorrected_py+correction_y

uncorrected_px = uncorrected_pt*cos(uncorrected_phi)
uncorrected_py = uncorrected_pt*sin(uncorrected_phi)

correction_x = -([0]*npvs+[1]) # corrections are parameterized as a linear function of npvs
correction_y = -([2]*npvs+[3]) # corrections are parameterized as a linear function of npvs

corrected_px =  uncorrected_pt*cos(uncorrected_phi)-([0]*npvs+[1]) # used to calculate corrected_pt and corrected_phi
corrected_py =  uncorrected_pt*sin(uncorrected_phi)-([2]*npvs+[3]) # used to calculate corrected_pt and corrected_phi

# the corrected_pt calculation is actually implemented as a larger TFormula string (see scripts/MetPhiCorrections_Utility.py) essentially doing the following
corrected_pt = sqrt(corrected_px^2+corrected_py^2)

# depending on corrected_px and corrected_py components, the corrected_phi calculation is different
# the phi calculation is actually implemented as a large TFormula string (see scripts/MetPhiCorrections_Utility.py) essentially doing the following
if (corrected_px==0 && corrected_py>0) corrected_phi = pi
else if (corrected_px==0 && corrected_py<0) corrected_phi = -pi
else if (corrected_px>0) corrected_phi = atan(corrected_py/corrected_px)
else if (corrected_px<0 && corrected_py>0) corrected_phi = atan(corrected_py/corrected_px) + pi
else if (corrected_px<0 && corrected_py<0) corrected_phi = atan(corrected_py/corrected_px) - pi
else corrected_phi = 0

# corrected_pt and corrected_phi are finally returned by the evaluate methods of the respective correction objects

```
The folder `corrections` contains the correction jsons in the xpog json format based on the correctionlib (https://cms-nanoaod.github.io/correctionlib/index.html). The corrections can also be found in the xpog json repository (https://gitlab.cern.ch/cms-nanoAOD/jsonpog-integration).

  

How to use the MET Phi Corrections is documented here: https://gitlab.cern.ch/cms-nanoAOD/jsonpog-integration/-/tree/master/POG/JME#met-phi-corrections

  

The folder `scripts` contains the scripts that were used to create the correctionlib jsons with the correctionlib python interface. There, the parameters ([0], [1], [2], [3]) needed to calculate the corrected MET quantities are stored/encoded in the `MetPhiCorrections_*.py` files for different eras, simulation and data, as well as PFMET and PuppiMET. The correction jsons are then created with the `CreateMETPhiCorrectionJSON_*.py` scripts, which import the aforementioned correction parameters from the corresponding files and uses the helper class defined in `MetPhiCorrections_Utility.py` to create the correctionlib objects. The helper class stores the formulas needed to calculate the corrected quantities and has methods that return the desired correctionlib.Correction objects based on the correction parameters and formulae. The correction jsons for e.g. PFMET in Run II UL simulation can then be created by running e.g.

```python CreateMETPhiCorrectionJSON_pfmet_mc.py```.

A further script `TestMetPhiCorrections.py` is provided that can be used to test the correction jsons on a technical level by calling
```
python TestMetPhiCorrections.py metphicorr_pfmet_mc metphicorr_pfmet_mc_2018_ul.json.gz
```
with the first argument being the name of the desired correction and the second argument being the path to the json file.
