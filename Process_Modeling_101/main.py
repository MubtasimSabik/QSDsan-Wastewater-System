# 1
# main.py

import warnings
import streams_and_components
import system_setup
# import initialization_startup # alternative to initialization.py for simulating startup from near-zero conditions
import initialization
import simulation

# Silence warnings (same as original notebook)
warnings.filterwarnings('ignore')

# Order of imports matters because each module runs its logic at import time:

# 1. Create components and streams

# 2. Build reactors and system

# 3. Load initial conditions and set them

# 4. Run dynamic simulation and plotting


if __name__ == "__main__":
    # All work is already done during imports.
    # This file exists to be the single entry point.
    pass
