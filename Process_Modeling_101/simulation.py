# 5
# simulation.py

"""
1. Configures the dynamic tracker — tells QSDsan which streams and units to record over time

2. Sets solver tolerance for numerical accuracy

3. Runs the dynamic simulation (integrates all ASM2d ODEs over time)

4. Computes the estimated Sludge Retention Time (SRT) at steady state
"""

import numpy as np
from qsdsan.utils import get_SRT


# ============================================================================
# Simulation function
# ============================================================================

"""
ASM2d is a stiff ODE system — meaning it contains reactions that operate on
very different timescales simultaneously:
  - Fast: acid-base equilibria and oxygen transfer (minutes to hours)
  - Medium: COD removal and nitrification (hours to days)
  - Slow: biomass growth and decay (days to weeks)

Explicit solvers like RK45 are forced to take tiny timesteps to track the
fast reactions, making them extremely slow on stiff systems.
Implicit solvers like BDF and Radau can take large timesteps even when some
reactions are fast, making them far more efficient here.

t_step controls the output resolution only — it does NOT affect solver accuracy.
The solver internally uses adaptive timestepping regardless of t_step.

state_reset_hook='reset_cache' clears any previously cached states before starting,
ensuring a clean run from the initial conditions set in initialization.py.
Uncomment export_state_to to save the full simulation output to an Excel file.

Other available methods (pass as method= argument in main.py):
  'RK45'   — explicit Runge-Kutta, good for non-stiff systems (will be slow here)
  'Radau'  — implicit Runge-Kutta, also suitable for stiff systems
  'LSODA'  — switches automatically between stiff and non-stiff solvers

See: https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html
"""


def run_simulation(sys, influent, effluent, A1, A2, O1, O2, O3, C1, wastage,
                   t, t_step, method, biomass_IDs):

    # Track all streams and reactors so their concentration profiles are saved over time
    sys.set_dynamic_tracker(influent, effluent, A1, A2, O1, O2, O3, C1, wastage)

    # Set relative molar tolerance for the ODE solver — tighter tolerance = more accurate but slower
    sys.set_tolerance(rmol=1e-6)

    sys.simulate(
        state_reset_hook='reset_cache',
        # integrate from day 0 to day t
        t_span=(0, t),
        t_eval=np.arange(0, t + t_step, t_step),    # store results at each day
        method=method,
        # export_state_to=f'sol_{t}d_{method}.xlsx',  # uncomment to export results to Excel
    )

    """
    Parameter	        Value	                          Meaning
    state_reset_hook	'reset_cache'	                  Clears any leftover solver state before starting — ensures a clean run from the initial conditions
    t_span	          (0, t)	                        Integration window — solver runs from day 0 to day t
    t_eval	          np.arange(0, t+t_step, t_step)	Time points where results are saved — output resolution only, not solver accuracy
    method	          'BDF'	                          ODE algorithm passed through from main.py
    """

    # ============================================================================
    # SRT calculation
    # ============================================================================

    """
    SRT (Sludge Retention Time) is the average time that biomass spends in the system.
    It is a key design parameter — longer SRT supports nitrification and PAO activity
    but increases reactor volume and sludge production.
    get_SRT() estimates SRT based on biomass inventory and wastage rate at the final timestep.
    """

    srt = get_SRT(sys, biomass_IDs)
    print(f'Estimated SRT assuming at steady state is {round(srt, 2)} days')
