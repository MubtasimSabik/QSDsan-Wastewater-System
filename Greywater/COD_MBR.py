import qsdsan as qs
from qsdsan import SanUnit


class CODBasedMBR(SanUnit):
    """
    COD-based MBR surrogate:
    - Removes a fraction of biodegradable COD from S_F & X_B_Subst (biological step).
    - Captures a fraction of particulate components into sludge (membrane/solids separation).
    Outputs:
    - filtrate (treated effluent)
    - sludge (captured solids + removed COD mass as biomass placeholder)
    """

    _N_ins = 1
    _N_outs = 2

    """The MBR unit is defined with one inlet and two outlets. 
    Removal and capture fractions (COD removal, solids capture, and optional nutrient removals) are provided as 
    user-defined parameters and stored as unit attributes for use during simulation.
    Consider the parameters in the __init__ method below as the "settings" for this unit operation.
    """

    def __init__(
        self,
        ID="",
        ins=None,
        outs=(),                   # fraction of (S_F + X_B_Subst) removed biologically
        COD_removal=0.85,          # fraction of biodegradable COD removed
        solids_capture=0.995,      # fraction of particulate components sent to sludge
        NH4_removal=0.0,           # optional fraction of S_NH4 removed
        PO4_removal=0.0,           # optional fraction of S_PO4 removed
        particulate_IDs=("X_B_Subst",),  # treat these as "solids" for capture
        **kwargs,                  # Allows QSDsan’s base class to accept extra settings (e.g., cost decorators, design args, etc.) without breaking our constructor.
    ):
        super().__init__(ID, ins, outs, **kwargs)
        self.COD_removal = COD_removal
        self.solids_capture = solids_capture
        self.NH4_removal = NH4_removal
        self.PO4_removal = PO4_removal
        self.particulate_IDs = tuple(particulate_IDs)

    def _run(self):
        inf = self.ins[0]
        eff, sludge = self.outs

        # Start: copy influent into effluent; sludge starts empty
        eff.copy_like(inf)
        sludge.empty()

        # --- 1) Biological COD removal from biodegradable COD bins ---
        # Remove from S_F and X_B_Subst proportionally

        """Biological COD removal is implemented by identifying biodegradable COD components (soluble and particulate), 
        summing their mass flow, and removing a user-defined fraction of that total."""

        biodegradable_ids = [cid for cid in ("S_F", "X_B_Subst") 
                             if cid in inf.components.IDs]                  # biodegradable_ids is a list of IDs for biodegradable COD components present in the influent stream
        bio_total = sum(eff.imass[cid] for cid in biodegradable_ids)        # bio_total is the total biodegradable COD mass flow (g/hr) in the effluent stream

        removed = self.COD_removal * bio_total if bio_total > 0 else 0.0    # If there is biodegradable COD: removed COD = COD_removal × bio_totat; If not, remove nothing

        """Here we distribute the total biologically removed COD across soluble and particulate COD in proportion to their shares, 
        subtract it from the effluent, and add the removed mass to sludge to keep the overall mass balance closed."""

        if bio_total > 0 and removed > 0:
            for cid in biodegradable_ids:
                frac = eff.imass[cid] / bio_total
                d = removed * frac
                eff.imass[cid] -= d
                # Put removed mass into sludge as "biomass/solids placeholder" by adding to X_B_Subst if present
                # (Keeps total mass conserved without requiring extra biomass components)
                if "X_B_Subst" in sludge.components.IDs:
                    sludge.imass["X_B_Subst"] += d
                else:
                    # fallback: just add it to sludge water-free mass by using the same cid
                    sludge.imass[cid] += d

    
        """Optional ammonium and phosphate removals are implemented as fractional transfers from effluent to sludge for mass-conserving bookkeeping, 
        without modeling detailed nutrient transformation pathways."""

        # --- 2) Optional nutrient removals  ---
        if "S_NH4" in eff.components.IDs and self.NH4_removal > 0:
            d = self.NH4_removal * eff.imass["S_NH4"]
            eff.imass["S_NH4"] -= d
            sludge.imass["S_NH4"] += d

        if "S_PO4" in eff.components.IDs and self.PO4_removal > 0:
            d = self.PO4_removal * eff.imass["S_PO4"]
            eff.imass["S_PO4"] -= d
            sludge.imass["S_PO4"] += d


        """Membrane solids capture is modeled by transferring a specified fraction of particulate components (defined by particulate_IDs) 
        from the effluent stream to the sludge stream."""
        
        # --- 3) Membrane solids capture: move particulate mass to sludge ---
        for cid in self.particulate_IDs:
            if cid in eff.components.IDs:
                captured = self.solids_capture * eff.imass[cid]
                eff.imass[cid] -= captured
                sludge.imass[cid] += captured
