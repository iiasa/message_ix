import ixmp
import ixmp.backend
from ixmp.util.ixmp4 import is_ixmp4backend


def platform_compat(platform: "ixmp.Platform") -> None:
    """Handle units and regions compatibility.

    This ensures `platform` backed by :class:`IXMP4Backend` has units and regions that
    are automatically populated when using :class:`.JDBCBackend`.
    """
    from message_ix.util.scenario_data import REQUIRED_UNITS

    if not is_ixmp4backend(platform._backend):
        return

    if not platform._units_to_warn_about:
        platform._units_to_warn_about = REQUIRED_UNITS.copy()

    units = set(platform.units())
    for u in {"-", "kg/kWa", "y", "Mt CO2/yr", "USD", "USD/GWa"} - units:
        platform.add_unit(u, "For compatibility with ixmp.JDBCBackend")

    for r in {"India"} - set(platform.regions()["region"]):
        platform.add_region(region=r, hierarchy="common")
