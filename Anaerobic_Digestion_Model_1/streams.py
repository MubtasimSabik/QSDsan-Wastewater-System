# 3
# streams.py

"""
1. Computes molecular weights for carbon and nitrogen — needed to convert
   molar concentrations (mol/L) to mass concentrations (kg/m3) for S_IC and S_IN

2. Defines the influent composition for a typical municipal sludge feed:
   soluble substrates, particulate organics, active biomass, and ions

3. Creates the three system streams: Influent, Effluent, and Biogas;
   sets the influent flowrate and component concentrations
"""

from qsdsan import WasteStream
from chemicals.elements import molecular_weight as get_mw


# ============================================================================
# 1. Molecular weights for unit conversion
# ============================================================================

"""
ADM1 expresses S_IC (inorganic carbon) and S_IN (inorganic nitrogen) in
molar units (kmol/m3) internally, but influent concentrations are typically
specified in kg/m3 (mass basis). Multiplying by molecular weight converts:
  mol/L × g/mol = g/L = kg/m3

C_mw = 12.011 g/mol  →  0.04 mol/L × 12.011 = 0.48 kg/m3 of inorganic carbon
N_mw = 14.007 g/mol  →  0.01 mol/L × 14.007 = 0.14 kg/m3 of inorganic nitrogen
"""

C_mw = get_mw({'C': 1})   # molecular weight of carbon [g/mol]
N_mw = get_mw({'N': 1})   # molecular weight of nitrogen [g/mol]


# ============================================================================
# 2. Influent composition (ADM1 state variables)
# ============================================================================

"""
This dictionary defines a typical municipal sludge feed composition.
S_ prefix = soluble (dissolved); X_ prefix = particulate (suspended solids).
All concentrations are in kg/m3 (equivalent to g/L).

The VFAs (S_va, S_bu, S_pro, S_ac) are set to very low values in the influent
because they are primarily produced inside the reactor by fermentation —
they are not typically present in raw sludge at high concentrations.

X_c (composite COD) is the main biodegradable feed — it disintegrates first
into carbohydrates (X_ch), proteins (X_pr), and lipids (X_li) before hydrolysis.
"""

default_inf_kwargs = {
    'concentrations': {
        # Soluble substrates
        'S_su': 0.01,           # monosaccharides / sugars [kg/m3]
        'S_aa': 1e-3,           # amino acids [kg/m3]
        'S_fa': 1e-3,           # long-chain fatty acids (LCFA) [kg/m3]

        # Volatile fatty acids (VFAs) — intermediates of fermentation
        'S_va': 1e-3,           # valerate [kg/m3]
        'S_bu': 1e-3,           # butyrate [kg/m3]
        'S_pro': 1e-3,          # propionate [kg/m3]
        'S_ac': 1e-3,           # acetate [kg/m3]

        # Dissolved gases
        'S_h2': 1e-8,           # dissolved hydrogen [kg/m3] — near zero in influent
        'S_ch4': 1e-5,          # dissolved methane [kg/m3] — near zero in influent

        # Inorganic species (converted from molar concentrations)
        'S_IC': 0.04 * C_mw,    # inorganic carbon — bicarbonate/CO2 [kg/m3]
        'S_IN': 0.01 * N_mw,    # inorganic nitrogen — ammonium [kg/m3]

        # Soluble inerts
        'S_I': 0.02,            # non-biodegradable dissolved organics [kg/m3]

        # Particulate organics (main biodegradable feed)
        'X_c': 2.0,             # composite particulate COD — raw sludge [kg/m3]
        'X_ch': 5.0,            # carbohydrates [kg/m3]
        'X_pr': 20.0,           # proteins [kg/m3]
        'X_li': 5.0,            # lipids [kg/m3]

        # Active microbial biomass in the feed (seed inoculum — typically small)
        'X_aa': 1e-2,           # amino-acid-degrading bacteria [kg/m3]
        'X_fa': 1e-2,           # LCFA-degrading bacteria [kg/m3]
        'X_c4': 1e-2,           # valerate/butyrate-degrading bacteria [kg/m3]
        'X_pro': 1e-2,          # propionate-degrading bacteria [kg/m3]
        'X_ac': 1e-2,           # acetoclastic methanogens [kg/m3]
        'X_h2': 1e-2,           # hydrogenotrophic methanogens [kg/m3]

        # Particulate inerts
        'X_I': 25,              # non-biodegradable suspended solids [kg/m3]

        # Ions (used for pH / charge balance)
        'S_cat': 0.04,          # lumped cations (e.g. Na+) [kg/m3]
        'S_an': 0.02,           # lumped anions (e.g. Cl-) [kg/m3]
    },
    'units': ('m3/d', 'kg/m3'),  # (flowrate unit, concentration unit)
}


# ============================================================================
# 3. Stream creation
# ============================================================================

"""
Three streams make up the system boundary:
- Influent: liquid feed entering the digester at reactor temperature
- Effluent: liquid digestate leaving the bottom of the reactor
- Biogas: gas-phase outlet (CH4, CO2, H2) — no temperature argument needed

Only the influent composition is set here. The effluent and biogas concentrations
are computed by the ODE solver during simulation.
"""

def create_streams(Q, Temp):
    inf = WasteStream('Influent', T=Temp)   # liquid feed stream at digester temperature
    eff = WasteStream('Effluent', T=Temp)   # liquid digestate outlet
    gas = WasteStream('Biogas')             # gas-phase outlet (CH4, CO2, H2)

    # Set influent mass flowrates from volumetric flow Q and concentrations above
    inf.set_flow_by_concentration(Q, **default_inf_kwargs)

    return inf, eff, gas
