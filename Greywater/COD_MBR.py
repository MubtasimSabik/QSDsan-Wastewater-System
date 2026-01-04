import qsdsan as qs
from qsdsan import SanUnit


class CODBasedMBR(SanUnit):
    """
    COD-based MBR surrogate:
    - Removes a fraction of biodegradable COD from S_F and X_B_Subst (biological step).
    - Captures a fraction of particulate components into sludge (membrane/solids separation).
    Outputs:
      [0] filtrate (treated effluent)
      [1] sludge (captured solids + removed COD mass placeholder)
    """

    _N_ins = 1
    _N_outs = 2

    def __init__(
        self,
        ID="",
        ins=None,
        outs=(),
        # fraction of (S_F + X_B_Subst) removed biologically
        COD_removal=0.85,
        solids_capture=0.995,      # fraction of particulate components sent to sludge
        NH4_removal=0.0,           # optional fraction of S_NH4 removed
        PO4_removal=0.0,           # optional fraction of S_PO4 removed
        particulate_IDs=("X_B_Subst",),  # treat these as "solids" for capture
        **kwargs,
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
        biodegradable_ids = [cid for cid in (
            "S_F", "X_B_Subst") if cid in inf.components.IDs]
        bio_total = sum(eff.imass[cid] for cid in biodegradable_ids)

        removed = self.COD_removal * bio_total if bio_total > 0 else 0.0

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

        # --- 2) Optional nutrient removals (simple bookkeeping) ---
        if "S_NH4" in eff.components.IDs and self.NH4_removal > 0:
            d = self.NH4_removal * eff.imass["S_NH4"]
            eff.imass["S_NH4"] -= d
            sludge.imass["S_NH4"] += d

        if "S_PO4" in eff.components.IDs and self.PO4_removal > 0:
            d = self.PO4_removal * eff.imass["S_PO4"]
            eff.imass["S_PO4"] -= d
            sludge.imass["S_PO4"] += d

        # --- 3) Membrane solids capture: move particulate mass to sludge ---
        for cid in self.particulate_IDs:
            if cid in eff.components.IDs:
                captured = self.solids_capture * eff.imass[cid]
                eff.imass[cid] -= captured
                sludge.imass[cid] += captured
