# 4
# system.py

"""
1. Defines benchmark initial concentrations for all ADM1 state variables
   (Rosen et al. 2006 steady-state values) to give the ODE solver a realistic starting point

2. Builds the AnaerobicCSTR unit, sets its liquid and gas volumes from Q and HRT,
   and applies the initial conditions

3. Assembles the reactor into a QSDsan System and configures the dynamic tracker
   so effluent and biogas concentrations are recorded over time
"""

from qsdsan import sanunits as su, System
from streams import C_mw, N_mw

# print([x for x in dir(su) if not x.startswith('_')])

"""
['A1junction', 'ADM1ptomASM2d', 'ADM1toASM2d', 'ADMjunction', 'ADMtoASM', 'ASM2dtoADM1', 'ASM2dtomADM1', 'ASMtoADM', 'ActivatedSludgeProcess', 'AdiabaticMultiStageVLEColumn', 
'AerobicDigester', 'AnMBR', 'AnaerobicBaffledReactor', 'AnaerobicCSTR', 'AnaerobicDigestion', 'BatchExperiment', 'BeltThickener', 'BinaryDistillation', 'BiogasCombustion', 
'BiogenicRefineryCarbonizerBase', 'BiogenicRefineryControls', 'BiogenicRefineryGrinder', 'BiogenicRefineryHHX', 'BiogenicRefineryHHXdryer', 'BiogenicRefineryHousing', 
'BiogenicRefineryIonExchange', 'BiogenicRefineryOHX', 'BiogenicRefineryPollutionControl', 'BiogenicRefineryScrewPress', 'BiogenicRefineryStruvitePrecipitation', 'CSTR', 
'CatalyticHydrothermalGasification', 'Centrifuge', 'CombinedHeatPower', 'CompletelyMixedMBR', 'ComponentSplitter', 'Copier', 'CropApplication', 'DryingBed', 'DynamicInfluent', 
'EcoSanAerobic', 'EcoSanAnaerobic', 'EcoSanAnoxic', 'EcoSanBioCost', 'EcoSanECR', 'EcoSanMBR', 'EcoSanPrimary', 'EcoSanSolar', 'EcoSanSystem', 'ElectrochemicalCell', 'Excretion', 
'ExcretionmASM2d', 'FakeSplitter', 'Flash', 'FlatBottomCircularClarifier', 'GasExtractionMembrane', 'HXprocess', 'HXutility', 'HeatExchangerNetwork', 'HydraulicDelay', 'Hydrocracking', .
'HydrothermalLiquefaction', 'Hydrotreating', 'IdealClarifier', 'Incinerator', 'InternalCirculationRx', 'IsothermalCompressor', 'Junction', 'Lagoon', 'LiquidTreatmentBed', 'LumpedCost', 
'MESHDistillation', 'MURT', 'MembraneDistillation', 'MembraneGasExtraction', 'MetalDosage', 'MixTank', 'Mixer', 'PFR', 'PhaseChanger]', 'PitLatrine','PolishingFilter', 
'PrimaryClarifier',('PrimaryClarifierBSM2", "ProcessWaterCenter", "Pump", "Reactor", "ReclaimerECR", "ReclaimerHousing", "ReclaimerIonExchange", "ReclaimerSolar", "ReclaimerSystem",
("SludgeCentrifuge", "SludgeDigester", "SludgePasteurization", "SludgePump", "SludgeSeparator", "SludgeThickening", "Splitter", "StorageTank", "Tank", "Thickener", "Toilet", 
"Trucking", "UDDT", "WWTpump", "dydt_cstr", "mADM1toASM2d", "mADMjunction", "mASM2dtoADM1p", "njit", "wwtpump"]
"""

# ============================================================================
# 1. Initial conditions (Rosen et al. 2006 ADM1 benchmark values)
# ============================================================================

"""
Starting the simulation from a near-zero state is numerically risky:
the stiff ODE solver must handle extreme concentration gradients as the
microbial community builds up from scratch — this can cause it to take
extremely small timesteps or fail to converge.

Using the Rosen et al. (2006) benchmark steady-state values as initial conditions
places the reactor close to a realistic operating point so the solver
converges smoothly.

Values are originally in kg/m3 (same units as the influent in streams.py),
multiplied by 1e3 to convert to g/m3 (= mg/L), which is what set_init_conc() expects.
S_IC and S_IN are again converted from molar to mass units using C_mw and N_mw.
"""

