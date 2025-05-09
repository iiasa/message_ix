from typing import Union

import ixmp
import ixmp.backend


def on_ixmp4backend(obj: Union["ixmp.Platform", "ixmp.TimeSeries"]) -> bool:
    """:any:`True` if `ts` is stored on :class:`IXMP4Backend`.

    .. todo:: Move upstream, to :mod:`ixmp`.
    """
    if "ixmp4" not in ixmp.backend.available():
        return False

    from ixmp.backend.ixmp4 import IXMP4Backend

    return isinstance(
        (obj if isinstance(obj, ixmp.Platform) else obj.platform)._backend,
        IXMP4Backend,
    )


def platform_compat(platform: "ixmp.Platform") -> None:
    """Handle units and regions compatibility.

    This ensures `platform` backed by :class:`IXMP4Backend` has units and regions that
    are automatically populated when using :class:`.JDBCBackend`.
    """
    from message_ix.util.scenario_data import REQUIRED_UNITS

    if not on_ixmp4backend(platform):
        return

    if not platform._units_to_warn_about:
        platform._units_to_warn_about = REQUIRED_UNITS.copy()

    units = set(platform.units())
    for u in {"-", "kg/kWa", "y", "Mt CO2/yr", "USD", "USD/GWa"} - units:
        platform.add_unit(u, "For compatibility with ixmp.JDBCBackend")

    for r in {"India"} - set(platform.regions()["region"]):
        platform.add_region(region=r, hierarchy="common")
