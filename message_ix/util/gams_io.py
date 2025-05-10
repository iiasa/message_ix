from typing import TYPE_CHECKING, Literal, Optional, Union, cast

import pandas as pd

if TYPE_CHECKING:
    from message_ix.core import Scenario

from ixmp.util.ixmp4 import ContainerData

from .scenario_data import (
    HELPER_INDEXSETS,
    HELPER_TABLES,
    HelperFilterInfo,
    HelperIndexSetInfo,
    HelperTableInfo,
)

# MESSAGE scheme version
# This value is used by MsgScenario in two ways:
#    1. To generate commit/exception messages in .checkOut() and
#       .updateMsgScheme() related to use of initializeMsgSetsParameters().
# 	    These methods do not check this value, nor is it stored (except as a
# 	    commit message).
# 	 2. In .toGDX(), it is written to the GAMS parameter "MESSAGE_ix_version"
# 	    to signal to the GAMS code which version of ixmp_source was used to
# 	    generate a particular GDX file.
# 	 Increment *only* in the event that the generated GDX contents change in a
# 	 way that requires corresponding changes to the MESSAGE GAMS source.
# 	 See also https://github.com/iiasa/message_ix/issues/254.

# MESSAGE_IX_VERSION = {
# 		{ "major": 2 }, { "minor": 0 }
# 	}

# This must be convertible to pd.DataFrame
MESSAGE_IX_VERSION: dict[str, Union[list[float], list[int], list[str]]] = {
    "version_part": ["major", "minor"],
    "value": [2, 0],
}


def store_message_version(container_data: list[ContainerData]) -> None:
    """Store 'MESSAGE_ix_version' in `container_data` for validation by GAMS."""
    # Add a helper IndexSet
    container_data.append(
        ContainerData(
            name="version_part",
            kind="IndexSet",
            records=MESSAGE_IX_VERSION["version_part"],
        )
    )
    # Add the actual parameter
    container_data.append(
        ContainerData(
            name="MESSAGE_ix_version",
            kind="Parameter",
            domain=["version_part"],
            records=MESSAGE_IX_VERSION,
        )
    )


def add_default_data_to_container_data_list(
    container_data: list[ContainerData],
    name: Literal["cat_tec", "type_tec_land"],
    scenario: "Scenario",
) -> None:
    """Add default data for item `name` to `container_data`."""
    # Gather existing data for `name` from `scenario`
    records = scenario.set(name=name)
    domain = scenario.idx_sets(name=name)

    # Set the default data to be added
    if name == "cat_tec":
        technologies = cast(pd.Series, scenario.set(name="technology"))
        data = {
            "type_tec": ["all"] * len(technologies),
            "technology": technologies.to_list(),
        }
    else:
        data = {"type_tec": ["all"]}

    additional_records = pd.DataFrame(data)

    # Merge default data with existing data
    records = pd.concat([records, additional_records], ignore_index=True)

    # Add complete data to `container_data`
    container_data.append(
        ContainerData(name=name, kind="Table", domain=domain, records=records)
    )


def _compose_resource_grade_map(
    scenario: "Scenario",
) -> dict[tuple[str, str], list[str]]:
    """Compose the helper data structure `resource_grade_map`."""
    # 'resource_grade_map' maps ["node", "commodity"] to ["grade"]
    resource_grade_map: dict[tuple[str, str], list[str]] = {}

    # 'resource_grade_map' is based on 'resource_volume'
    resource_volume = scenario.par(name="resource_volume")

    for row in resource_volume.itertuples(index=False):
        # Create the key from each row
        key = (str(row.node), str(row.commodity))

        # Get existing grade_list or start a new one
        grade_list = resource_grade_map.get(key, [])
        grade_list.append(row.grade)

        # Set the key to grade_list
        resource_grade_map[key] = grade_list

    return resource_grade_map


def _handle_renames(
    df: pd.DataFrame, renames: Optional[dict[str, str]]
) -> pd.DataFrame:
    """Rename columns from `df` according to `renames`, if present."""
    return df.rename(columns=renames) if renames else df


def _handle_empty_parameter(
    scenario: "Scenario",
    source_name: str,
    columns: Optional[list[str]],
    renames: Optional[dict[str, str]] = None,
) -> pd.DataFrame:
    """Create an empty pd.DataFrame with correct column names."""
    _columns = columns or scenario.idx_names(name=source_name)
    record = pd.DataFrame(columns=_columns)
    return _handle_renames(df=record, renames=renames)


def _compose_records(
    scenario: "Scenario",
    sources: dict[str, Optional[list[str]]],
    filters: Optional[HelperFilterInfo],
    renames: Optional[dict[str, str]],
) -> pd.DataFrame:
    """Compose the records for an auxiliary IndexSet/Table.

    Parameters
    ----------
    scenario: Scenario
        The scenario to gather data from.
    sources: dict
        A mapping to specify the sources. Keys are parameter names, values are optional
        columns to limit the data to.
    filters: Optional[HelperFilterInfo]
        Optionally, specify a filter that limits a single column to specific values.
    renames: Optional[dict[str, str]]
        Optionally, rename columns of the records to align them properly.
    """
    # Create a list to collect records
    records: list[pd.DataFrame] = []

    for source_name, columns in sources.items():
        # Copy the scenario data to avoid modifying it
        df = scenario.par(name=source_name).copy()

        # If `df` is empty, add an empty record with correctly named columns
        if df.empty:
            records.append(
                _handle_empty_parameter(
                    scenario=scenario,
                    source_name=source_name,
                    columns=columns,
                    renames=renames,
                )
            )
            continue

        # Apply filters if requested
        if filters:
            df = df.loc[df[filters.column_name].isin(filters.target)]

        # If no columns are specified, exclude 'value' and 'unit' at least because we're
        # composing Table.data
        df = df[columns] if columns else df.drop(columns=["value", "unit"])

        # 'map_relation' and 'map_land': fix mismatch with column names expected by gams
        # 'map_tec' and 'map_commodity': align different column names in their sources
        if renames:
            df.rename(columns=renames, inplace=True)

        # Add record to the collection
        records.append(df)

    # NOTE ixmp_source only adds elements that were not already in records, but here we
    # add everything and drop_duplicates() afterwards
    return pd.concat(records, ignore_index=True).drop_duplicates()


