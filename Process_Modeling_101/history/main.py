import qsdsan as qs
import numpy as np
import pandas as pd
from qsdsan import sanunits as su, processes as pc, WasteStream, System
from qsdsan.utils import time_printer, load_data, get_SRT

import warnings
warnings.filterwarnings('ignore')

"""
We now create components of ASM2d. 
Compiled components for ASM2d are already available so we don't need to define each component one by one.
"""

cmps = pc.create_asm2d_cmps()

# cmps.show()
# cmps.S_A.show(chemical_info=True)

"""
We can uncomment this line to see all the components created for ASM2d. We use # in front of a line to comment it out.
cmps.show() will show a list of all components, while cmps.S_A.show(chemical_info=True) will show detailed chemical information for the component S_A (readily biodegradable substrate).
"""


# Parameters (flowrates, temperature)
Q_inf = 18446                               # influent flowrate [m3/d]
Q_was = 385                                 # sludge wastage flowrate [m3/d]
Q_ext = 18446                               # external recycle flowrate [m3/d]
# internal recycle flowrate will be defined later using split ratio.
# effluent flowrate will be calculated as the amount remaining after recycling and wastage.

Temp = 273.15+20                            # temperature [K]


# Create influent, effluent, recycle stream
# create an empty wastestream with specified temperature
influent = WasteStream('influent', T=Temp)
effluent = WasteStream('effluent', T=Temp)

int_recycle = WasteStream('internal_recycle', T=Temp)
ext_recycle = WasteStream('external_recycle', T=Temp)
# streams between the reactors will be
wastage = WasteStream('wastage', T=Temp)
# automatically assigned when we define SanUnit.

# Set the influent composition
default_inf_kwargs = {                                             # default influent composition
    'concentrations': {                                            # you can set concentration of each component separately.
        'S_I': 14,
        'X_I': 26.5,
        'S_F': 20.1,
        'S_A': 94.3,
        'X_S': 409.75,
        'S_NH4': 31,
        'S_N2': 0,
        'S_NO3': 0.266,
        'S_PO4': 2.8,
        'X_PP': 0.05,
        'X_PHA': 0.5,
        'X_H': 0.15,
        'X_AUT': 0,
        'X_PAO': 0,
        'S_ALK': 7*12,
    },
    # ('input total flowrate', 'input concentrations')
    'units': ('m3/d', 'mg/L'),
}

# set flowrate and composition of empty influent WasteStream
influent.set_flow_by_concentration(Q_inf, **default_inf_kwargs)

# you can also retreive other information, such as VSS, TSS, TDS, etc.
influent.get_VSS()

# Parameters (volumes)
V_an = 1000                                 # anoxic zone tank volume [m3/d]
V_ae = 1333                                 # aerated zone tank volume [m3/d]

# Aeration model
# aeration model for Tank 3 & Tank 4
aer1 = pc.DiffusedAeration('aer1', DO_ID='S_O2', KLa=240, DOsat=8.0, V=V_ae)
# aeration model for Tank 5
aer2 = pc.DiffusedAeration('aer2', DO_ID='S_O2', KLa=84, DOsat=8.0, V=V_ae)

aer1

# ASM2d
asm2d = pc.ASM2d()                       # create ASM2d processes
asm2d.show()                             # 21 processes in ASM2d

# ASM2d([aero_hydrolysis, anox_hydrolysis, anae_hydrolysis, hetero_growth_S_F, hetero_growth_S_A, denitri_S_F, denitri_S_A, ferment, hetero_lysis, PAO_storage_PHA,
#      aero_storage_PP, PAO_aero_growth_PHA, PAO_lysis, PP_lysis, PHA_lysis, auto_aero_growth, auto_lysis, precipitation, redissolution, anox_storage_PP, PAO_anox_growth])

# Each process includes stoichiometry, rate equation, and parameters.
asm2d.aero_hydrolysis

# Petersen stoichiometric matrix of ASM2d
# to display all columns
pd.set_option('display.max_columns', None)

asm2d.stoichiometry

# Rate equations of ASM2d
asm2d.rate_equations

# Anoxic reactors (Tank 1 & Tank 2)
A1 = su.CSTR('A1', ins=[influent, int_recycle, ext_recycle], V_max=V_an,      # As CSTR, 3 input streams, tank volume as V_an
             aeration=None, suspended_growth_model=asm2d)                     # No aeration, biokinetic model as asm2d

A2 = su.CSTR('A2', ins=A1-0, V_max=V_an,                 # ins=A1-0: set influent of A2 as effluent of A1 reactor (to connect A1 with A2)
             aeration=None, suspended_growth_model=asm2d)

A1                                        # Before simulation, outs are empty.

# Aerated reactors (Tank 3, Tank 4, Tank 5)
O1 = su.CSTR('O1', ins=A2-0, V_max=V_ae, aeration=aer1,                          # tank volume as V_ae with aeration model1
             DO_ID='S_O2', suspended_growth_model=asm2d)

O2 = su.CSTR('O2', ins=O1-0, V_max=V_ae, aeration=aer1,
             DO_ID='S_O2', suspended_growth_model=asm2d)

