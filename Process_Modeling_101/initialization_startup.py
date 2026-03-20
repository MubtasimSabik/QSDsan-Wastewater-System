# initialization_startup.py

"""
Alternative to initialization.py for simulating plant startup from near-zero conditions.

Instead of loading pre-computed steady-state values from an Excel file, this script
seeds each reactor with a small amount of biomass and near-zero everything else.

To use: in main.py, replace 'import initialization' with 'import initialization_startup'
Also extend the simulation duration in simulation.py (t = 300 recommended).
"""

from system_setup import sys


# ============================================================================
# 1. Seed concentrations
# ============================================================================

"""
We can't start at true zero — zero biomass means no biological reactions ever start,
which is unrealistic. In practice, a new plant is seeded with sludge from another plant.

Here we provide a small inoculum of each biomass group to kick off the biology:
- X_H:   heterotrophs   — grow fastest, establish within weeks
- X_AUT: autotrophs     — grow slower, nitrification takes 1-2 months to establish
- X_PAO: PAOs           — slowest growing, biological P removal takes 2-3 months

All other components start at zero or near-zero.
Units: mg/L
"""

seed = {
    'X_H':   10.0,    # heterotrophic biomass seed [mg/L]
    'X_AUT':  1.0,    # autotrophic (nitrifying) biomass seed [mg/L]
    'X_PAO':  1.0,    # phosphorus accumulating organisms seed [mg/L]
}

"""
The clarifier TSS profile needs exactly 10 values — one per layer (top to bottom).
During startup the clarifier is essentially empty, so we use a small uniform value.
"""

# Small uniform TSS across all 10 clarifier layers [mg/L]
startup_tss = [10.0] * 10


# ============================================================================
# 2. Apply startup conditions
# ============================================================================

u = sys.flowsheet.unit

# Set the same seed concentrations in all 5 bioreactors
for reactor in [u.A1, u.A2, u.O1, u.O2, u.O3]:
    reactor.set_init_conc(**seed)

# Clarifier: set sludge solids and TSS profile
# Solubles are left at zero (default) — clarifier liquid starts clean
u.C1.set_init_sludge_solids(**seed)
u.C1.set_init_TSS(startup_tss)
