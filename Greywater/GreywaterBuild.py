import qsdsan as qs


def make_greywater(population):
    """
    Creates a QSDsan WasteStream called 'greywater' from per-capita loads (g/cap/d).
    Assumes qs.set_thermo(...) has already been called in the main script.
    Outputs are in g/hr (including H2O).
    """

    Qgw_L_cap_d = 65.0  # 65L of Greywater
    CODgw_g_cap_d = 47.0
    Ngw_g_cap_d = 1.0
    Pgw_g_cap_d = 0.5
    Kgw_g_cap_d = 1.0
    Sgw_g_cap_d = 2.9

    Diclo_g_cap_d = 0.000068
    Meto_g_cap_d = 0.000068
    Sulfa_g_cap_d = 0.0000008228
    Benzo_g_cap_d = 0.001088
    Iome_g_cap_d = 0

    # ---- Conversions ----
    Q_L_d = population * Qgw_L_cap_d
    Q_m3_h = (Q_L_d / 1000.0) / 24.0

    def gph(g_cap_d):
        return (population * g_cap_d) / 24.0  # g/hr

    COD_g_h = gph(CODgw_g_cap_d)
    N_g_h = gph(Ngw_g_cap_d)
    P_g_h = gph(Pgw_g_cap_d)

    # COD split (70/30)
    COD_X = 0.7 * COD_g_h
    COD_S = 0.3 * COD_g_h

    # water mass in g/hr
    H2O_g_h = Q_m3_h * 1e6

    return qs.WasteStream(
        ID="Greywater",
        X_B_Subst=COD_X,
        S_F=COD_S,
        S_NH4=N_g_h,
        S_PO4=P_g_h,
        S_K=gph(Kgw_g_cap_d),
        S_SO4=gph(Sgw_g_cap_d),

        Diclo=gph(Diclo_g_cap_d),
        Meto=gph(Meto_g_cap_d),
        Sulfa=gph(Sulfa_g_cap_d),
        Benzo=gph(Benzo_g_cap_d),
        Iome=gph(Iome_g_cap_d),

        H2O=H2O_g_h,
        units="g/hr",
    )
