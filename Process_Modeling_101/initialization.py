# 4
# initialization.py

"""
1. Builds the path to the Excel file containing initial conditions for all reactors

2. Defines batch_init() — a function that reads each reactor's row from the DataFrame
   and sets its initial concentrations using the appropriate QSDsan method

3. Defines load_initial_conditions() — the main entry point called from main.py:
   loads the Excel file and applies initial conditions to the system
"""

from qsdsan.utils import load_data
from pathlib import Path


# ============================================================================
# 1. Locate the initial conditions file
# ============================================================================

"""
We use Path(__file__) to build the path relative to this script's location,
so it works regardless of where you run Python from (avoids "file not found" errors
caused by the working directory being different from the script directory).
"""

# Absolute path to this script's parent directory
BASE_DIR = Path(__file__).resolve().parent

# Path to the Excel file containing initial concentrations for each reactor
data_path = BASE_DIR / "initial_conditions_asm2d.xlsx"

"""
The Excel file has one row per reactor (A1, A2, O1, O2, O3) with columns
for each ASM2d state variable. The clarifier (C1) is split across 3 rows:
- C1_s: soluble components
- C1_x: particulate (sludge solids) components
- C1_tss: TSS profile across each of the 10 clarifier layers
Change the file name above if your file is named differently.
"""


# ============================================================================
# 2. Batch initialization function
# ============================================================================

def batch_init(sys, df):
    """Apply initial concentrations from the DataFrame to each unit in the system."""

    # Convert the DataFrame to a nested dictionary: {reactor_ID: {component: value, ...}}
    dct = df.to_dict('index')

    # Access the unit registry via the flowsheet — lets us look up units by name (e.g., u.A1)
    u = sys.flowsheet.unit

    # For the 5 bioreactors, set_init_conc() accepts keyword arguments for each state variable
    for k in [u.A1, u.A2, u.O1, u.O2, u.O3]:
        k.set_init_conc(**dct[k._ID])   # k._ID is the unit's string ID (e.g., 'A1')

    """
    The clarifier uses three separate methods instead of one, because the 1D settler
    tracks solubles, particulates, and TSS separately across its 10 vertical layers.
    We also filter out zeros (if v > 0) to only pass components with non-zero initial values.
    """

    # Extract non-zero soluble initial concentrations for C1
    c1s = {k: v for k, v in dct['C1_s'].items() if v > 0}

    # Extract non-zero sludge solids initial concentrations for C1
    c1x = {k: v for k, v in dct['C1_x'].items() if v > 0}

    # Extract non-zero TSS values across the 10 clarifier layers
    tss = [v for v in dct['C1_tss'].values() if v > 0]

    u.C1.set_init_solubles(**c1s)          # set soluble component concentrations
    u.C1.set_init_sludge_solids(**c1x)     # set particulate component concentrations
    u.C1.set_init_TSS(tss)                 # set TSS profile (one value per layer)


# ============================================================================
# 3. Load and apply initial conditions
# ============================================================================

def load_initial_conditions(sys):
    """Load initial conditions from Excel and apply them to the system."""

    # Raise a clear error early if the file is missing, rather than a cryptic crash later
    if not data_path.is_file():
        raise FileNotFoundError(
            f"Could not find initial conditions file at: {data_path}")

    # load_data returns a pandas DataFrame with reactor IDs as the index
    # Change the sheet name here if your Excel file uses a different sheet
    df = load_data(str(data_path), sheet='Sheet1')

    batch_init(sys, df)
