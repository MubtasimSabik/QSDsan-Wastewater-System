# 2
# components.py

"""
1. Defines the 26 ADM1 state variable components (soluble substrates, particulate biomass,
   ions, and dissolved gases) using QSDsan's pre-compiled component set

2. Instantiates the ADM1 biological process model, which describes the 22 reactions
   that convert complex organic matter into biogas
"""

import warnings
from qsdsan import processes as pc

# Suppress Pandas FutureWarnings that originate inside QSDsan internals
warnings.simplefilter(action='ignore', category=FutureWarning)


# ============================================================================
# 1. ADM1 components (state variables)
# ============================================================================

"""
ADM1 tracks 26 state variables + water across the liquid and gas phases:

Soluble (S_) — dissolved in the liquid:
  S_su, S_aa, S_fa               — monosaccharides, amino acids, fatty acids (primary substrates)
  S_va, S_bu, S_pro, S_ac        — volatile fatty acids (VFAs): valerate, butyrate, propionate, acetate
  S_h2, S_ch4                    — dissolved hydrogen and methane (gas-liquid transfer)
  S_IC, S_IN                     — inorganic carbon (CO2/bicarbonate) and inorganic nitrogen (NH4+)
  S_I                            — soluble inerts (non-biodegradable dissolved organics)

Particulate (X_) — suspended solids:
  X_c                            — composite particulate COD (raw sludge, disintegrates first)
  X_ch, X_pr, X_li               — carbohydrates, proteins, lipids (hydrolysis substrates)
  X_su, X_aa, X_fa, X_c4, X_pro — active microbial groups (fermenters, degraders)
  X_ac, X_h2                     — methanogens: acetoclastic and hydrogenotrophic
  X_I                            — particulate inerts (non-biodegradable solids)

Ions:
  S_cat, S_an                    — lumped cations and anions (used for charge balance / pH)

QSDsan provides a pre-compiled set so we don't need to define each component individually.
"""


def create_components():
    return pc.create_adm1_cmps()


# ============================================================================
# 2. ADM1 process model (22 reactions)
# ============================================================================

"""
ADM1 describes the full anaerobic degradation pathway in 4 stages:

1. Disintegration  — composite particulate matter (X_c) breaks into carbohydrates, proteins, lipids
2. Hydrolysis      — particulate organics → soluble substrates (extracellular enzymes)
3. Acidogenesis    — soluble substrates → VFAs + H2 + CO2 (fermentation by acidogens)
4. Acetogenesis    — longer VFAs (propionate, butyrate, valerate) → acetate + H2
5. Methanogenesis  — acetate → CH4 + CO2 (acetoclastic); H2 + CO2 → CH4 (hydrogenotrophic)

Plus acid-base equilibria and liquid-gas transfer reactions for H2, CH4, and CO2.

A single ADM1 instance is shared with the reactor so all kinetics and stoichiometry come from one place.
"""


def create_processes():
    return pc.ADM1()
