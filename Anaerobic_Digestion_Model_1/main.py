# 1
# main.py

"""
1. Sets reactor operating conditions: flowrate, temperature, and hydraulic retention time

2. Calls create_components() and create_processes() to define the 26 ADM1 state variables
   and the 22 biological/chemical processes

3. Calls create_streams() to build influent, effluent, and biogas streams with
   influent concentrations set

4. Calls create_system() to build the anaerobic CSTR, set initial conditions,
   and assemble into a QSDsan System

5. Calls run_simulation() to integrate the ADM1 ODEs over time

6. Calls plot_results() to visualise concentration time series for key state variables
"""

from components import create_components, create_processes
from streams import create_streams
from system import create_system
from simulation import run_simulation
from visualization import plot_results


# ============================================================================
# Reactor operating conditions
# ============================================================================

"""
These three parameters define the physical operating point of the digester.
They are passed down through every module, so changing them here changes the
entire simulation.

HRT (Hydraulic Retention Time) controls how long the sludge stays in the reactor:
- Short HRT (< 5 d): faster throughput, but risk of washout (biomass leaves before growing)
- Typical mesophilic HRT: 15–30 d for municipal sludge; 5 d is used here as a tutorial case
"""

# influent flowrate [m3/d]
Q = 170

# operating temperature [K] — 35°C is the mesophilic optimum for methanogens
Temp = 273.15 + 35

# hydraulic retention time [d] — reactor volume = Q × HRT
HRT = 5

# to be used in Step 4

t = 10            # t : total simulation duration [days]
# t_step : interval at which to store results [days] — does not affect solver accuracy
t_step = 0.1
# method : ODE integration algorithm (BDF recommended for ADM1)
method = 'BDF'


# ============================================================================
# Main execution
# ============================================================================

def main():
    # Step 1: define ADM1 components (26 state variables) and process model (22 reactions)
    cmps = create_components()
    adm1 = create_processes()

    # Step 2: create influent, effluent, and biogas streams; set influent composition
    inf, eff, gas = create_streams(Q, Temp)

    # Step 3: build the anaerobic CSTR, apply initial conditions, wrap in a System
    # we only use sys later, so AD can be removed. However, it is useful if we wanted to extend from here.
    sys, AD = create_system(inf, eff, gas, adm1, Q, HRT, Temp)

    # Step 4: integrate ADM1 ODEs over time using the BDF solver
    run_simulation(sys, t=t, t_step=t_step, method=method)

    # Step 5: plot concentration time series for effluent and biogas state variables
    plot_results(eff, gas, cmps)


if __name__ == '__main__':
    main()
