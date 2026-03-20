import sys
import faulthandler
faulthandler.enable()
print("step 1: importing streams_and_components")
sys.stdout.flush()
import streams_and_components

print("step 2: importing system_setup")
sys.stdout.flush()
import system_setup

print("step 3: importing initialization")
sys.stdout.flush()
from pathlib import Path
from qsdsan.utils import load_data
data_path = Path("initial_conditions_asm2d.xlsx")
df = load_data(str(data_path), sheet='Sheet1')
print(f"  DataFrame shape: {df.shape}")
print(f"  Index: {list(df.index)}")
print(df)
import initialization

print("step 4: setting up simulation")
sys.stdout.flush()
import numpy as np
from system_setup import sys as qsys, A1, A2, O1, O2, O3, C1
from streams_and_components import influent, effluent, wastage
from qsdsan.utils import get_SRT

qsys.set_dynamic_tracker(influent, effluent, A1, A2, O1, O2, O3, C1, wastage)
qsys.set_tolerance(rmol=1e-6)

print("step 5: running simulation (short test, RK45)")
sys.stdout.flush()
try:
    qsys.simulate(
        state_reset_hook='reset_cache',
        t_span=(0, 1),
        t_eval=np.arange(0, 2, 1),
        method='RK45',
    )
    print("step 6: 1-day RK45 simulation complete")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")

sys.stdout.flush()

print("step 7: running full simulation (BDF)")
sys.stdout.flush()
try:
    qsys.simulate(
        state_reset_hook='reset_cache',
        t_span=(0, 50),
        t_eval=np.arange(0, 51, 1),
        method='BDF',
    )
    print("step 8: full simulation complete")
    srt = get_SRT(qsys, ('X_H', 'X_PAO', 'X_AUT'))
    print(f'SRT: {round(srt, 2)} days')
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
