import correctionlib.schemav2 as cs


class MetPhiCorrectionsHelper:
    """
    utility class to create MET Phi Correction jsons
    """

    # phi calculation string
    phi_calculation = (
        "(((x*cos(y)-([0]*z+[1]))==0)*((x*sin(y)-([2]*z+[3]))>0))*3.14159+"
        "(((x*cos(y)-([0]*z+[1]))==0)*((x*sin(y)-([2]*z+[3]))<0))*(-3.14159)+"
        "((x*cos(y)-([0]*z+[1]))>0)*atan((x*sin(y)-([2]*z+[3]))/(x*cos(y)-([0]*z+[1])))+"
        "(((x*cos(y)-([0]*z+[1]))<0)*((x*sin(y)-([2]*z+[3]))>0))*(atan((x*sin(y)-([2]*z+[3]))/(x*cos(y)-([0]*z+[1])))+3.14159)+"
        "(((x*cos(y)-([0]*z+[1]))<0)*((x*sin(y)-([2]*z+[3]))<0))*(atan((x*sin(y)-([2]*z+[3]))/(x*cos(y)-([0]*z+[1])))-3.14159)+"
        "0"
    )

    # pt calculation string
    pt_calculation = "sqrt((x*cos(y)-([0]*z+[1]))^2+(x*sin(y)-([2]*z+[3]))^2)"

    # maximum allowed pt of MET
    pt_max = 6500.0

    # maximum allowed phi of MET
    phi_max = 3.15

    # maximum allowed number of primary vertices
    npvs_max = 1000.0

    # in the following, four methods are given to return correction objects for phi-corrected MET quantities (pt, phi) in simulation or data
    # the corrections for simulation depend on the uncorrected quantities of MET (pt, phi) and the number of reconstructed primary vertices
    # however, to make the call to the correction objects similar between simulation and data, the run number is also an input variable for simulation, but it is never used
    # the corrections for data have the same input variables as in simulation, however the run number is explicitly used, since the corrections are different for different runs
    # the user of these methods is responsible to feed in sensible corrections as the third input argument of the following functions

    @classmethod
    def MetPhiCorrection_MC_pt(cls, base_label="base_label", nice_met_type_label="Type 1 PFMET", corrections=[]):
        """returns a correction object for the phi-corrected pt of MET in simulation"""
        pt_correction = cs.Correction(
            name="pt_{}".format(base_label),
            version=1,
            inputs=[
                cs.Variable(
                    name="met_pt", type="real", description="{} pt without XY corrections".format(nice_met_type_label)
                ),
                cs.Variable(
                    name="met_phi",
                    type="real",
                    description="{} phi [-pi,pi] without XY corrections".format(nice_met_type_label),
                ),
                cs.Variable(name="npvs", type="real", description="Number of reconstructed primary vertices"),
                cs.Variable(name="run", type="real", description="Run number"),
            ],
            output=cs.Variable(
                name="corrmet_pt",
                type="real",
                description="{} pt with XY corrections applied".format(nice_met_type_label),
            ),
            generic_formulas=[
                cs.Formula(
                    nodetype="formula",
                    variables=["met_pt", "met_phi", "npvs"],
                    parser="TFormula",
                    expression=cls.pt_calculation,
                )
            ],
            data=cs.Binning(
                nodetype="binning",
                input="met_pt",
                flow="error",
                edges=[0.0, cls.pt_max],
                content=[
                    cs.Binning(
                        nodetype="binning",
                        input="met_phi",
                        flow="error",
                        edges=[-cls.phi_max, cls.phi_max],
                        content=corrections,
                    )
                ],
            ),
        )
        return pt_correction

    @classmethod
    def MetPhiCorrection_MC_phi(cls, base_label="base_label", nice_met_type_label="Type 1 PFMET", corrections=[]):
        """returns a correction object for the phi-corrected phi of MET in simulation"""
        phi_correction = cs.Correction(
            name="phi_{}".format(base_label),
            version=1,
            inputs=[
                cs.Variable(
                    name="met_pt", type="real", description="{} pt without XY corrections".format(nice_met_type_label)
                ),
                cs.Variable(
                    name="met_phi",
                    type="real",
                    description="{} phi [-pi,pi] without XY corrections".format(nice_met_type_label),
                ),
                cs.Variable(name="npvs", type="real", description="Number of reconstructed primary vertices"),
                cs.Variable(name="run", type="real", description="Run number"),
            ],
            output=cs.Variable(
                name="corrmet_phi",
                type="real",
                description="{} phi [-pi,pi] with XY corrections applied".format(nice_met_type_label),
            ),
            generic_formulas=[
                cs.Formula(
                    nodetype="formula",
                    variables=["met_pt", "met_phi", "npvs"],
                    parser="TFormula",
                    expression=cls.phi_calculation,
                )
            ],
            data=cs.Binning(
                nodetype="binning",
                input="met_pt",
                flow="error",
                edges=[0.0, cls.pt_max],
                content=[
                    cs.Binning(
                        nodetype="binning",
                        input="met_phi",
                        flow="error",
                        edges=[-cls.phi_max, cls.phi_max],
                        content=corrections,
                    )
                ],
            ),
        )
        return phi_correction

    @classmethod
    def MetPhiCorrection_Data_pt(
        cls, base_label="base_label", nice_met_type_label="Type 1 PFMET", corrections=[], edges=[]
    ):
        """returns a correction object for the phi-corrected pt of MET in data"""
        pt_correction = cs.Correction(
            name="pt_{}".format(base_label),
            version=1,
            inputs=[
                cs.Variable(
                    name="met_pt", type="real", description="{} pt without XY corrections".format(nice_met_type_label)
                ),
                cs.Variable(
                    name="met_phi",
                    type="real",
                    description="{} phi [-pi,pi] without XY corrections".format(nice_met_type_label),
                ),
                cs.Variable(name="npvs", type="real", description="Number of reconstructed primary vertices"),
                cs.Variable(name="run", type="real", description="Run number"),
            ],
            output=cs.Variable(
                name="corrmet_pt",
                type="real",
                description="{} pt with XY corrections applied".format(nice_met_type_label),
            ),
            generic_formulas=[
                cs.Formula(
                    nodetype="formula",
                    variables=["met_pt", "met_phi", "npvs"],
                    parser="TFormula",
                    expression=cls.pt_calculation,
                ),
                cs.Formula(nodetype="formula", variables=["met_pt"], parser="TFormula", expression="x"),
            ],
            data=cs.Binning(
                nodetype="binning",
                input="met_pt",
                flow="error",
                edges=[0.0, cls.pt_max],
                content=[
                    cs.Binning(
                        nodetype="binning",
                        input="met_phi",
                        flow="error",
                        edges=[-cls.phi_max, cls.phi_max],
                        content=[
                            cs.Binning(nodetype="binning", input="run", edges=edges, flow="error", content=corrections)
                        ],
                    )
                ],
            ),
        )
        return pt_correction

    @classmethod
    def MetPhiCorrection_Data_phi(
        cls, base_label="base_label", nice_met_type_label="Type 1 PFMET", corrections=[], edges=[]
    ):
        """returns a correction object for the phi-corrected phi of MET in data"""
        phi_correction = cs.Correction(
            name="phi_{}".format(base_label),
            version=1,
            inputs=[
                cs.Variable(
                    name="met_pt", type="real", description="{} pt without XY corrections".format(nice_met_type_label)
                ),
                cs.Variable(
                    name="met_phi",
                    type="real",
                    description="{} phi [-pi,pi] without XY corrections".format(nice_met_type_label),
                ),
                cs.Variable(name="npvs", type="real", description="Number of reconstructed primary vertices"),
                cs.Variable(name="run", type="real", description="Run number"),
            ],
            output=cs.Variable(
                name="corrmet_phi",
                type="real",
                description="{} phi [-pi,pi] with XY corrections applied".format(nice_met_type_label),
            ),
            generic_formulas=[
                cs.Formula(
                    nodetype="formula",
                    variables=["met_pt", "met_phi", "npvs"],
                    parser="TFormula",
                    expression=cls.phi_calculation,
                ),
                cs.Formula(nodetype="formula", variables=["met_phi"], parser="TFormula", expression="x"),
            ],
            data=cs.Binning(
                nodetype="binning",
                input="met_pt",
                flow="error",
                edges=[0.0, cls.pt_max],
                content=[
                    cs.Binning(
                        nodetype="binning",
                        input="met_phi",
                        flow="error",
                        edges=[-cls.phi_max, cls.phi_max],
                        content=[
                            cs.Binning(nodetype="binning", input="run", edges=edges, flow="error", content=corrections)
                        ],
                    )
                ],
            ),
        )
        return phi_correction
