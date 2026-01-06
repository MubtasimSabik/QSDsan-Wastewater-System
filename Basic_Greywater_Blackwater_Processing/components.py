import qsdsan as qs

"""
More info about the Components class - https://qsdsan.readthedocs.io/en/latest/tutorials/2_Component.html
Since it is already a default compiled set of components, we try to uncompile it so we can append our own components.
As a fail safe to uncompile, we convert the variable base into a list.
"""


def build_cmps():
    # we load the default components library in a variable
    base = qs.Components.load_default()

    try:
        cmps = base.uncompile()
    except Exception:
        cmps = qs.Components(list(base))

    """
    The exists() helper function checks whether a component ID is already present in the component list,
    to prevent duplicate component definitions when extending the default library.
    """

    def exists(ID: str) -> bool:
        try:
            cmps.index(ID)  # an index based lookup
            return True
        except Exception:
            try:
                _ = cmps[ID]  # a literal match lookup aka dictionary lookup
                return True
            except Exception:
                # if both lookups fail, it means the component does not exist in the default list.
                return False

    """
    This is the actual function that does the appending part. It defines minimal dissolved components so that sulfate and 
    drugs can be tracked through the system without introducing additional reaction or degradation assumptions.
    """
    # ID, Organic (Yes or No), Degradibility (U means undegradable)
    def append_component(ID: str, organic, degradability: str = "U"):
        # this is where we are calling the function above with ID as the parameter.
        if exists(ID):
            return
        cmp = qs.Component(
            ID=ID,
            # different particle size is available, we use dissolved here
            particle_size="dissolved",
            degradability=degradability,
            organic=organic,
        )
        cmps.append(cmp)
    
    """
    Append a real chemical component in the gas phase (e.g., CH4, CO2) so anaerobic digestion can output
    a chemically meaningful biogas stream.
    """

    def append_gas_chemical(ID: str, search_ID: str, organic: bool):
     
        if exists(ID):
            return
        cmp = qs.Component.from_chemical(
            ID=ID,
            search_ID=search_ID,
            phase="g",
            particle_size="dissolved",  # placeholder; gas phase dominates
            degradability="U",
            organic=organic,
        )
        cmps.append(cmp)

    append_component("S_SO4", organic=False)
    append_component("Diclo", organic=False)
    append_component("Meto",  organic=False)
    append_component("Sulfa", organic=False)
    append_component("Benzo", organic=False)
    append_component("Iome",  organic=False)

    append_gas_chemical("CH4", "CH4", organic=True)
    append_gas_chemical("CO2", "CO2", organic=False)

    # Compile component set
    cmps.compile(skip_checks=True, ignore_inaccurate_molar_weight=True)

    return cmps