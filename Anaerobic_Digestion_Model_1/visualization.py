# 6
# visualization.py

"""
1. Plots effluent VFA and fatty acid concentrations over time — key indicators
   of fermentation activity and organic loading

2. Plots effluent inorganic carbon (S_IC) — indicator of buffering capacity and pH stability

3. Plots active microbial biomass concentrations in the effluent — shows community dynamics

4. Plots dissolved H2 and CH4 in the biogas — main process performance indicators

5. Computes and plots total VFA (sum of S_va + S_bu + S_pro + S_ac) — a single
   composite indicator of process stability
"""

import matplotlib.pyplot as plt
import numpy as np

plt.rcParams['figure.dpi'] = 100
plt.rcParams['savefig.dpi'] = 100


# ============================================================================
# Results plotting
# ============================================================================

"""
Each call to plot_time_series() opens a new figure window showing how the
specified state variables evolve over the simulated time period.

The .scope attribute on a tracked stream stores the full concentration history
recorded during simulation — it is populated by set_dynamic_tracker() in system.py.
"""


def plot_results(eff, gas, cmps):

    # -----------------------------------------------------------------------
    # Effluent liquid phase
    # -----------------------------------------------------------------------

    # VFAs and fatty acids — rising VFAs signal fermentation accumulation
    # (possible overloading or methanogen inhibition)
    _, ax = eff.scope.plot_time_series(
        ('S_aa', 'S_fa', 'S_va', 'S_bu', 'S_pro', 'S_ac'))
    ax.set_title('Effluent — VFAs and Fatty Acids')

    # Inorganic carbon — high S_IC indicates good CO2 production and buffering;
    # a drop in S_IC can signal pH instability
    _, ax = eff.scope.plot_time_series(('S_IC',))
    ax.set_title('Effluent — Inorganic Carbon (S_IC)')

    # Active biomass — shows how each microbial group grows, washes out, or stabilises
    _, ax = eff.scope.plot_time_series(
        ('X_aa', 'X_fa', 'X_c4', 'X_pro', 'X_ac', 'X_h2'))
    ax.set_title('Effluent — Active Microbial Biomass')

    # -----------------------------------------------------------------------
    # Biogas phase
    # -----------------------------------------------------------------------

    """
    H2 partial pressure is a critical control variable in ADM1:
    - High H2 inhibits acetogenesis (propionate/butyrate degraders slow down)
    - This causes VFA accumulation, which lowers pH and can inhibit methanogens
    Monitoring S_h2 in the gas phase gives an early warning of process stress.
    """

    # Dissolved hydrogen in biogas — key inhibition indicator
    _, ax = gas.scope.plot_time_series(('S_h2',))
    ax.set_title('Biogas — Dissolved Hydrogen (S_h2)')

    # Methane and inorganic carbon in biogas — main products of successful digestion
    _, ax = gas.scope.plot_time_series(('S_ch4', 'S_IC'))
    ax.set_title('Biogas — Methane and Inorganic Carbon')

    # -----------------------------------------------------------------------
    # Custom total VFA plot
    # -----------------------------------------------------------------------

    """
    Total VFA (S_va + S_bu + S_pro + S_ac) is a single composite stability indicator:
    - Stable digestion: total VFA typically < 500 mg/L
    - Early warning: 500–2000 mg/L (accumulation outpacing methanogenesis)
    - Process failure risk: > 2000 mg/L (pH drop, methanogen inhibition)

    We build this manually using the recorded data matrix:
    - eff.scope.record is a 2-D array with shape (timesteps × components)
    - cmps.indices() returns the column positions for the four VFA components
    - np.sum(..., axis=1) sums across those columns to get a 1-D total VFA profile
    """

    # Column indices of the four VFA components in the concentration data matrix
    idx_vfa = cmps.indices(['S_va', 'S_bu', 'S_pro', 'S_ac'])

    # 1-D array of recorded time points [days]
    t_stamp = eff.scope.time_series
    # 2-D slice: rows = time, cols = VFA components
    vfa = eff.scope.record[:, idx_vfa]
    # sum across VFA columns → total VFA at each timestep
    total_vfa = np.sum(vfa, axis=1)

    plt.figure()
    plt.plot(t_stamp, total_vfa)
    plt.xlabel("Time [day]")
    plt.ylabel("Total VFA [mg/L]")
    plt.title("Total VFA over time")
    plt.show()
