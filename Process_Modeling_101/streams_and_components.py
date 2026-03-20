# 2
# streams_and_components.py

"""
1. Defines the ASM2d component set (COD fractions, nitrogen species, phosphorus species,
   biomass types, alkalinity, etc.) using QSDsan's pre-compiled component set

2. Creates the main plant streams: influent, effluent, internal recycle,
   external recycle, and wastage

3. Sets the influent composition at the plant temperature
"""

from qsdsan import processes as pc, WasteStream


# ============================================================================
# 1. Component definition (ASM2d)
# ============================================================================

"""
Create components of ASM2d.
Compiled components for ASM2d are already available so we don't need to define each component one by one.

Other default components lists are - adm1_cmps, adm1_p_extension_cmps, adm1p_cmps, masm2d_cmps, pm2_cmps, pm2abaco2_cmps, pm2asm2d_cmps
"""

# Use the pre-compiled ASM2d component set provided by QSDsan.
# This includes all relevant COD, N, and P fractions, biomass groups, and alkalinity.

def create_components():
    return pc.create_asm2d_cmps()


# ============================================================================
# 2. Influent wastewater composition (ASM2d components)
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


# ============================================================================
# 3. Stream creation
# ============================================================================

"""
Five streams make up the system boundary:
- influent:     raw wastewater entering the plant
- effluent:     treated water leaving to discharge
- int_recycle:  internal recycle from aerobic zone back to anoxic zone
                (carries nitrate-rich mixed liquor for denitrification)
- ext_recycle:  external recycle — return activated sludge (RAS) from clarifier back to A1
                (carries biomass back to the front of the process)
- wastage:      waste activated sludge (WAS) removed for SRT control

Streams between reactors are created automatically by QSDsan when SanUnits are defined.
Only the influent composition is set here. The other stream concentrations
are computed by the ODE solver during simulation.
"""

def create_streams(Q_inf, Q_was, Q_ext, Temp):
    """Here we set up the streams using WasteStream function. The two parameters are
    the stream ID (user defined) and the temperature we just defined earlier."""

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

    return influent, effluent, int_recycle, ext_recycle, wastage
