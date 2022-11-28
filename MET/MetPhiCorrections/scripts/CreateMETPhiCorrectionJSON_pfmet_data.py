import correctionlib
import correctionlib.schemav2 as cs
import gzip
from MetPhiCorrections_Utility import MetPhiCorrectionsHelper as helper
from MetPhiCorrections_pfmet_data_ul import metphicorrs, edges

# loop over eras
for era in metphicorrs.keys():
    # label
    label = "metphicorr_pfmet_data"
    # pt component
    pt_metphicorr = helper.MetPhiCorrection_Data_pt(label, "Type 1 PFMET", metphicorrs[era]["xy"], edges[era])
    # phi component
    phi_metphicorr = helper.MetPhiCorrection_Data_phi(label, "Type 1 PFMET", metphicorrs[era]["xy"], edges[era])
    # write json
    cset = correctionlib.schemav2.CorrectionSet(
        schema_version=2,
        description="Type 1 PFMET Phi Corrections for data",
        corrections=[pt_metphicorr, phi_metphicorr],
    )
    # write as regular json
    # with open("{}_ul.json".format(label), "w") as fout:
    # fout.write(cset.json(exclude_unset=True, indent=4))
    # write as zipped json
    with gzip.open("{}_{}_ul.json.gz".format(label, era), "wt") as fout:
        fout.write(cset.json(exclude_unset=True, indent=4))
