import logging
from typing import TYPE_CHECKING, Literal, TypeVar, cast

import pandas as pd

if TYPE_CHECKING:
    from message_ix.core import Scenario

from ixmp import Platform
from ixmp4 import Run

from .scenario_data import (
    DEFAULT_INDEXSET_DATA,
    DEFAULT_PARAMETER_DATA,
    DEFAULT_TABLE_DATA,
    REQUIRED_EQUATIONS,
    REQUIRED_INDEXSETS,
    REQUIRED_PARAMETERS,
    REQUIRED_TABLES,
    REQUIRED_VARIABLES,
)

log = logging.getLogger(__name__)

# TODO If this is writing every single addition to the DB, the following is slow. Could
# we tell sqlalchemy to only commit to the DB at the end of this function?


def set_up_scenario(scenario: "Scenario") -> None:
    """Create all optimization items required by MESSAGEix.

    (According to ixmp_source.)
    """
    # NOTE this assumes an IXMP4Backend
    # Get the Run associated with the Scenario
    run = cast(Run, scenario.platform._backend.index[scenario])

    # Add all required IndexSets
    for indexset_name in REQUIRED_INDEXSETS:
        run.optimization.indexsets.create(name=indexset_name)

    # Add all required Tables
    for table_info in REQUIRED_TABLES:
        run.optimization.tables.create(
            name=table_info.name,
            constrained_to_indexsets=table_info.indexsets,
            column_names=table_info.column_names,
        )

    # Add all required Parameters
    for parameter_info in REQUIRED_PARAMETERS:
        run.optimization.parameters.create(
            name=parameter_info.name,
            constrained_to_indexsets=parameter_info.indexsets,
            column_names=parameter_info.column_names,
        )

    # Add all required Variables
    for variable_info in REQUIRED_VARIABLES:
        run.optimization.variables.create(
            name=variable_info.name,
            constrained_to_indexsets=variable_info.indexsets,
            column_names=variable_info.column_names,
        )

    # Add all required Equations
    for equation_info in REQUIRED_EQUATIONS:
        run.optimization.equations.create(
            name=equation_info.name,
            constrained_to_indexsets=equation_info.indexsets,
            column_names=equation_info.column_names,
        )


def add_default_data(scenario: "Scenario") -> None:
    """Add default data expected in a MESSAGEix Scenario."""
    # NOTE this assumes an IXMP4Backend
    # Get the Run associated with the Scenario
    run = cast(Run, scenario.platform._backend.index[scenario])

    # Add IndexSet data
    for indexset_data_info in DEFAULT_INDEXSET_DATA:
        run.optimization.indexsets.get(name=indexset_data_info.name).add(
            data=indexset_data_info.data
        )

    # Add Table data
    for table_data_info in DEFAULT_TABLE_DATA:
        run.optimization.tables.get(name=table_data_info.name).add(
            data=table_data_info.data
        )

    # Add Parameter data
    for parameter_data_info in DEFAULT_PARAMETER_DATA:
        # NOTE parameter_data_info.data *must* contain a 'unit' column
        check_existence_of_units(
            platform=scenario.platform, data=pd.DataFrame(parameter_data_info.data)
        )
        run.optimization.parameters.get(name=parameter_data_info.name).add(
            data=parameter_data_info.data
        )


# TODO Should this really be a ValueError?
def ensure_required_indexsets_have_data(scenario: "Scenario") -> None:
    """Ensure that required IndexSets contain *some* data.

    The checked IndexSets are: ("node", "technology", "year", "time").

    Raises
    ------
    ValueError
        If the required IndexSets are empty.
    """
    indexsets_to_check = ("node", "technology", "year", "time")

    # NOTE this assumes an IXMP4Backend
    # Get the Run associated with the Scenario
    run = cast(Run, scenario.platform._backend.index[scenario])

    # Raise an error if any of the checked IndexSets are empty
    for name in indexsets_to_check:
        indexset = run.optimization.indexsets.get(name=name)
        # NOTE this is prone to failure should ixmp4 make indexset.data optional
        if indexset.data == []:
            raise ValueError(f"The required IndexSet {name} is empty!")


