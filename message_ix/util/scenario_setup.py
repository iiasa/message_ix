import logging
from typing import TYPE_CHECKING, Any, Literal, TypeVar, Union, cast

import pandas as pd

if TYPE_CHECKING:
    from ixmp4 import Run
    from ixmp4.core import IndexSet, Parameter, Table

    from message_ix.core import Scenario

from ixmp import Platform

from message_ix.util.ixmp4 import on_ixmp4backend

from .scenario_data import (
    DEFAULT_INDEXSET_DATA,
    DEFAULT_PARAMETER_DATA,
    DEFAULT_TABLE_DATA,
)

log = logging.getLogger(__name__)


# NOTE This is currently not in use because we don't use scenario_data for this, but
# models.py. We may want to keep something like below's function should that change.
# TODO If this is writing every single addition to the DB, the following is slow. Could
# we tell sqlalchemy to only commit to the DB at the end of this function?
# def set_up_scenario(scenario: "Scenario") -> None:
#     """Create all optimization items required by MESSAGEix in `scenario`.

#     (According to ixmp_source.)
#     """
#     if not on_ixmp4backend(scenario):
#         return
#
#     # Get the Run associated with the Scenario
#     run = cast("Run", scenario.platform._backend.index[scenario])

#     # Add all required IndexSets
#     for indexset_name in REQUIRED_INDEXSETS:
#         run.optimization.indexsets.create(name=indexset_name)

#     # Add all required Tables
#     for table_info in REQUIRED_TABLES:
#         run.optimization.tables.create(
#             name=table_info.name,
#             constrained_to_indexsets=table_info.indexsets,
#             column_names=table_info.column_names,
#         )

#     # Add all required Parameters
#     for parameter_info in REQUIRED_PARAMETERS:
#         run.optimization.parameters.create(
#             name=parameter_info.name,
#             constrained_to_indexsets=parameter_info.indexsets,
#             column_names=parameter_info.column_names,
#         )

#     # Add all required Variables
#     for variable_info in REQUIRED_VARIABLES:
#         run.optimization.variables.create(
#             name=variable_info.name,
#             constrained_to_indexsets=variable_info.indexsets,
#             column_names=variable_info.column_names,
#         )

#     # Add all required Equations
#     for equation_info in REQUIRED_EQUATIONS:
#         run.optimization.equations.create(
#             name=equation_info.name,
#             constrained_to_indexsets=equation_info.indexsets,
#             column_names=equation_info.column_names,
#         )


def add_default_data(scenario: "Scenario") -> None:
    """Add default data expected in a MESSAGEix Scenario."""
    if not on_ixmp4backend(scenario):
        return

    # Get the Run associated with the Scenario
    run = cast("Run", scenario.platform._backend.index[scenario])

    # Add IndexSet data
    for indexset_data_info in DEFAULT_INDEXSET_DATA:
        indexset = run.optimization.indexsets.get(name=indexset_data_info.name)

        # Only add default data if they are missing
        # NOTE this works because all DEFAULT_INDEXSET_DATA items have str-type data
        if missing := [
            item for item in indexset_data_info.data if item not in indexset.data
        ]:
            indexset.add(data=list(missing))

    # Add Table data
    for table_data_info in DEFAULT_TABLE_DATA:
        table = run.optimization.tables.get(name=table_data_info.name)

        # Only add default data if they are missing
        # NOTE this works because all DEFAULT_TABLE_DATA items have just one row
        if not pd.DataFrame(table_data_info.data).isin(table.data).all(axis=None):
            table.add(data=table_data_info.data)

    # Add Parameter data
    for parameter_data_info in DEFAULT_PARAMETER_DATA:
        parameter_df = pd.DataFrame(parameter_data_info.data)

        # NOTE parameter_data_info.data *must* contain a 'unit' column
        check_existence_of_units(platform=scenario.platform, data=parameter_df)

        parameter = run.optimization.parameters.get(name=parameter_data_info.name)

        # Only add default data if they are missing
        # NOTE this works because all DEFAULT_PARAMETER_DATA items have just one row
        if not parameter_df.isin(parameter.data).all(axis=None):
            parameter.add(data=parameter_data_info.data)


# TODO Should this really be a ValueError?
def ensure_required_indexsets_have_data(scenario: "Scenario") -> None:
    """Ensure that required IndexSets contain *some* data.

    The checked IndexSets are: ("node", "technology", "year", "time").

    Raises
    ------
    ValueError
        If the required IndexSets are empty.
    """
    if not on_ixmp4backend(scenario):
        return

    indexsets_to_check = ("node", "technology", "year", "time")

    # Get the Run associated with the Scenario
    run = cast("Run", scenario.platform._backend.index[scenario])

    # Raise an error if any of the checked IndexSets are empty
    for name in indexsets_to_check:
        indexset = run.optimization.indexsets.get(name=name)
        # NOTE this is prone to failure should ixmp4 make indexset.data optional
        if indexset.data == []:
            raise ValueError(f"The required IndexSet {name} is empty!")


def _maybe_add_to_table(
    table: "Table", data: Union[dict[str, Any], pd.DataFrame]
) -> None:
    """Add (parts of) `data` to `table` if they are missing."""
    # NOTE This function doesn't handle empty data as internally, this won't happen

    # Convert to DataFrame for subsequent logic
    if isinstance(data, dict):
        data = pd.DataFrame(data)

    # Keep only rows that don't already exist
    new_data = data[~data.isin(table.data).all(axis=1)]

    # Add new rows to table data
    table.add(data=new_data)


