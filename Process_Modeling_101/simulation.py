# 5
# simulation.py

"""
1. Configures the dynamic tracker — tells QSDsan which streams and units to record over time

2. Sets solver tolerance for numerical accuracy

3. Defines simulation duration, output timestep, and the ODE integration method

4. Runs the dynamic simulation (integrates all ASM2d ODEs over time)

5. Computes the estimated Sludge Retention Time (SRT) at steady state

6. Plots time series of all ASM2d state variables for influent and effluent
"""

import numpy as np
import matplotlib.pyplot as plt
from qsdsan.utils import get_SRT

from system_setup import sys, A1, A2, O1, O2, O3, C1
from streams_and_components import influent, effluent, wastage


# ============================================================================
# 1. Dynamic tracker and solver tolerance
# ============================================================================

"""
set_dynamic_tracker tells QSDsan which streams and units to record state variables for
throughout the simulation. Only tracked objects will have time-series data available for plotting.
"""

# Set figure resolution for all plots
plt.rcParams['figure.dpi'] = 100
plt.rcParams['savefig.dpi'] = 100

# Track all streams and reactors so their concentration profiles are saved over time
sys.set_dynamic_tracker(influent, effluent, A1, A2, O1, O2, O3, C1, wastage)

# Set relative molar tolerance for the ODE solver — tighter tolerance = more accurate but slower
sys.set_tolerance(rmol=1e-6)

# Biomass groups used to calculate SRT (Sludge Retention Time)
# heterotrophs, PAOs, autotrophs (nitrifiers)
biomass_IDs = ('X_H', 'X_PAO', 'X_AUT')


# ============================================================================
# 2. Simulation settings
# ============================================================================

"""
The simulation integrates a system of ODEs from t=0 to t=50 days.
t_step controls how often the solution is stored (every 1 day here) — it does NOT
affect solver accuracy, only the resolution of the output time series.

BDF (Backwards Differentiation Formula) is recommended for stiff ODE systems like ASM2d,
where reaction rates vary by several orders of magnitude.
Other available methods from scipy.integrate.solve_ivp:
- RK45, RK23, DOP853: explicit Runge-Kutta (better for non-stiff systems)
- Radau: implicit Runge-Kutta (also good for stiff systems)
- LSODA: switches automatically between stiff and non-stiff solvers
See: https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html
"""


# t = 300      # time period for stateup scenario
t = 50         # total simulation duration [days]
t_step = 1     # output timestep — solution is stored every 1 day [days]

method = 'BDF'  # ODE integration method (recommended for stiff ASM2d system)
# method = 'RK45'
# method = 'RK23'
# method = 'DOP853'
# method = 'Radau'
# method = 'LSODA'


# ============================================================================
# 3. Run the simulation
# ============================================================================

"""
state_reset_hook='reset_cache' clears any previously cached states before starting,
ensuring a clean run from the initial conditions set in initialization.py.
Uncomment export_state_to to save the full simulation output to an Excel file.
"""

sys.simulate(
    state_reset_hook='reset_cache',
    # integrate from day 0 to day 50
    t_span=(0, t),
    t_eval=np.arange(0, t + t_step, t_step),    # store results at each day
    method=method,
    # export_state_to=f'sol_{t}d_{method}.xlsx',  # uncomment to export results to Excel
)


# ============================================================================
# 4. SRT calculation
# ============================================================================

"""
SRT (Sludge Retention Time) is the average time that biomass spends in the system.
It is a key design parameter — longer SRT supports nitrification and PAO activity
but increases reactor volume and sludge production.
get_SRT() estimates SRT based on biomass inventory and wastage rate at the final timestep.
"""

srt = get_SRT(sys, biomass_IDs)
print(f'Estimated SRT assuming at steady state is {round(srt, 2)} days')


# ============================================================================
# 5. Plotting
# ============================================================================

# Influent: time series for all ASM2d state variables (should be flat — influent is constant)
fig, ax = influent.scope.plot_time_series((
    'S_I', 'X_I', 'S_F', 'S_A', 'X_S', 'S_NH4', 'S_N2', 'S_NO3',
    'S_PO4', 'X_PP', 'X_PHA', 'X_H', 'X_AUT', 'X_PAO', 'S_ALK'
))
ax.set_title('Influent — All ASM2d State Variables')

# Effluent: time series for all ASM2d state variables (shows how treatment evolves over time)
fig, ax = effluent.scope.plot_time_series((
    'S_I', 'X_I', 'S_F', 'S_A', 'X_S', 'S_NH4', 'S_N2', 'S_NO3',
    'S_PO4', 'X_PP', 'X_PHA', 'X_H', 'X_AUT', 'X_PAO', 'S_ALK'
))
ax.set_title('Effluent — All ASM2d State Variables')

# Effluent: focused plots for key nutrient removal indicators
fig, ax = effluent.scope.plot_time_series(('S_NH4', 'S_NO3'))
ax.set_title('Effluent — Nitrogen Removal (NH4, NO3)')

fig, ax = effluent.scope.plot_time_series(('S_O2',))
ax.set_title('Effluent — Dissolved Oxygen')


# Keep plot windows open when running as a script (non-blocking mode would close them immediately)
plt.show()
