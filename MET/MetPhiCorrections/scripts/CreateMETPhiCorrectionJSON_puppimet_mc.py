import correctionlib
import correctionlib.schemav2 as cs
import gzip
from MetPhiCorrections_Utility import MetPhiCorrectionsHelper as helper
from MetPhiCorrections_puppimet_mc_ul import metphicorrs

# loop over eras
for era in metphicorrs.keys():
    # label
    label = "metphicorr_puppimet_mc"
    # pt component
    pt_metphicorr = helper.MetPhiCorrection_MC_pt(label, "Type 1 PuppiMET", metphicorrs[era]["xy"])
    # phi component
    phi_metphicorr = helper.MetPhiCorrection_MC_phi(label, "Type 1 PuppiMET", metphicorrs[era]["xy"])
    # write json
    cset = correctionlib.schemav2.CorrectionSet(
        schema_version=2,
        description="Type 1 PuppiMET Phi Corrections for MC/simulation",
        corrections=[pt_metphicorr, phi_metphicorr],
    )
    # write as regular json
    # with open("{}_ul.json".format(label), "w") as fout:
    # fout.write(cset.json(exclude_unset=True, indent=4))
    # write as zipped json
    with gzip.open("{}_{}_ul.json.gz".format(label, era), "wt") as fout:
        fout.write(cset.json(exclude_unset=True, indent=4))