O3 = su.CSTR('O3', ins=O2-0, outs=[int_recycle, 'treated'], split=[0.6, 0.4],    # 60% of efflunet to internal recycle, 40% to clarifier
             V_max=V_ae, aeration=aer2,
             DO_ID='S_O2', suspended_growth_model=asm2d)

O3

# Clarifier
C1 = su.FlatBottomCircularClarifier('C1', ins=O3-1, outs=[effluent, ext_recycle, wastage],  # O3-1: second effluent of O3, three outs
                                    underflow=Q_ext, wastage=Q_was, surface_area=1500,
                                    # modeled as a 10 layer non-reactive unit
                                    height=4, N_layer=10, feed_layer=5,
                                    X_threshold=3000, v_max=474, v_max_practical=250,
                                    rh=5.76e-4, rp=2.86e-3, fns=2.28e-3)

# Create system
sys = System('example_system', path=(A1, A2, O1, O2, O3, C1), recycle=(
    int_recycle, ext_recycle))     # path: the order of reactor

# System diagram
sys.diagram()

# before running the simulation, 'outs' have nothing
sys

# Import initial condition excel file
df = load_data(
    'assets/tutorial_13/initial_conditions_asm2d.xlsx', sheet='default')

# Unlike other reactors, C1 has 3 rows for each of soluble, solids, and tss.
df

# Create a function to set initial conditions of the reactors


def batch_init(sys, df):
    # convert the DataFrame to a dictionary.
    dct = df.to_dict('index')
    # unit registry (A1, A2, O1, O2, O3, C1)
    u = sys.flowsheet.unit

    # for A1, A2, O1, O2, O3 reactor,
    for k in [u.A1, u.A2, u.O1, u.O2, u.O3]:
        # A1.set_init_conc(**dct[k_ID])
        k.set_init_conc(**dct[k._ID])

    # for clarifier, need to use different methods
    c1s = {k: v for k, v in dct['C1_s'].items() if v > 0}
    c1x = {k: v for k, v in dct['C1_x'].items() if v > 0}
    tss = [v for v in dct['C1_tss'].values() if v > 0]
    # set solubles
    u.C1.set_init_solubles(**c1s)
    # set sludge solids
    u.C1.set_init_sludge_solids(**c1x)
    u.C1.set_init_TSS(tss)                                            # set TSS


batch_init(sys, df)


# Simulation settings
# what you want to track changes in concentration
sys.set_dynamic_tracker(influent, effluent, A1, A2, O1, O2, O3, C1, wastage)
sys.set_tolerance(rmol=1e-6)

biomass_IDs = ('X_H', 'X_PAO', 'X_AUT')

# Simulation settings
t = 50                          # total time for simulation
t_step = 1                      # times at which to store the computed solution

method = 'BDF'                  # integration method to use
# method = 'RK45'
# method = 'RK23'
# method = 'DOP853'
# method = 'Radau'
# method = 'LSODA'

# https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html

# Run simulation, this could take several minuates
sys.simulate(state_reset_hook='reset_cache',
             t_span=(0, t),
             t_eval=np.arange(0, t+t_step, t_step),
             method=method,
             # export_state_to=f'sol_{t}d_{method}.xlsx',               # uncomment to export simulation result as excel file
             )

srt = get_SRT(sys, biomass_IDs)
print(f'Estimated SRT assuming at steady state is {round(srt, 2)} days')
# now you have 'outs' info.
sys

# Influent
influent.scope.plot_time_series(('S_I', 'X_I', 'S_F', 'S_A', 'X_S', 'S_NH4', 'S_N2', 'S_NO3', 'S_PO4', 'X_PP', 'X_PHA',
                                 'X_H', 'X_AUT', 'X_PAO', 'S_ALK'))      # you can plot how each state variable changes over time

# default_inf_kwargs = {
#    'concentrations': {
#      'S_I': 14,
#      'X_I': 26.5,
#      'S_F': 20.1,
#      'S_A': 94.3,
#      'X_S': 409.75,
#      'S_NH4': 31,
#      'S_N2': 0,
#      'S_NO3': 0.266,
#      'S_PO4': 2.8,
#      'X_PP': 0.05,
#      'X_PHA': 0.5,
#      'X_H': 0.15,
#      'X_AUT': 0,
#      'X_PAO': 0,
#      'S_ALK':7*12,
#      },
#    'units': ('m3/d', 'mg/L'),
#    }                                                               # constant influent setting

# Effluent
effluent.scope.plot_time_series((('S_I', 'X_I', 'S_F', 'S_A', 'X_S', 'S_NH4', 'S_N2', 'S_NO3', 'S_PO4', 'X_PP', 'X_PHA',
                                 'X_H', 'X_AUT', 'X_PAO', 'S_ALK')))                   # you can plot how each state variable changes over time

# you can plot how each state variable changes over time
effluent.scope.plot_time_series(('S_NH4', 'S_NO3'))

# you can plot how each state variable changes over time
effluent.scope.plot_time_series(('S_O2'))
