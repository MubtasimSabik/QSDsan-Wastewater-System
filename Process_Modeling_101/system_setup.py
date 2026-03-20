# 3
# system_setup.py

"""
1. Creates aeration models for the aerobic reactors (diffused aeration with KLa and DO saturation)

2. Instantiates the ASM2d biological process model used by all reactors

3. Builds the 5 bioreactors in sequence:
- A1, A2: anoxic CSTRs (no aeration) for denitrification
- O1, O2, O3: aerobic CSTRs for nitrification and COD removal

4. Builds the secondary clarifier (C1) for solids separation and sludge recycling

5. Assembles all units into a System with recycle loops defined
"""

from qsdsan import sanunits as su, processes as pc, System

from streams_and_components import (
    influent, effluent, int_recycle, ext_recycle, wastage,
    V_an, V_ae, Q_ext, Q_was
)


# ============================================================================
# 1. Aeration models
# ============================================================================

"""
DiffusedAeration models oxygen transfer into the aerobic tanks.
KLa is the overall oxygen transfer coefficient [1/d] — higher KLa means faster oxygen transfer.
DOsat is the dissolved oxygen saturation concentration [mg/L] at the operating temperature.
Two separate aeration models are used because O3 has a lower KLa (less aeration) than O1 and O2.
"""

# Aeration model for aerobic reactors O1 and O2
aer1 = pc.DiffusedAeration('aer1', DO_ID='S_O2', KLa=240, DOsat=8.0, V=V_ae)

# Aeration model for aerobic reactor O3 (lower KLa — less oxygen supplied)
aer2 = pc.DiffusedAeration('aer2', DO_ID='S_O2', KLa=84, DOsat=8.0, V=V_ae)

"""
DO_ID accepts any component ID string. But practically, it should always be 'S_O2' for ASM2d because that's the only component that represents dissolved oxygen in that model.
"""

# ============================================================================
# 2. ASM2d biological process model
# ============================================================================

"""
ASM2d (Activated Sludge Model No. 2d) describes the biological reactions:
- COD removal by heterotrophic bacteria
- Nitrification by autotrophic bacteria
- Biological phosphorus removal by PAOs
- Denitrification under anoxic conditions

A single instance is shared across all reactors — they all use the same kinetics and stoichiometry.
"""

asm2d = pc.ASM2d()

# ============================================================================
# 3. Anoxic reactors — A1 and A2 (denitrification zone)
# ============================================================================

"""
CSTRs with aeration=None are anoxic (no dissolved oxygen).
Under anoxic conditions, heterotrophic bacteria use nitrate (NO3) as the electron acceptor instead of oxygen.
This is how nitrogen is removed from the wastewater (denitrification).

A1 receives three inflows: fresh influent, the internal recycle from O3 (nitrate-rich),
and the external recycle from the clarifier (biomass-rich).
"""

# Tank 1: anoxic — receives influent + both recycle streams
A1 = su.CSTR(
    'A1',
    # influent + internal recycle + external recycle (RAS)
    ins=[influent, int_recycle, ext_recycle],
    V_max=V_an,                                # tank volume [m3]
    aeration=None,                             # no aeration → anoxic conditions
    suspended_growth_model=asm2d,
)

# Tank 2: anoxic — continues denitrification with effluent from A1
A2 = su.CSTR(
    'A2',
    ins=A1-0,      # A1-0 means the first (index 0) outlet stream of A1
    V_max=V_an,
    aeration=None,
    suspended_growth_model=asm2d,
)

"""
no outs named here for A1 or A2. So, qsdsan will automatically create outlet streams A1 -> A2 on to the next ones A2 -> O1 and so on.
also tanks-in-series effect?

Parameter	            Value	                                Meaning
'A1', 'A2'	            string ID	                            registered name in QSDsan flowsheet
ins (A1)	            [influent, int_recycle, ext_recycle]	three inflows: fresh feed + both recycle streams
ins (A2)	            A1-0	                                directly connected to A1's outlet
V_max	                V_an = 1000 m³	                        tank volume
aeration	            None	                                no oxygen → anoxic conditions
suspended_growth_model	asm2d	                                biological process model

"""

# ============================================================================
# 4. Aerobic reactors — O1, O2, O3 (nitrification zone)
# ============================================================================

"""
CSTRs with an aeration model maintain dissolved oxygen for aerobic metabolism.
Under aerobic conditions:
- Heterotrophic bacteria oxidize remaining COD
- Autotrophic bacteria convert ammonium (NH4) to nitrate (NO3) — nitrification

O3 splits its outflow: 60% is recycled internally back to A1 (carrying nitrate for denitrification),
and 40% continues to the clarifier.
"""