def compose_dimension_map(
    scenario: "Scenario", dimension: Literal["node", "time"]
) -> None:
    """Add data to dimension maps.

    This covers assignDisaggregationMaps() from ixmp_source.

    Parameters
    ----------
    scenario: Scenario
        The Scenario object holding the data.
    dimension: 'node' or 'time'
        Whether to handle the spatial or temporal dimension.
    """
    # NOTE this assumes an IXMP4Backend
    # Get the Run associated with the Scenario
    run = cast(Run, scenario.platform._backend.index[scenario])

    # Handle both spatial and temporal dimensions
    name_part = "spatial" if dimension == "node" else "temporal"

    # Load Tables
    hierarchy_map = pd.DataFrame(
        run.optimization.tables.get(name=f"map_{name_part}_hierarchy").data
    )
    # TODO do we want to call this function when 'hierarchy_map' is empty? If not,
    # remove this:
    if hierarchy_map.empty:
        return

    map_parameter = run.optimization.tables.get(name=f"map_{dimension}")

    # Create auxiliary variables
    dimension_items = set(hierarchy_map[f"{dimension}"].to_list()) | set(
        hierarchy_map[f"{dimension}_parent"].to_list()
    )
    self_map = pd.DataFrame(
        [(dim, dim) for dim in dimension_items],
        columns=[f"{dimension}", f"{dimension}_parent"],
    )

    # Create original map with self-maps and direct descendants
    data = hierarchy_map.drop(columns=f"lvl_{name_part}").merge(self_map, how="outer")

    # Group for recursion
    grouped = data.groupby(f"{dimension}_parent", sort=False)

    T = TypeVar("T", int, str)

    def _find_all_descendants(parent: T) -> list[T]:
        """Find all descendants of parent dimension by recursion."""
        _descendants: list[T] = []
        base = grouped.get_group(parent)
        if len(base) == 1:
            # descendants.append(parent)
            pass
        else:
            for _dim in base[base[f"{dimension}"] != base[f"{dimension}_parent"]][
                f"{dimension}"
            ]:
                _descendants.append(_dim)
                _descendants.extend(_find_all_descendants(parent=_dim))
        return _descendants

    # Prepare descendant data
    descendant_data: dict[str, list[str] | list[int]] = {
        f"{dimension}": [],
        f"{dimension}_parent": [],
    }

    # Iterate over parents to find all descendants
    for dim in dimension_items:
        descendants = _find_all_descendants(parent=dim)
        if number := len(descendants):
            descendant_data[f"{dimension}"].extend(descendants)
            descendant_data[f"{dimension}_parent"].extend([dim] * number)

    # Add map_{dimension} data after merging descendant data to original map
    map_parameter.add(data=data.merge(pd.DataFrame(descendant_data), how="outer"))


def compose_period_map(scenario: "Scenario") -> None:
    """Add data to the `duration_period` Parameter in `scenario`.

    This covers assignPeriodMaps() from ixmp_source.
    """
    # NOTE this assumes an IXMP4Backend
    # Get the Run associated with the Scenario
    run = cast(Run, scenario.platform._backend.index[scenario])

    # TODO Included here in ixmp_source; this should likely move to add_default_data
    # Add one default item to 'type_year'
    type_year = run.optimization.indexsets.get(name="type_year")
    type_year.add("cumulative")

    cat_year = run.optimization.tables.get(name="cat_year")
    cat_year_df = pd.DataFrame(cat_year.data)

    # Get the first model year for determination of the model horizon below
    first_model_year = None
    if not cat_year_df.empty:
        first_model_year_df = cat_year_df[cat_year_df["type_year"] == "firstmodelyear"]
        assert len(first_model_year_df) <= 1, (
            "A MESSAGEix Scenario can't have multiple first years!"
        )
        first_model_year = (
            int(first_model_year_df["year"][0])
            if not first_model_year_df.empty
            else None
        )

    # Load 'year' data. NOTE that this is somehow converted to str going through ixmp,
    # but we need int for the calculations here, then str to add the data back.
    year = run.optimization.indexsets.get(name="year")
    years = [int(_year) for _year in year.data]

    # TODO do we want to call this function when 'year' is empty? If not remove this:
    if years == []:
        return

    # Ensure that years are sorted
    sorted_years = sorted(years)
    if years != sorted_years:
        year.remove(data=years)
        year.add(data=sorted_years)

    # Store years within the model horizon
    for y in sorted_years:
        if first_model_year is None or first_model_year <= y:
            y_str = str(y)
            type_year.add(y_str)
            cat_year.add({"type_year": ["cumulative", y_str], "year": [y_str, y_str]})

    # Initialize duration_period with this data
    duration_period = run.optimization.parameters.get(name="duration_period")
    durations = [
        sorted_years[i] - sorted_years[i - 1] for i in range(len(sorted_years))
    ]

    # Correct very first duration: Assume it's equal to second period or 1 if there is
    # no second period
    durations[0] = durations[1] if len(sorted_years) > 1 else 1

    # Add data to `duration_period`
    duration_period.add(
        data={
            "year": [str(y) for y in sorted_years],
            "values": durations,
            "units": ["y"] * len(sorted_years),
        }
    )


def check_existence_of_units(platform: Platform, data: pd.DataFrame) -> None:
    """Check if all units requested for use exist on the Platform.

    Create them if they don't exist, but warn that this will be disabled in the future.

    Parameters
    ----------
    platform : ixmp.Platform
        The platform to check.
    units_to_warn_about : list[str]
        The list of unit names that are expected for historical reasons and have not
        been checked before.
    data : pd.DataFrame
        The data containing the requested units.

    Returns
    -------
    list[str]
        The units_to_warn_about minus the ones that were checked.
    """
    # Handle singular and plural form; could there be others?
    try:
        unit_column = data["units"]
    except KeyError:
        unit_column = data["unit"]

    units = unit_column.astype(str).to_list()
    existing_units = platform.units()

    # As long as this function is called after Scenario.__init__() sets
    # '_units_to_warn_about' for this `platform`, this will always be true
    assert platform._units_to_warn_about is not None

    for unit in units:
        if unit in platform._units_to_warn_about and unit not in existing_units:
            log.warning(
                f"Unit '{unit}' does not exist on the Platform! Please adjust your "
                "code to explicitly add all units to the Platform. This will be "
                f"required in the future, but '{unit}' will be added automatically for "
                "now."
            )

            # Add the unit to retain backward compatibility
            platform.add_unit(unit=unit)

            # Ensure each unit is only warned about once
            platform._units_to_warn_about.remove(unit)
