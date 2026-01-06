from qsdsan import SanUnit


class CODAnaerobicDigester(SanUnit):
    
    """
    Inputs:
      [0] influent (blackwater)

    Outputs:
      [0] digestate (liquid/slurry)
      [1] biogas (CH4 + CO2, gas phase)

    Notes:
    - COD removal is applied to biodegradable COD bins (S_F, X_B_Subst)
    - Removed COD is converted to CH4 using:
          1 g CH4 ≈ 4 g COD
    - CO2 is added to reach a target methane fraction
    - NH4, PO4, salts remain in digestate
    """

    _N_ins = 1
    _N_outs = 2

    # Unit interface: 1 inlet (influent) and 2 outlets (digestate, biogas).

    """The Anaerobic Digester unit is defined with one inlet and two outlets. 
    Removal and capture fractions (COD removal, digestion) are provided as 
    user-defined parameters and stored as unit attributes for use during simulation.
    Consider the parameters in the __init__ method below as the "settings" for this unit operation.
    """

    # Initialize SanUnit and store performance parameters for use in _run().

    def __init__(
        self,
        ID="",
        ins=None,
        outs=(),
        COD_removal=0.60,       # fraction of biodegradable COD removed
        methane_fraction=0.65,  # volumetric / molar CH4 fraction
        **kwargs
    ):
        super().__init__(ID, ins, outs, **kwargs)
        self.COD_removal = COD_removal
        self.methane_fraction = methane_fraction

    # Simulation step: read influent and write to digestate + biogas outlets.

    def _run(self):
        inf = self.ins[0]
        digestate, biogas = self.outs

        # Initialize outputs
        digestate.copy_like(inf)
        biogas.empty()
        biogas.phase = "g"      # Start digestate as a copy of influent; reset biogas and enforce gas phase for CH4/CO2.

        # Biodegradable COD bins
        ids = [cid for cid in ("S_F", "X_B_Subst")  # Identify biodegradable COD components present in the thermo (here: S_F and X_B_Subst).
               if cid in digestate.components.IDs]

        bio_total = sum(digestate.imass[cid] for cid in ids)    # Total biodegradable COD mass flow (g/h) available for removal.

        if bio_total <= 0:                      # If no biodegradable COD is available, pass through with no biogas generation.
            return

        # COD removed (g COD / h)
        removed_COD = self.COD_removal * bio_total      # Apply fixed-fraction COD removal to the biodegradable COD pool.
        if removed_COD <= 0:
            return

        # Remove COD proportionally from liquid phase
        for cid in ids:
            frac = digestate.imass[cid] / bio_total
            digestate.imass[cid] -= removed_COD * frac

        # Convert removed COD to methane
        # 1 g CH4 ≈ 4 g COD
        CH4_g_h = removed_COD / 4.0
        biogas.imass["CH4"] = CH4_g_h

       
        # Add CO2 so that biogas achieves the target molar (≈ volumetric) CH4 fraction; assume biogas = CH4 + CO2 only.
        y_CH4 = self.methane_fraction
        n_CH4 = biogas.imol["CH4"]
        n_CO2 = n_CH4 * (1 - y_CH4) / y_CH4
        biogas.imol["CO2"] = n_CO2

        # Save key KPIs on the unit for reporting (removed COD and produced CH4).
        self.removed_COD_g_h = removed_COD
        self.CH4_g_h = CH4_g_h
 
    