# Tank 3: aerobic — nitrification begins
O1 = su.CSTR(
    'O1',
    ins=A2-0,
    V_max=V_ae,
    aeration=aer1,
    DO_ID='S_O2',              # state variable ID for dissolved oxygen
    suspended_growth_model=asm2d,
)

# Tank 4: aerobic — continued nitrification and COD removal
O2 = su.CSTR(
    'O2',
    ins=O1-0,
    V_max=V_ae,
    aeration=aer1,
    DO_ID='S_O2',
    suspended_growth_model=asm2d,
)

# Tank 5: aerobic — splits flow between internal recycle (to A1) and clarifier
O3 = su.CSTR(
    'O3',
    ins=O2-0,
    # two outlets: 60% recycle, 40% to clarifier
    outs=[int_recycle, 'treated'],
    split=[0.6, 0.4],               # split ratio by volumetric flow
    V_max=V_ae,
    aeration=aer2,                  # lower KLa than O1/O2
    DO_ID='S_O2',
    suspended_growth_model=asm2d,
)

"""
Parameter	            Value	                                Meaning
'O1', 'O2', 'O3'	    string ID	                            registered name in QSDsan flowsheet
ins	                    A2-0, O1-0, O2-0	                    chained outlets from previous reactor
V_max	                V_ae = 1333 m³	                        tank volume
aeration	            aer1 (O1, O2) / aer2 (O3)	            oxygen transfer model — KLa=240 for O1/O2, KLa=84 for O3
DO_ID	                'S_O2'	                                component ID for dissolved oxygen in ASM2d
suspended_growth_model	asm2d	                                biological process model
outs (O3 only)	        [int_recycle, 'treated']	            splits flow into recycle and clarifier feed
split (O3 only)	        [0.6, 0.4]	                            60% to internal recycle, 40% to clarifier
"""


# ============================================================================
# 5. Secondary clarifier — C1 (solids separation)
# ============================================================================

"""
The FlatBottomCircularClarifier separates the mixed liquor from O3 into:
- Clarified effluent (top) — treated water leaving the plant
- External recycle / return activated sludge, RAS (bottom) — biomass returned to A1
- Wastage / waste activated sludge, WAS (bottom) — excess sludge removed for SRT control

It is modeled as a 10-layer 1D settler (Takács model) — a common simplification
that captures the vertical concentration gradient without full 2D/3D CFD.
"""

C1 = su.FlatBottomCircularClarifier(
    'C1',
    # second outlet of O3 (the 40% going to clarifier)
    ins=O3-1,
    outs=[effluent, ext_recycle, wastage],  # treated effluent, RAS, WAS
    # return activated sludge flowrate [m3/d]
    underflow=Q_ext,
    wastage=Q_was,                         # waste sludge flowrate [m3/d]
    surface_area=1500,                     # clarifier surface area [m2]
    height=4,                              # clarifier depth [m]
    N_layer=10,                            # number of vertical layers in the 1D model
    # layer where influent enters (from top)
    feed_layer=5,
    # TSS threshold separating clear water and sludge zones [mg/L]
    X_threshold=3000,
    # maximum Vesilind settling velocity [m/d]
    v_max=474,
    # practical maximum settling velocity [m/d]
    v_max_practical=250,
    rh=5.76e-4,                            # hindered settling parameter [m3/g]
    # compressive settling parameter [m3/g]
    rp=2.86e-3,
    # fraction of non-settleable solids [-]
    fns=2.28e-3,
)

"""
The parameters:

Parameter	    Value	    Meaning
underflow=Q_ext	18446 m³/d	RAS flowrate
wastage=Q_was	385 m³/d	WAS flowrate
surface_area	1500 m²	    clarifier footprint
height	        4 m	        clarifier depth
N_layer	        10	        number of vertical layers in the 1D model
feed_layer	    5	        where the inlet enters (layer 5 from top)
X_threshold	    3000 mg/L	TSS boundary between clear water and sludge blanket
v_max	        474 m/d	    maximum theoretical settling velocity
v_max_practical	250 m/d	    capped practical settling velocity
rh, rp	        —	        hindered/compressive settling coefficients (Takács model)
fns	            2.28e-3	    fraction of non-settleable solids
"""


# ============================================================================
# 6. System assembly
# ============================================================================

"""
System connects all units in order and tells QSDsan which streams are recycles.
Recycle streams create feedback loops — QSDsan will iterate until convergence
during steady-state simulation, or integrate them dynamically during dynamic simulation.
"""

sys = System(
    'example_system',
    path=(A1, A2, O1, O2, O3, C1),       # unit operation sequence
    # recycle streams (internal + external)
    recycle=(int_recycle, ext_recycle),
)
