# 5
# simulation.py

"""
1. Defines run_simulation() — configures the ODE integration settings
   and runs the dynamic simulation for the anaerobic digestion system

2. Uses the BDF (Backwards Differentiation Formula) solver by default,
   recommended for stiff systems like ADM1 where reaction timescales
   vary by several orders of magnitude
"""

import numpy as np


# ============================================================================
# Simulation function
# ============================================================================

"""
ADM1 is a stiff ODE (Ordinary Differential Equation)system — meaning it contains reactions that operate on
very different timescales simultaneously:
  - Fast: acid-base equilibria (milliseconds to seconds)
  - Medium: hydrolysis and acidogenesis (hours to days)
  - Slow: methanogenesis and biomass decay (days to weeks)

Explicit solvers like RK45 are forced to take tiny timesteps to track the
fast reactions, making them extremely slow on stiff systems.
Implicit solvers like BDF and Radau can take large timesteps even when some
reactions are fast, making them far more efficient here.

t_step controls the output resolution only — it does NOT affect solver accuracy.
The solver internally uses adaptive timestepping regardless of t_step.

Other available methods (pass as method= argument):
  'RK45'   — explicit Runge-Kutta, good for non-stiff systems (will be slow here)
  'Radau'  — implicit Runge-Kutta, also suitable for stiff systems
  'LSODA'  — switches automatically between stiff and non-stiff solvers

See: https://docs.scipy.org/doc/scipy/reference/generated/scipy.integrate.solve_ivp.html
"""


def run_simulation(sys, t, t_step, method):

    sys.simulate(
        # clear any cached state before solving
        state_reset_hook='reset_cache',
        # integrate from day 0 to day t
        t_span=(0, t),
        # time points at which to record output
        t_eval=np.arange(0, t + t_step, t_step),
        method=method,
    )


"""
Parameter	        Value	                          Meaning
state_reset_hook	'reset_cache'	                  Clears any leftover solver state before starting — ensures a clean run from the initial conditions set in system.py
t_span	          (0, t)	                        Integration window — solver runs from day 0 to day t
t_eval	          np.arange(0, t+t_step, t_step)	Time points where results are saved — e.g. [0, 0.1, 0.2, ..., 10.0]. Output resolution only, not solver accuracy
method	          'BDF'	                          ODE algorithm passed through from main.py
"""