def compose_dimension_map(
    scenario: "Scenario", dimension: Literal["node", "time"]
) -> None:
    """Add data to dimension maps.

    This covers `assignDisaggregationMaps()` from ixmp_source.

    Parameters
    ----------
    scenario: Scenario
        The Scenario object holding the data.
    dimension: 'node' or 'time'
        Whether to handle the spatial or temporal dimension.
    """
    if not on_ixmp4backend(scenario):
        return

    # Get the Run associated with the Scenario
    run = cast("Run", scenario.platform._backend.index[scenario])

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

    # Merge descendant data to original map
    new_map_df = data.merge(pd.DataFrame(descendant_data), how="outer")

    # Add new rows to map_{dimension} data
    _maybe_add_to_table(table=map_parameter, data=new_map_df)


def _maybe_add_single_item_to_indexset(
    indexset: "IndexSet", data: Union[float, int, str]
) -> None:
    """Add `data` to `indexset` if it is missing."""
    if data not in list(indexset.data):
        indexset.add(data=data)


def _maybe_add_list_to_indexset(
    indexset: "IndexSet", data: Union[list[float], list[int], list[str]]
) -> None:
    """Add missing parts of `data` to `indexset`."""
    # NOTE missing will always only have one type, but how to tell mypy?
    # NOTE mypy recognizes missing as set[float | str]. If int indexsets mysteriously
    # turn to float indexsets, look here
    if missing := set(data) - set(indexset.data):
        indexset.add(list(missing))  # type: ignore[arg-type]


def _maybe_add_to_indexset(
    indexset: "IndexSet",
    data: Union[float, int, str, list[float], list[int], list[str]],
) -> None:
    """Add (parts of) `data` to `indexset` if they are missing."""
    # NOTE This function doesn't handle empty data as internally, this won't happen
    if not isinstance(data, list):
        _maybe_add_single_item_to_indexset(indexset=indexset, data=data)
    else:
        _maybe_add_list_to_indexset(indexset=indexset, data=data)


# NOTE this could be combined with `_maybe_add_to_table()`, but that function would be
# slower than necessary (though likely not by much). Is the maintenance effort worth it?
def _maybe_add_to_parameter(
    parameter: "Parameter", data: Union[dict[str, Any], pd.DataFrame]
) -> None:
    """Add (parts of) `data` to `parameter` if they are missing."""
    # NOTE This function doesn't handle empty data as internally, this won't happen

    # Convert to DataFrame for subsequent logic
    if isinstance(data, dict):
        data = pd.DataFrame(data)

    # Only compare entries of specific columns (not of `values` and `units`)
    columns = parameter.column_names or parameter.indexset_names

    # Keep only rows that don't already exist
    new_data = (
        data[~data[columns].isin(pd.DataFrame(parameter.data)[columns]).all(axis=1)]
        if bool(parameter.data)
        else data
    )

    # Add new rows to table data
    parameter.add(data=new_data)


def compose_maps(scenario: "Scenario") -> None:
    """Compose maps.

    - Call :func:`compose_dimension_map` for:

      - :py:`dimension="node"`
      - :py:`dimension="time"`

    - Call :func:`compose_period_map`.
    """
    # Compose some auxiliary tables
    for dimension in ("node", "time"):
        compose_dimension_map(scenario=scenario, dimension=dimension)

    compose_period_map(scenario=scenario)


def compose_period_map(scenario: "Scenario") -> None:
    """Add data to the 'duration_period' Parameter in `scenario`.

    This covers `assignPeriodMaps()` from ixmp_source.
    """
    if not on_ixmp4backend(scenario):
        return

    # Get the Run associated with the Scenario
    run = cast("Run", scenario.platform._backend.index[scenario])

    # TODO Included here in ixmp_source; this should likely move to add_default_data
    # Add one default item to 'type_year'
    type_year = run.optimization.indexsets.get(name="type_year")
    _maybe_add_to_indexset(indexset=type_year, data="cumulative")

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
            _maybe_add_to_indexset(indexset=type_year, data=y_str)
            _maybe_add_to_table(
                table=cat_year,
                data={"type_year": ["cumulative", y_str], "year": [y_str, y_str]},
            )

    # Initialize duration_period with this data
    duration_period = run.optimization.parameters.get(name="duration_period")
    durations = [
        sorted_years[i] - sorted_years[i - 1] for i in range(len(sorted_years))
    ]

    # Correct very first duration: Assume it's equal to second period or 1 if there is
    # no second period
    durations[0] = durations[1] if len(sorted_years) > 1 else 1

    # Add data to `duration_period`
    _maybe_add_to_parameter(
        parameter=duration_period,
        data={
            "year": [str(y) for y in sorted_years],
            "values": durations,
            "units": ["y"] * len(sorted_years),
        },
    )


def check_existence_of_units(platform: Platform, data: pd.DataFrame) -> None:
    """Check if all units requested for use in `data` exist on the `platform`.

    Create them if they don't exist, but warn that this will be disabled in the future.

    Parameters
    ----------
    platform : ixmp.Platform
        The platform to check.
    data : pd.DataFrame
        The data containing the requested units.
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
