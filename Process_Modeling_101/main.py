# 1
# main.py

"""
1. Sets plant operating conditions: flowrates, temperature, and reactor volumes

2. Calls create_components() to define the ASM2d state variables,
   and create_streams() to build influent, effluent, and recycle streams
   with influent concentrations set

3. Calls create_system() to build the 5 bioreactors and secondary clarifier,
   and assemble them into a QSDsan System with recycle loops

4. Calls load_initial_conditions() to apply near-steady-state starting values
   from an Excel file
   (or swap in apply_startup_conditions() from initialization_startup.py for a cold start)

5. Calls run_simulation() to integrate the ASM2d ODEs over time
   and compute the estimated Sludge Retention Time (SRT)

6. Calls plot_results() to visualise concentration time series for key state variables
"""

import warnings
warnings.filterwarnings('ignore')

from streams_and_components import create_components, create_streams
from system_setup import create_system
from initialization import load_initial_conditions
# from initialization_startup import apply_startup_conditions  # alternative: cold start
from simulation import run_simulation
from visualization import plot_results


# ============================================================================
# Plant operating conditions
# ============================================================================

"""
These parameters define the physical operating point of the activated sludge plant.
They are passed down through every module, so changing them here changes the
entire simulation.
"""

# Flowrates [m3/d]
Q_inf = 18446    # influent wastewater flowrate
Q_was = 385      # sludge wastage flowrate (for SRT control)
Q_ext = 18446    # external recycle flowrate (return activated sludge)

# We have set a 1:1 recycle ratio (Q_inf = Q_ext). Higher recycle brings more biomass back to the front of the system.

# Operating temperature [K] (20°C)
Temp = 273.15 + 20

# Reactor volumes [m3]
V_an = 1000    # anoxic reactor volume — applies to both A1 and A2
V_ae = 1333    # aerobic reactor volume — applies to O1, O2, and O3

"""
Anoxic reactor volume in m³. This applies to both A1 and A2 (they share the same size).
Aerobic reactor volume in m³. This applies to O1, O2, and O3.
"""

# Simulation settings
# t = 300      # time period for startup scenario
t = 50         # total simulation duration [days]
t_step = 1     # output timestep — solution is stored every 1 day [days]

method = 'BDF'  # ODE integration method (recommended for stiff ASM2d system)
# method = 'RK45'
# method = 'RK23'
# method = 'DOP853'
# method = 'Radau'
# method = 'LSODA'

# Biomass groups used to calculate SRT (Sludge Retention Time)
# heterotrophs, PAOs, autotrophs (nitrifiers)
biomass_IDs = ('X_H', 'X_PAO', 'X_AUT')


# ============================================================================
# Main execution
# ============================================================================

def main():
    # Step 1: register ASM2d components (state variables) with QSDsan
    create_components()

    # Step 2: create influent, effluent, recycle, and wastage streams; set influent composition
    influent, effluent, int_recycle, ext_recycle, wastage = create_streams(Q_inf, Q_was, Q_ext, Temp)

    # Step 3: build the 5 bioreactors and secondary clarifier, assemble into a System
    sys, A1, A2, O1, O2, O3, C1 = create_system(
        influent, effluent, int_recycle, ext_recycle, wastage,
        V_an, V_ae, Q_ext, Q_was
    )

    # Step 4: apply near-steady-state initial conditions from Excel file
    load_initial_conditions(sys)
    # apply_startup_conditions(sys)  # uncomment for cold-start simulation

    # Step 5: integrate ASM2d ODEs over time and compute SRT
    run_simulation(sys, influent, effluent, A1, A2, O1, O2, O3, C1, wastage,
                   t, t_step, method, biomass_IDs)

    # Step 6: plot concentration time series for influent and effluent state variables
    plot_results(influent, effluent)


if __name__ == '__main__':
    main()
