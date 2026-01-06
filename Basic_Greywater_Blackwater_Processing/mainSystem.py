import qsdsan as qs

from components import build_cmps
from BlackwaterBuild import make_blackwater
from GreywaterBuild import make_greywater
from COD_MBR import CODBasedMBR
from COD_AnaerobicDigester import CODAnaerobicDigester


def print_stream_summary(stream, label: str, nonzero_only: bool = True, tol: float = 1e-12):
    print(f"\n--- {label} ---")
    print(f"ID: {stream.ID}")

    # Total mass flow
    """
    We access the F_mass attribute of stream. But it's not always guaranteed in QSDsan so we do try/except."
   """
    try:
        print(f"Total mass flow: {stream.F_mass / 1000:.6g} kg/hr")
    except Exception:
        pass

    # Phase (useful now that we have gas streams)
    try:
        print(f"Phase: {stream.phase}")
    except Exception:
        pass

    """
    With try/except we try the common components from a stream
    """
    # Concentration metrics (only meaningful for liquids)
    if getattr(stream, "phase", None) != "g":
        for attr in ("COD", "TN", "TP", "TSS"):
            try:
                print(f"{attr}: {getattr(stream, attr):.6g} mg/L")
            except Exception:
                continue

    # Component mass rates
    
    print("Component mass rates (g/hr):")
    printed_any = False
    for cid in stream.components.IDs:
        try:
            mass = float(stream.imass[cid])  # g/hr
            if abs(mass) > 1e-12:
                print(f"  {cid}: {mass:.6g}")
                printed_any = True
        except Exception:
            continue

    if not printed_any:
        print("  (all components ~0)")


""
"This function computes the percentage removal of the given metrics - COD, TN, TP, TSS; between influent and effluent streams."
"Currently needs rework.."
""


def percent_removal(influent, effluent, attr):
    try:
        vin = getattr(influent, attr)
        vout = getattr(effluent, attr)
        if vin == 0:
            return None
        return 100.0 * (vin - vout) / vin
    except Exception:
        return None


# -------------------
# System construction
# -------------------

"This block creates the system based on the defined functions described above."


def build_system(population: float):

    
    # Create influent streams

    gw = make_greywater(population)     # calls the GreywaterBuild.py file based on defined population number.
    bw = make_blackwater(population)  # calls the BlackwaterBuild.py file based on defined population number.

    # Units

    mbr = CODBasedMBR(
        ID="U_MBR",
        ins=gw,
        outs=("mbr_effluent", "mbr_sludge"),
        # These are the MBR's performance metrics
        COD_removal=0.85,
        solids_capture=0.995,
        NH4_removal=0.2,
        PO4_removal=0.0,
        particulate_IDs=("X_B_Subst",),
        # We can edit these.
    )

    ad = CODAnaerobicDigester(
        ID="U_AD",
        ins=bw,
        outs=("digestate", "biogas"),
        COD_removal=0.60,
        # We can edit these.
    )

    sys = qs.System("Household_System", path=(mbr, ad))
    return sys, gw, bw, mbr, ad


# --------------
# Main execution
# --------------


if __name__ == "__main__":

    # 1) Thermodynamics / components (exactly once)

    """
    We run the simulation based on our custom list of components defined in the components.py. 
    Here we call the build_cmps_greywater function and generate our custom list of components. 
    set_thermo the internal function of QSDsan generates the thermodynamics of our defined components, it already has references in the library. 
    For COD_based streams the components were already defined, here it is not. We are specifically saying - 
    Every stream from now on uses this component set..
    """

    components = build_cmps()
    qs.set_thermo(components)

    # 2) Build + simulate system
    population = 10000  # We control population here..
    system, greywater, blackwater, mbr, ad = build_system(population)

    print(f"\nRunning simulation for population of {population}.")

    print_stream_summary(greywater, "Influent Greywater (pre-simulation)")
    print_stream_summary(blackwater, "Influent Blackwater (pre-simulation)")

    system.simulate()

    # 3) Outputs (read from units, not system.outs)
    mbr_effluent = mbr.outs[0]
    mbr_sludge = mbr.outs[1] if len(mbr.outs) > 1 else None

    digestate = ad.outs[0]
    biogas = ad.outs[1]

    print_stream_summary(mbr_effluent, "MBR Effluent")
    if mbr_sludge is not None:
        print_stream_summary(mbr_sludge, "MBR Sludge")

    print_stream_summary(digestate, "AD Digestate")
    print_stream_summary(biogas, "AD Biogas")

    # 4) Removal performance (per-train)
    for metric in ("COD", "TN", "TP", "TSS"):
        r = percent_removal(greywater, mbr_effluent, metric)
        if r is not None:
            print(f"\n[Greywater→MBR] {metric} removal: {r:.2f}%")

    for metric in ("COD", "TN", "TP", "TSS"):
        r = percent_removal(blackwater, digestate, metric)
        if r is not None:
            print(f"\n[Blackwater→AD] {metric} removal: {r:.2f}%")

