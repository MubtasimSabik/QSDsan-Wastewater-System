import qsdsan as qs


def build_cmps_greywater():
    base = qs.Components.load_default()

    try:
        cmps = base.uncompile()
    except Exception:
        cmps = qs.Components(list(base))

    def exists(ID: str) -> bool:
        try:
            cmps.index(ID)
            return True
        except Exception:
            try:
                _ = cmps[ID]
                return True
            except Exception:
                return False

    def add_placeholder_dissolved(ID: str, organic: bool = False, degradability: str = "U"):
        if exists(ID):
            return
        cmp = qs.Component(
            ID=ID,
            particle_size="dissolved",
            degradability=degradability,
            organic=organic,
        )
        cmps.append(cmp)

    add_placeholder_dissolved("S_SO4", organic=False)
    add_placeholder_dissolved("Diclo", organic=False)
    add_placeholder_dissolved("Meto",  organic=False)
    add_placeholder_dissolved("Sulfa", organic=False)
    add_placeholder_dissolved("Benzo", organic=False)
    add_placeholder_dissolved("Iome",  organic=False)

    cmps.compile(skip_checks=True, ignore_inaccurate_molar_weight=True)
    return cmps