default_init_conds = {
    # Soluble intermediates
    'S_su':  0.0124 * 1e3,          # monosaccharides [g/m3]
    'S_aa':  0.0055 * 1e3,          # amino acids [g/m3]
    'S_fa':  0.1074 * 1e3,          # long-chain fatty acids [g/m3]
    'S_va':  0.0123 * 1e3,          # valerate [g/m3]
    'S_bu':  0.0140 * 1e3,          # butyrate [g/m3]
    'S_pro': 0.0176 * 1e3,          # propionate [g/m3]
    'S_ac':  0.0893 * 1e3,          # acetate [g/m3]
    # dissolved H2 [g/m3] — very low at steady state
    'S_h2':  2.5055e-7 * 1e3,
    'S_ch4': 0.0555 * 1e3,          # dissolved CH4 [g/m3]
    'S_IC':  0.0951 * C_mw * 1e3,   # inorganic carbon [g/m3]
    'S_IN':  0.0945 * N_mw * 1e3,   # inorganic nitrogen [g/m3]
    'S_I':   0.1309 * 1e3,          # soluble inerts [g/m3]

    # Particulate biomass (active microbial groups)
    'X_ch':  0.0205 * 1e3,          # carbohydrates [g/m3]
    'X_pr':  0.0842 * 1e3,          # proteins [g/m3]
    'X_li':  0.0436 * 1e3,          # lipids [g/m3]
    'X_su':  0.3122 * 1e3,          # sugar-degrading biomass [g/m3]
    'X_aa':  0.9317 * 1e3,          # amino-acid-degrading biomass [g/m3]
    'X_fa':  0.3384 * 1e3,          # LCFA-degrading biomass [g/m3]
    # valerate/butyrate-degrading biomass [g/m3]
    'X_c4':  0.3258 * 1e3,
    'X_pro': 0.1011 * 1e3,          # propionate-degrading biomass [g/m3]
    'X_ac':  0.6772 * 1e3,          # acetoclastic methanogens [g/m3]
    'X_h2':  0.2848 * 1e3,          # hydrogenotrophic methanogens [g/m3]
    'X_I':   17.2162 * 1e3,         # particulate inerts [g/m3]
}


# ============================================================================
# 2. Build the anaerobic CSTR and apply initial conditions
# ============================================================================

"""
AnaerobicCSTR is a single completely mixed reactor with no recycle stream —
sludge exits with the effluent (once-through).

Reactor volumes are calculated directly from the operating parameters:
  V_liq = Q × HRT         (e.g. 170 m3/d × 5 d = 850 m3)
  V_gas = V_liq × 0.1     (headspace is assumed to be 10% of the liquid volume)

The gas headspace is where CH4, CO2, and H2 accumulate before leaving via the
biogas outlet. Its volume affects the gas-liquid mass transfer rates.

Outlets are ordered (gas, eff) — biogas leaves first, liquid digestate second.
"""


def create_system(inf, eff, gas, adm1, Q, HRT, Temp):
    AD = su.AnaerobicCSTR(
        'AD',
        ins=inf,
        # first outlet = biogas, second = liquid effluent
        outs=(gas, eff),
        model=adm1,                   # ADM1 process kinetics and stoichiometry
        V_liq=Q * HRT,                # liquid volume [m3]
        # gas headspace volume [m3] (10% of liquid)
        V_gas=Q * HRT * 0.1,
        T=Temp,                       # operating temperature [K]
    )

    """
    Parameter	    Value	                Meaning
    'AD'	        string ID	            Registered name in QSDsan flowsheet
    ins	            inf	                    Single liquid inlet — the influent stream
    outs	        (gas, eff)	            Two outlets: index 0 = biogas, index 1 = liquid effluent
    model	        adm1	                ADM1 kinetics and stoichiometry attached to this reactor
    V_liq	        Q × HRT = 850 m³	    Liquid volume — set from operating conditions in main.py
    V_gas	        Q × HRT × 0.1 = 85 m³	Gas headspace — assumed 10% of liquid volume
    T	            308.15 K	            Operating temperature (35°C)
    """

    # Apply benchmark initial concentrations so the solver starts near steady state
    AD.set_init_conc(**default_init_conds)

    # ============================================================================
    # 3. Assemble into a System and configure dynamic tracking
    # ============================================================================

    """
    System wraps one or more SanUnits into a single flowsheet and manages
    the simulation loop. set_dynamic_tracker registers which streams to record
    over time — only tracked streams will have time-series data for plotting.
    """

    sys = System('Anaerobic_Digestion', path=(AD,))

    # Record effluent and biogas concentration profiles throughout the simulation
    sys.set_dynamic_tracker(eff, gas)

    return sys, AD
