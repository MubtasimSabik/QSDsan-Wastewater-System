# 6
# visualization.py

"""
1. Plots influent and effluent time series for all ASM2d state variables

2. Plots focused nitrogen removal indicators (NH4, NO3) and dissolved oxygen

3. The influent plot should appear flat (constant feed); the effluent shows
   how treatment evolves over the simulation period
"""

import matplotlib.pyplot as plt

plt.rcParams['figure.dpi'] = 100
plt.rcParams['savefig.dpi'] = 100


# ============================================================================
# Results plotting
# ============================================================================

"""
Each call to plot_time_series() opens a new figure window showing how the
specified state variables evolve over the simulated time period.

The .scope attribute on a tracked stream stores the full concentration history
recorded during simulation — it is populated by set_dynamic_tracker() in simulation.py.
"""


def plot_results(influent, effluent):

    # -----------------------------------------------------------------------
    # Influent
    # -----------------------------------------------------------------------

    # Influent: time series for all ASM2d state variables (should be flat — influent is constant)
    fig, ax = influent.scope.plot_time_series((
        'S_I', 'X_I', 'S_F', 'S_A', 'X_S', 'S_NH4', 'S_N2', 'S_NO3',
        'S_PO4', 'X_PP', 'X_PHA', 'X_H', 'X_AUT', 'X_PAO', 'S_ALK'
    ))
    ax.set_title('Influent — All ASM2d State Variables')

    # -----------------------------------------------------------------------
    # Effluent
    # -----------------------------------------------------------------------

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
