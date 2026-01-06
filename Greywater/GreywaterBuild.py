import qsdsan as qs


def make_greywater(population):
    """
    We create a QSDsan WasteStream called 'Greywater' from per-capita loads (g/cap/d).
    This is after the qs.set_thermo(...) has already been called in the main script.
    Outputs are in g/hr (including H2O).
    """

    Qgw_L_cap_d = 65.0  # 65L of Greywater generation by each person

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
    """
    We convert per-capita-per-day inputs into population-scaled hourly flows, expressed as either m³/hr (for water) or g/hr (for pollutants).
    QSDsan systems are solved on a continuous time-rate basis, not as daily totals.
    Everything in the system must be expressed as a flow rate, not a batch amount.
    """
    Q_L_d = population * Qgw_L_cap_d
    Q_m3_h = (Q_L_d / 1000.0) / 24.0

    def gph(g_cap_d):
        return (population * g_cap_d) / 24.0  # g/hr

    COD_g_h = gph(CODgw_g_cap_d)
    N_g_h = gph(Ngw_g_cap_d)
    P_g_h = gph(Pgw_g_cap_d)
    K_g_h = gph(Kgw_g_cap_d)
    S_g_h = gph(Sgw_g_cap_d)

    Diclo_g_h = gph(Diclo_g_cap_d),
    Meto_g_h = gph(Meto_g_cap_d),
    Sulfa_g_h = gph(Sulfa_g_cap_d),
    Benzo_g_h = gph(Benzo_g_cap_d),
    Iome_g_h = gph(Iome_g_cap_d),

    # COD split - Controllable, here 70/30
    COD_X = 0.7 * COD_g_h # This represents the particulate biodegradable COD, later noted as X_B_Subst
    COD_S = 0.3 * COD_g_h # This represents the soluable biodegradable COD later noted as S_F

    # water mass in g/hr
    H2O_g_h = Q_m3_h * 1e6 # 1 m³ = 1000 × 1000 = 1,000,000 g = 1e6 g

    return qs.WasteStream(
        ID="Greywater",
        X_B_Subst=COD_X,
        S_F=COD_S,
        S_NH4=N_g_h,
        S_PO4=P_g_h,
        S_K=K_g_h,
        S_SO4=S_g_h,

        Diclo=Diclo_g_h,
        Meto=Meto_g_h,
        Sulfa=Sulfa_g_h,
        Benzo=Benzo_g_h,
        Iome=Iome_g_h,

        H2O=H2O_g_h,
        units="g/hr",
    )