def _compose_map_tec_time(
    scenario: "Scenario", sources: dict[str, Optional[list[str]]]
) -> pd.DataFrame:
    """Compose the records for an auxiliary IndexSet/Table.

    Parameters
    ----------
    scenario: Scenario
        The scenario to gather data from.
    sources: dict
        A mapping to specify the sources. Keys are parameter names, values are optional
        columns to limit the data to.
    """
    records: list[pd.DataFrame] = []

    for source_name, columns in sources.items():
        df = scenario.par(name=source_name).copy()

        if df.empty:
            records.append(
                _handle_empty_parameter(
                    scenario=scenario, source_name=source_name, columns=columns
                )
            )
            continue

        if columns:
            df = df[columns]
        if source_name == "relation_activity":
            # TODO (from ixmp_source) this should be dependent on the correct sub-annual
            # time slice
            # TODO once we fix that, we can likely drop this function and use
            # _compose_records() for `map_tec_time`
            df["time"] = "year"
        records.append(df)

    return pd.concat(records, ignore_index=True).drop_duplicates()


def _compose_map_resource(
    scenario: "Scenario",
    sources: dict[str, Optional[list[str]]],
    filters: Optional[HelperFilterInfo],
    resource_grade_map: dict[tuple[str, str], list[str]],
) -> pd.DataFrame:
    """Compose the records for an auxiliary IndexSet/Table.

    Parameters
    ----------
    scenario: Scenario
        The scenario to gather data from.
    sources: dict
        A mapping to specify the sources. Keys are parameter names, values are optional
        columns to limit the data to.
    filters: Optional[HelperFilterInfo]
        Optionally, specify a filter that limits a single column to specific values.
    resource_grade_map: dict[list[str], list[str]]
        An auxiliary mapping from (`node`, `commodity`) to list of `grade` to construct
        `map_resource`.
    """
    records: list[pd.DataFrame] = []
    columns = ["node_loc", "commodity", "grade", "year_act"]

    # There's just one item here: {`input`: None}
    for source_name, _ in sources.items():
        df = scenario.par(name=source_name).copy()

        if filters:
            df = df.loc[df[filters.column_name].isin(filters.target)]

        # columns is None for map_resource
        # if columns:
        #     df = df[columns]
        df = df.drop(columns=["value", "unit"])

        for row in df.itertuples(index=False):
            key = (str(row.node_loc), str(row.commodity))
            grade_list = resource_grade_map.get(key, None)
            if not grade_list:
                # TODO This used to be an IxException
                # TODO Why do we mention `level` instead of `commodity`?
                raise ValueError(
                    f"the resource-commodity '{row.level}' at node '{row.commodity}'"
                    "does not have a resource volume assigned for any grade!"
                )

            base_record = {
                "node_loc": [row.node_loc],
                "commodity": [row.commodity],
                # NOTE ixmp_source used to have a placeholder here
                # "grade": [grade_list[0]],
                "year_act": [row.year_act],
            }
            for grade in grade_list:
                base_record["grade"] = [grade]

                # Add to collection with correct column order
                records.append(pd.DataFrame(base_record)[columns])

    # For some tutorials, input['level'] is never 'resources', so map is empty
    return (
        pd.concat(records, ignore_index=True).drop_duplicates()
        if len(records)
        else pd.DataFrame(columns=columns)
    )


def add_auxiliary_items_to_container_data_list(
    container_data: list[ContainerData], scenario: "Scenario"
) -> None:
    """Add GAMS helper items to `container_data` based on data in `scenario`."""
    # Collect some helper data specific to this Scenario
    resource = scenario.set(name="level_resource")
    renewables = scenario.set(name="level_renewable")
    stocks = scenario.set(name="level_stocks")
    resource_grade_map = _compose_resource_grade_map(scenario=scenario)

    helpers = HELPER_INDEXSETS.copy()
    helpers.extend(HELPER_TABLES)

    for item_info in helpers:
        # If filters are to be applied, gather the local helper data
        if item_info.filters:
            # NOTE the locals() are Table data, so always pd.DataFrame, with str data
            # The following are thus mostly no-ops for mypy
            item_info.filters.target = (
                pd.DataFrame(locals().get(item_info.filters.target_name))[
                    item_info.filters.column_name
                ]
                .astype(str)
                .to_list()
            )

        # Construct the records to be added
        # Handle special cases
        if item_info.name == "map_tec_time":
            records = _compose_map_tec_time(
                scenario=scenario, sources=item_info.sources
            )
        elif item_info.name == "map_resource":
            records = _compose_map_resource(
                scenario=scenario,
                sources=item_info.sources,
                filters=item_info.filters,
                resource_grade_map=resource_grade_map,
            )
        else:
            renames = (
                item_info.renames if isinstance(item_info, HelperTableInfo) else None
            )
            records = _compose_records(
                scenario=scenario,
                sources=item_info.sources,
                filters=item_info.filters,
                renames=renames,
            )

        # Add the item to the the list of container data
        container_data.append(
            ContainerData(
                name=item_info.name,
                kind="IndexSet"
                if isinstance(item_info, HelperIndexSetInfo)
                else "Table",
                domain=records.columns.to_list(),
                records=records,
            )
        )
