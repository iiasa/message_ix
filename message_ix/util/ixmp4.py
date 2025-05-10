from typing import Union

import ixmp
import ixmp.backend


def configure_logging_and_warnings() -> None:
    """Quiet verbose log and warning messages from :mod:`ixmp4`.

    These include:

    1. Log messages with level WARNING on logger ixmp4.data.db.base: “Dispatching a
       versioned insert statement on an 'sqlite' backend. This might be very slow!”
    2. :py:`PydanticDeprecatedSince211` (a subclass of :class:`DeprecationWarning`) in
       :py:`ixmp4.db.filters`: “Accessing the 'model_fields' attribute on the instance
       is deprecated.”
    3. :class:`pandas.errors.SettingWithCopyWarning` in :py:`ixmp4.data.db.base` at
       L589, L590, L621.
    4. :class:`DeprecationWarning` for calling :meth:`datetime.datetime.now`.
    """
    import logging
    import warnings

    from pandas.errors import SettingWithCopyWarning

    logging.getLogger("ixmp4.data.db.base").setLevel(logging.WARNING + 1)

    warnings.filterwarnings(
        "ignore",
        ".*Accessing the 'model_fields' attribute on the instance.*",
        DeprecationWarning,  # Actually pydantic.PydanticDeprecatedSince211
        "ixmp4.db.filters",
    )
    warnings.filterwarnings(
        "ignore",
        ".*A value is trying to be set on a copy of a slice from a DataFrame.*",
        SettingWithCopyWarning,
        "ixmp4.data.db.base",
    )
    warnings.filterwarnings(
        "ignore", "datetime.datetime.now", DeprecationWarning, "sqlalchemy.sql.schema"
    )


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
