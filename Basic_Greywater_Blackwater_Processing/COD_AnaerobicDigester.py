from qsdsan import SanUnit


class CODAnaerobicDigester(SanUnit):
    """
    COD-based anaerobic digester surrogate.
    Outputs:
      [0] digestate (liquid/slurry)
      [1] biogas (mass proxy)

    """

    _N_ins = 1
    _N_outs = 2

    def __init__(
        self,
        ID="",
        ins=None,
        outs=(),
        # fraction of (S_F + X_B_Subst) converted to biogas
        COD_removal=0.60,
        **kwargs
    ):
        super().__init__(ID, ins, outs, **kwargs)
        self.COD_removal = COD_removal

    def _run(self):
        inf = self.ins[0]
        digestate, biogas = self.outs

        digestate.copy_like(inf)
        biogas.empty()

        # biodegradable COD bins
        ids = [cid for cid in ("S_F", "X_B_Subst")
               if cid in digestate.components.IDs]
        bio_total = sum(digestate.imass[cid] for cid in ids)

        removed = self.COD_removal * bio_total if bio_total > 0 else 0.0
        if removed <= 0 or bio_total <= 0:
            return

        # Remove proportionally from S_F and X_B_Subst
        for cid in ids:
            frac = digestate.imass[cid] / bio_total
            d = removed * frac
            digestate.imass[cid] -= d

        # Put removed mass into biogas as a proxy (use S_F if available, else first id)
        target = "S_F" if "S_F" in biogas.components.IDs else ids[0]
        biogas.imass[target] += removed
