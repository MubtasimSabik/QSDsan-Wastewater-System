# 2
# streams_and_components.py

"""
1. This script selects the biological/chemical state components we will track in ASM2d model (COD fractions, nitrogen species, phosphorus species, biomass types, alkalinity, etc.)

2. Defines key flow parameters for the plant: influent flow, sludge wastage flow, external recycle, and later the internal recycle and effluent

3. Creates the main plant streams
- influent - effluent - internal recycle - external recycle - wastage

4. Sets the influent composition at the plant temperature
"""

import qsdsan as qs
from qsdsan import processes as pc, WasteStream

# ============================================================================
# 1. Component definition (ASM2d)
# ============================================================================

# Use the pre-compiled ASM2d component set provided by QSDsan.
# This includes all relevant COD, N, and P fractions, biomass groups, and alkalinity.

"""
Create components of ASM2d.
Compiled components for ASM2d are already available so we don't need to define each component one by one.

Other default components lists are - adm1_cmps, adm1_p_extension_cmps, adm1p_cmps, masm2d_cmps, pm2_cmps, pm2abaco2_cmps, pm2asm2d_cmps
"""

cmps = pc.create_asm2d_cmps()


"""These are the hydraulic parameters and flowrates that we will use to set up the system in the next module. 
We can change these values to see how they affect the system behavior. The flowrates and volumes here are based on the tutorial page."""


# ============================================================================
# 2. Hydraulic parameters (flow rates and temperature)
# ============================================================================

# Influent wastewater flowrate [m3/d]
Q_inf = 18446

# Sludge wastage flowrate from the biological system [m3/d]
Q_was = 385

# External recycle flowrate (e.g., return activated sludge) [m3/d]
Q_ext = 18446

"""We have set a 1:1 recycle ratio (Q_inf = Q_ext). Higher recycle brings more biomass back to the front of the system."""

# Internal recycle flowrate will be defined later using a split ratio
# (e.g., from aerobic to anoxic zone).
# Effluent flowrate will be the remaining flow after recycle and wastage.

# Operating temperature [K] (20°C)
Temp = 273.15 + 20


# ============================================================================
# 3. Main plant streams
# ============================================================================

"""Here we set up the streams using WasteStream function. The two paramets are the stream ID (user defined) and the temperature we just defined earlier."""

# Influent wastewater entering the plant
influent = WasteStream('influent', T=Temp)

# Final effluent leaving the biological system (to discharge)
effluent = WasteStream('effluent', T=Temp)

# Internal recycle (e.g., from aerobic to anoxic zone)
int_recycle = WasteStream('internal_recycle', T=Temp)

# External recycle (e.g., return activated sludge from clarifier)
ext_recycle = WasteStream('external_recycle', T=Temp)

# Sludge wastage stream (for SRT control)
# Streams between reactors will be created automatically when SanUnits are defined.
wastage = WasteStream('wastage', T=Temp)


# ============================================================================
# 4. Influent wastewater composition (ASM2d components)
# ============================================================================

# Default influent composition in terms of ASM2d state variables.
# Concentrations are in mg/L; flowrate unit is m3/d.
default_inf_kwargs = {
    'concentrations': {
        # COD fractions
        'S_I': 14,       # soluble inert COD
        'X_I': 26.5,     # particulate inert COD
        'S_F': 20.1,     # readily biodegradable substrate
        'S_A': 94.3,     # fermentation products (e.g., acetate)
        'X_S': 409.75,   # slowly biodegradable substrate

        # Nitrogen species
        'S_NH4': 31,     # ammonium/ammonia nitrogen
        'S_N2': 0,       # dissolved nitrogen gas
        'S_NO3': 0.266,  # nitrate/nitrite nitrogen

        # Phosphorus species
        'S_PO4': 2.8,    # soluble orthophosphate
        'X_PP': 0.05,    # polyphosphate (stored P)
        'X_PHA': 0.5,    # stored PHA

        # Biomass groups
        'X_H': 0.15,     # heterotrophic biomass
        'X_AUT': 0,      # autotrophic nitrifying biomass
        'X_PAO': 0,      # PAO biomass

        # Alkalinity
        'S_ALK': 7 * 12,  # alkalinity (e.g., 7 meq/L × 12 mg/meq)
    },
    # ('total flowrate unit', 'concentration unit')
    'units': ('m3/d', 'mg/L'),
}

# Set influent flowrate and component concentrations.
influent.set_flow_by_concentration(Q_inf, **default_inf_kwargs)

""" 
default_inf_kwargs is a user defined variable, can be named anything. _kwargs is a python lingo for dictionary of keyword arguments. 
the ** here unpacks the dictionary default_inf_kwargs into named variable. Writing the above line is like writing
influent.set_flow_by_concentration(
    Q_inf, 
    'concentrations': {
        # COD fractions
        'S_I': 14, 
        ........
)  
"""

# Example of derived properties that can be queried (e.g., for QA/QC):
# VSS, TSS, TDS, etc. Here we call get_VSS() as a demonstration.
# (Optional: the returned value can be printed or logged if needed.)
influent.get_VSS()

""" 
get_VSS() is a method that calculates the volatile suspended solids (VSS) concentration based on the ASM2d component concentrations. 
it can be wrapped with print() to display the value or stored for later use.
"""

# Anoxic reactor volume [m3]
V_an = 1000

"""
Anoxic reactor volume in m³. This applies to both A1 and A2 (they share the same size).

"""

# Aerated (aerobic) reactor volume [m3]
V_ae = 1333

"""
Aerobic reactor volume in m³. This applies to O1, O2, and O3.

"""
