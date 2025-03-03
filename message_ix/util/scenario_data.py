from dataclasses import dataclass
from typing import Literal, Optional, Union

# List of required indexset names
REQUIRED_INDEXSETS = [
    "year",
    "node",
    "technology",
    "relation",
    "emission",
    "land_scenario",
    "land_type",
    "lvl_spatial",
    "time",
    "lvl_temporal",
    "type_node",
    "type_tec",
    "type_year",
    "type_emission",
    "type_relation",
    "mode",
    "grade",
    "level",
    "commodity",
    "rating",
    "shares",
    "type_addon",
]


@dataclass
class DefaultIndexSetData:
    name: str
    data: list[str]


# List of indexset names and data added to them by default
DEFAULT_INDEXSET_DATA = [
    DefaultIndexSetData(name="node", data=["World"]),
    DefaultIndexSetData(name="lvl_spatial", data=["World", "global"]),
    DefaultIndexSetData(name="type_node", data=["economy"]),
    DefaultIndexSetData(name="time", data=["year"]),
    DefaultIndexSetData(name="lvl_temporal", data=["year"]),
    DefaultIndexSetData(
        name="type_year",
        data=["firstmodelyear", "lastmodelyear", "initializeyear_macro"],
    ),
    DefaultIndexSetData(name="type_tec", data=["all"]),
    DefaultIndexSetData(name="rating", data=["firm", "unrated"]),
    DefaultIndexSetData(name="mode", data=["all"]),
]


@dataclass
class TableInfo:
    name: str
    indexsets: list[str]
    column_names: Optional[list[str]] = None


# List of required table names and indexsets they are linked to, including column_names
# if they differ
# NOTE The list in ixmp_source includes some dimension entries with three items:
# Apparently, (indexset.name, unique_indexset.name, another name?).
# In ixmp4, we only need the real name and unique names if the same indexset is linked
# to multiple columns of the same item. Thus, the list below is constructed ignoring the
# third ixmp_source item.
REQUIRED_TABLES = [
    TableInfo(
        name="map_spatial_hierarchy",
        indexsets=["lvl_spatial", "node", "node"],
        column_names=["lvl_spatial", "node", "node_parent"],
    ),
    TableInfo(
        name="map_node",
        indexsets=["node", "node"],
        column_names=["node_parent", "node"],
    ),
    TableInfo(
        name="map_temporal_hierarchy",
        indexsets=["lvl_temporal", "time", "time"],
        column_names=["lvl_temporal", "time", "time_parent"],
    ),
    TableInfo(
        name="map_time",
        indexsets=["time", "time"],
        column_names=["time_parent", "time"],
    ),
    TableInfo(name="cat_node", indexsets=["type_node", "node"]),
    TableInfo(name="cat_tec", indexsets=["type_tec", "technology"]),
    TableInfo(name="cat_year", indexsets=["type_year", "year"]),
    TableInfo(name="cat_emission", indexsets=["type_emission", "emission"]),
    TableInfo(name="cat_relation", indexsets=["type_relation", "relation"]),
    TableInfo(name="type_tec_land", indexsets=["type_tec"]),
    TableInfo(name="level_resource", indexsets=["level"]),
    TableInfo(name="level_renewable", indexsets=["level"]),
    TableInfo(name="level_stocks", indexsets=["level"]),
    TableInfo(
        name="map_shares_commodity_total",
        indexsets=[
            "shares",
            "node",
            "node",
            "type_tec",
            "mode",
            "commodity",
            "level",
        ],
        column_names=[
            "shares",
            "node_share",
            "node",
            "type_tec",
            "mode",
            "commodity",
            "level",
        ],
    ),
    TableInfo(
        name="map_shares_commodity_share",
        indexsets=[
            "shares",
            "node",
            "node",
            "type_tec",
            "mode",
            "commodity",
            "level",
        ],
        column_names=[
            "shares",
            "node_share",
            "node",
            "type_tec",
            "mode",
            "commodity",
            "level",
        ],
    ),
    TableInfo(name="addon", indexsets=["technology"]),
    TableInfo(
        name="type_addon",
        indexsets=["type_addon", "technology"],
        column_names=["type_addon", "technology_addon"],
    ),
    TableInfo(name="map_tec_addon", indexsets=["technology", "type_addon"]),
    TableInfo(name="balance_equality", indexsets=["commodity", "level"]),
]


@dataclass
class DefaultTableData:
    name: str
    data: dict[str, list[str]]  # based on current usage


# List of table names and data added to them by default
DEFAULT_TABLE_DATA = [
    DefaultTableData(
        name="map_temporal_hierarchy",
        data={
            "lvl_temporal": ["year"],
            "time": ["year"],
            "time_parent": ["year"],
        },
    )
]


# NOTE There are several options in ixmp_source that I don't understand:
# - 2LDB
# - noMode
# - noTimeSeries
# - mode
# - LoUpFx
# - noPar
# - noTs2C
# They are migrated to preserve the information, but I don't know how to handle them
# further.
# Are noMode and mode really flags for whether `mode` is a linked indexset? If so, why
# do we need them? And why do not all parameters have such a flag?

# NOTE ixmp_source also includes additional DB query options for some parameters, where
# I don't immediately know how to translate them, so they're ignored for now.


@dataclass
class ParameterInfo:
    name: str
    gams_name: str  # could default to None  and use name in that case, maybe?
    indexsets: list[str]
    column_names: list[str] | None = None
    write_to_gdx: bool = True
    is_tec: bool = False
    is_tec_act: bool = False
    section: (
        Literal[
            "energyforms:",
            "demand:",
            "resources:",
            "systems:",
            "variables:",
            "relationsX:",
        ]
        | None
    ) = None
    # NOTE changing '2LDB' to 'toLDB'
    toLDB: bool = False
    mode: bool = False
    noMode: bool = False
    noTimeSeries: bool = False
    LoUpFx: bool = False
    noPar: bool = False
    noTs2C: bool = False


# List of all parameter names and indexsets they are linked to, including column_names
# if they differ.
# NOTE this includes a key 'gams_name' because apparently the names in the gams code
# differ. Not yet sure how best to handle this, but we'll likely receive data under the
# names used as keys here and need to ensure it's written to the correct names in the
# gdx.
# NOTE the list in ixmp_source includes parameters with write_to_gdx = False, which are
# not required. We include them here, too, and construct a separate list of required
# parameters below.
PARAMETERS = [
    # NOTE these headings are copied from ixmp_source
    # energyforms (stocks)
    # NOTE this includes an indexset '<value>', not sure how to handle that
    ParameterInfo(
        name="commodity_stock",
        gams_name="commodity_stock",
        indexsets=["node", "commodity", "level", "year"],
        section="energyforms:",
        toLDB=True,
        noMode=True,
        noTimeSeries=True,
    ),
    # demand
    ParameterInfo(
        name="demand",
        gams_name="demand",
        indexsets=["node", "commodity", "level", "year", "time"],
        section="demand:",
        toLDB=True,
        noMode=True,
    ),
    # resources
    # resource cost and remaining resources
    ParameterInfo(
        name="resource_cost",
        gams_name="cost",
        indexsets=["node", "commodity", "grade", "year"],
        section="resources:",
        toLDB=True,
    ),
    ParameterInfo(
        name="resource_remaining",
        gams_name="resrem",
        indexsets=["node", "commodity", "grade", "year"],
        section="resources:",
        toLDB=True,
    ),
    ParameterInfo(
        name="bound_extraction_up",
        gams_name="uplim",
        indexsets=["node", "commodity", "grade", "year"],
        section="resources:",
        toLDB=True,
    ),
    # resource volume and base year extraction
    # NOTE this includes an indexset '<value>', not sure how to handle that
    ParameterInfo(
        name="resource_volume",
        gams_name="volume",
        indexsets=["node", "commodity", "grade"],
        section="resources:",
        toLDB=True,
        noTimeSeries=True,
    ),
    # NOTE this is deactivated for unknown reasons
    # # NOTE this includes an indexset '<value>', not sure how to handle that
    # ParameterInfo(
    #     name="resource_baseyear_extraction",
    #     gams_name="byrex",
    #     indexsets=["node", "commodity", "grade"],
    #     section="resources:",
    #     toLDB=True,
    #     noTimeSeries=True,
    # )
    # systems
    # technical parameters
    ParameterInfo(
        name="technical_lifetime",
        gams_name="pll",
        indexsets=["node", "technology", "year"],
        column_names=["node_loc", "technology", "year_vtg"],
        is_tec=True,
        section="systems:",
        noMode=True,
    ),
    ParameterInfo(
        name="capacity_factor",
        gams_name="plf",
        indexsets=["node", "technology", "year", "year", "time"],
        column_names=["node_loc", "technology", "year_vtg", "year_act", "time"],
        is_tec_act=True,
        section="systems:",
        toLDB=True,
        noMode=True,
    ),
    ParameterInfo(
        name="operation_factor",
        gams_name="optm",
        indexsets=["node", "technology", "year", "year"],
        column_names=["node_loc", "technology", "year_vtg", "year_act"],
        is_tec_act=True,
        section="systems:",
        toLDB=True,
        noMode=True,
    ),
    ParameterInfo(
        name="min_utilization_factor",
        gams_name="minutil",
        indexsets=["node", "technology", "year", "year"],
        column_names=["node_loc", "technology", "year_vtg", "year_act"],
        is_tec_act=True,
        section="systems:",
        toLDB=True,
        noMode=True,
    ),
    # cost parameters
    ParameterInfo(
        name="inv_cost",
        gams_name="inv",
        indexsets=["node", "technology", "year"],
        column_names=["node_loc", "technology", "year_vtg"],
        is_tec=True,
        section="systems:",
        toLDB=True,
        noMode=True,
    ),
    ParameterInfo(
        name="fix_cost",
        gams_name="fom",
        indexsets=["node", "technology", "year", "year"],
        column_names=["node_loc", "technology", "year_vtg", "year_act"],
        is_tec_act=True,
        section="systems:",
        toLDB=True,
        noMode=True,
    ),
    ParameterInfo(
        name="var_cost",
        gams_name="vom",
        indexsets=["node", "technology", "year", "year", "mode", "time"],
        column_names=["node_loc", "technology", "year_vtg", "year_act", "mode", "time"],
        is_tec_act=True,
        section="systems:",
        toLDB=True,
        mode=True,
    ),
    # input, output
    ParameterInfo(
        name="main_output",
        gams_name="moutp",
        indexsets=["node", "technology", "year", "mode", "node", "commodity", "level"],
        column_names=[
            "node_loc",
            "technology",
            "year_act",
            "mode",
            "node_dest",
            "commodity",
            "level",
        ],
        write_to_gdx=False,
        section="systems:",
        toLDB=True,
        mode=True,
    ),
    # NOTE this includes an indexset '<value>', not sure how to handle that
    ParameterInfo(
        name="main_input",
        gams_name="minp",
        indexsets=["node", "technology", "mode", "node", "commodity", "level"],
        column_names=[
            "node_loc",
            "technology",
            "mode",
            "node_dest",
            "commodity",
            "level",
        ],
        write_to_gdx=False,
        section="systems:",
        toLDB=True,
        mode=True,
        noTimeSeries=True,
    ),
    ParameterInfo(
        name="output",
        gams_name="outp",
        indexsets=[
            "node",
            "technology",
            "year",
            "yearmode",
            "node",
            "commodity",
            "level",
            "time",
            "time",
        ],
        column_names=[
            "node_loc",
            "technology",
            "year_vtg",
            "year_act",
            "mode",
            "node_dest",
            "commodity",
            "level",
            "time",
            "time_dest",
        ],
        is_tec_act=True,
        section="systems:",
        toLDB=True,
        mode=True,
    ),
    ParameterInfo(
        name="input",
        gams_name="inp",
        indexsets=[
            "node",
            "technology",
            "year",
            "yearmode",
            "node",
            "commodity",
            "level",
            "time",
            "time",
        ],
        column_names=[
            "node_loc",
            "technology",
            "year_vtg",
            "year_act",
            "mode",
            "node_origin",
            "commodity",
            "level",
            "time",
            "time_origin",
        ],
        is_tec_act=True,
        section="systems:",
        toLDB=True,
        mode=True,
    ),
    # costs for 'soft' relaxation of dynamic new capacity constraints
    ParameterInfo(
        name="abs_cost_new_capacity_soft_up",
        gams_name="abs_cost_new_capacity_soft_up",
        indexsets=["node", "technology", "year"],
        column_names=["node_loc", "technology", "year_vtg"],
        is_tec=True,
    ),
    ParameterInfo(
        name="abs_cost_new_capacity_soft_lo",
        gams_name="abs_cost_new_capacity_soft_lo",
        indexsets=["node", "technology", "year"],
        column_names=["node_loc", "technology", "year_vtg"],
        is_tec=True,
    ),
    ParameterInfo(
        name="level_cost_new_capacity_soft_up",
        gams_name="level_cost_new_capacity_soft_up",
        indexsets=["node", "technology", "year"],
        column_names=["node_loc", "technology", "year_vtg"],
        is_tec=True,
    ),
    ParameterInfo(
        name="level_cost_new_capacity_soft_lo",
        gams_name="level_cost_new_capacity_soft_lo",
        indexsets=["node", "technology", "year"],
        column_names=["node_loc", "technology", "year_vtg"],
        is_tec=True,
    ),
    # costs for 'soft' relaxation of dynamic activity constraints
    ParameterInfo(
        name="abs_cost_activity_soft_up",
        gams_name="abs_cost_activity_soft_up",
        indexsets=["node", "technology", "year", "time"],
        column_names=["node_loc", "technology", "year_act", "time"],
        is_tec=True,
    ),
    ParameterInfo(
        name="abs_cost_activity_soft_lo",
        gams_name="abs_cost_activity_soft_lo",
        indexsets=["node", "technology", "year", "time"],
        column_names=["node_loc", "technology", "year_act", "time"],
        is_tec=True,
    ),
    ParameterInfo(
        name="level_cost_activity_soft_up",
        gams_name="level_cost_activity_soft_up",
        indexsets=["node", "technology", "year", "time"],
        column_names=["node_loc", "technology", "year_act", "time"],
        is_tec=True,
    ),
    ParameterInfo(
        name="level_cost_activity_soft_lo",
        gams_name="level_cost_activity_soft_lo",
        indexsets=["node", "technology", "year", "time"],
        column_names=["node_loc", "technology", "year_act", "time"],
        is_tec=True,
    ),
    # bounds on activity and new capacity (old MESSAGE formulation)
    # NOTE from ixmp_source: TODO: only included for legacy reasons of MESSAGE V -
    # marked for deletion
    # So should we delete this now?
    # Otherwise: does '*' work as intended?
    ParameterInfo(
        name="bounds_new_capacity",
        gams_name="bdc",
        indexsets=["node", "technology", "year", "*"],
        column_names=["node", "technology", "year", "dir"],
        write_to_gdx=False,
        is_tec=True,
        section="systems:",
        toLDB=True,
        noMode=True,
        LoUpFx=True,
    ),
    # NOTE from ixmp_source: TODO: only included for legacy reasons of MESSAGE V -
    # marked for deletion
    # So should we delete this now?
    # Otherwise: does '*' work as intended?
    ParameterInfo(
        name="bounds_total_capacity",
        gams_name="bdi",
        indexsets=["node", "technology", "year", "*"],
        column_names=["node", "technology", "year", "dir"],
        write_to_gdx=False,
        is_tec=True,
        section="systems:",
        toLDB=True,
        LoUpFx=True,
    ),
    # Otherwise: does '*' work as intended?
    ParameterInfo(
        name="bounds_activity",
        gams_name="bda",
        indexsets=["node", "technology", "year", "mode", "*"],
        column_names=["node", "technology", "year", "mode", "dir"],
        write_to_gdx=False,
        is_tec=True,
        section="systems:",
        toLDB=True,
        LoUpFx=True,
    ),
    # new formulation for upper and lower bounds (new GAMS-MESSAGE formulation)
    ParameterInfo(
        name="bound_new_capacity_up",
        gams_name="bound_new_capacity_up",
        indexsets=["node", "technology", "year"],
        column_names=["node_loc", "technology", "year_vtg"],
        is_tec=True,
    ),
    ParameterInfo(
        name="bound_new_capacity_lo",
        gams_name="bound_new_capacity_lo",
        indexsets=["node", "technology", "year"],
        column_names=["node_loc", "technology", "year_vtg"],
        is_tec=True,
    ),
    ParameterInfo(
        name="bound_total_capacity_up",
        gams_name="bound_total_capacity_up",
        indexsets=["node", "technology", "year"],
        column_names=["node_loc", "technology", "year_act"],
        is_tec=True,
    ),
    ParameterInfo(
        name="bound_total_capacity_lo",
        gams_name="bound_total_capacity_lo",
        indexsets=["node", "technology", "year"],
        column_names=["node_loc", "technology", "year_act"],
        is_tec=True,
    ),
    ParameterInfo(
        name="bound_activity_up",
        gams_name="bound_activity_up",
        indexsets=["node", "technology", "year", "mode", "time"],
        column_names=["node_loc", "technology", "year_act", "mode", "time"],
        is_tec=True,
    ),
    ParameterInfo(
        name="bound_activity_lo",
        gams_name="bound_activity_lo",
        indexsets=["node", "technology", "year", "mode", "time"],
        column_names=["node_loc", "technology", "year_act", "mode", "time"],
        is_tec=True,
    ),
    # bounds on market penetration of new capacity (old MESSAGE formulation)
    # TODO Does '*' work as intended?
    ParameterInfo(
        name="market_penetration_new_capacity",
        gams_name="mpc",
        indexsets=["node", "technology", "year", "*", "*", "time"],
        column_names=["node", "technology", "year", "dir", "item", "time"],
        write_to_gdx=False,
        section="systems:",
        toLDB=True,
        noMode=True,
        LoUpFx=True,
    ),
    # TODO Does '*' work as intended?
    ParameterInfo(
        name="market_penetration_activity",
        gams_name="mpc",
        indexsets=["node", "technology", "year", "mode", "*", "*"],
        column_names=["node", "technology", "year", "mode", "dir", "item"],
        write_to_gdx=False,
        section="systems:",
        toLDB=True,
        LoUpFx=True,
    ),
    # technological learning and spillover effects across technologies/regions
    # (new GAMS-MESSAGE formulation)
    # NOTE deactivated for unknown reasons
    # ParameterInfo(
    #     name="diffusion_factor",
    #     gams_name="diffusion_factor",
    #     indexsets=["node", "technology", "year", "node", "technology", "year"],
    #     column_names=[
    #         "node_loc",
    #         "technology",
    #         "year_act",
    #         "node_origin",
    #         "technology_origin",
    #         "year_origin",
    #     ],
    #     is_tec=True,
    # ),
    ParameterInfo(
        name="initial_new_capacity_up",
        gams_name="initial_new_capacity_up",
        indexsets=["node", "technology", "year"],
        column_names=["node_loc", "technology", "year_vtg"],
        is_tec=True,
    ),
    ParameterInfo(
        name="growth_new_capacity_up",
        gams_name="growth_new_capacity_up",
        indexsets=["node", "technology", "year"],
        column_names=["node_loc", "technology", "year_vtg"],
        is_tec=True,
    ),
    ParameterInfo(
        name="soft_new_capacity_up",
        gams_name="soft_new_capacity_up",
        indexsets=["node", "technology", "year"],
        column_names=["node_loc", "technology", "year_vtg"],
        is_tec=True,
    ),
    ParameterInfo(
        name="initial_new_capacity_lo",
        gams_name="initial_new_capacity_lo",
        indexsets=["node", "technology", "year"],
        column_names=["node_loc", "technology", "year_vtg"],
        is_tec=True,
    ),
    ParameterInfo(
        name="growth_new_capacity_lo",
        gams_name="growth_new_capacity_lo",
        indexsets=["node", "technology", "year"],
        column_names=["node_loc", "technology", "year_vtg"],
        is_tec=True,
    ),
    ParameterInfo(
        name="soft_new_capacity_lo",
        gams_name="soft_new_capacity_lo",
        indexsets=["node", "technology", "year"],
        column_names=["node_loc", "technology", "year_vtg"],
        is_tec=True,
    ),
    ParameterInfo(
        name="initial_activity_up",
        gams_name="initial_activity_up",
        indexsets=["node", "technology", "year", "time"],
        column_names=["node_loc", "technology", "year_act", "time"],
        is_tec=True,
    ),
    ParameterInfo(
        name="growth_activity_up",
        gams_name="growth_activity_up",
        indexsets=["node", "technology", "year", "time"],
        column_names=["node_loc", "technology", "year_act", "time"],
        is_tec=True,
    ),
    ParameterInfo(
        name="soft_activity_up",
        gams_name="soft_activity_up",
        indexsets=["node", "technology", "year", "time"],
        column_names=["node_loc", "technology", "year_act", "time"],
        is_tec=True,
    ),
    ParameterInfo(
        name="initial_activity_lo",
        gams_name="initial_activity_lo",
        indexsets=["node", "technology", "year", "time"],
        column_names=["node_loc", "technology", "year_act", "time"],
        is_tec=True,
    ),
    ParameterInfo(
        name="growth_activity_lo",
        gams_name="growth_activity_lo",
        indexsets=["node", "technology", "year", "time"],
        column_names=["node_loc", "technology", "year_act", "time"],
        is_tec=True,
    ),
    ParameterInfo(
        name="soft_activity_lo",
        gams_name="soft_activity_lo",
        indexsets=["node", "technology", "year", "time"],
        column_names=["node_loc", "technology", "year_act", "time"],
        is_tec=True,
    ),
    # emission intensity factor
    ParameterInfo(
        name="emission_factor",
        gams_name="emission_factor",
        indexsets=["node", "technology", "year", "year", "mode", "emission"],
        column_names=[
            "node_loc",
            "technology",
            "year_vtg",
            "year_act",
            "mode",
            "emission",
        ],
        is_tec=True,
    ),
    # construction time
    ParameterInfo(
        name="construction_time",
        gams_name="ctime",
        indexsets=["node", "technology", "year"],
        column_names=["node_loc", "technology", "year_vtg"],
        is_tec=True,
        section="systems:",
        toLDB=True,
        noMode=True,
    ),
    # power relations, initial cores, final cores
    # NOTE all of these are deactivated for unknown reasons
    # ParameterInfo(
    #     name="power_relation",
    #     gams_name="prel",
    #     indexsets=["node", "technology", "year", "mode", "time"],
    #     column_names=["node_loc", "technology", "year_act", "mode", "time"],
    #     is_tec=True,
    #     section="systems:",
    #     toLDB=True,
    #     mode=True,
    # ),
    # # NOTE the setup for this is partly missing from ixmp_source
    # ParameterInfo(
    #     name="initial_cores",
    #     gams_name="corein",
    #     is_tec=True,
    #     section="systems:",
    #     toLDB=True,
    #     noMode=True,
    # ),
    # # NOTE the setup for this is partly missing from ixmp_source
    # ParameterInfo(
    #     name="final_cores",
    #     gams_name="coreout",
    #     is_tec=True,
    #     section="systems:",
    #     toLDB=True,
    #     noMode=True,
    # ),
    # constraints on activity, including the lag (a
    ParameterInfo(
        name="con1a",
        gams_name="con1a",
        indexsets=["node", "technology", "year", "mode", "*"],
        column_names=["node", "technology", "year", "mode", "relation"],
        write_to_gdx=False,
        section="systems:",
        toLDB=True,
    ),
    ParameterInfo(
        name="con2a",
        gams_name="con2a",
        indexsets=["node", "technology", "year", "mode", "*"],
        column_names=["node", "technology", "year", "mode", "relation"],
        write_to_gdx=False,
        section="systems:",
        toLDB=True,
    ),
    # # NOTE deactivated for unknown reasons
    # # NOTE the setup for this is partly missing from ixmp_source
    # ParameterInfo(
    #     name="conca", gams_name="conca", is_tec=True, section="systems:", toLDB=True, noMode=True # noqa: E501
    # ),
    # note that the investment-related con1c entries are already collected individually
    # (using mappings)
    ParameterInfo(
        name="con1c",
        gams_name="con1c",
        indexsets=["node", "technology", "year", "*"],
        column_names=["node", "technology", "year", "relation"],
        write_to_gdx=False,
        section="systems:",
        toLDB=True,
        noMode=True,
    ),
    ParameterInfo(
        name="con2c",
        gams_name="con2c",
        indexsets=["node", "technology", "year", "*"],
        column_names=["node", "technology", "year", "relation"],
        write_to_gdx=False,
        section="systems:",
        toLDB=True,
        noMode=True,
    ),
    # pseudotechnology (what is called variables in Message)
    # NOTE from ixmp_source: TODO: only included for legacy reasons of MESSAGE V -
    # marked for deletion
    ParameterInfo(
        name="cost_pseudotec",
        gams_name="cost",
        indexsets=["node", "pseudotechnology", "year"],
        write_to_gdx=False,
        section="variables:",
        toLDB=True,
        noMode=True,
    ),
    # upper, lower
    # TODO (@danielhuppmann, 26/11/2015): integrate this with activity bounds in systems
    # NOTE from ixmp_source: TODO: only included for legacy reasons of MESSAGE V -
    # marked for deletion
    ParameterInfo(
        name="upper_bound",
        gams_name="upper_bound",
        indexsets=["node", "pseudotechnology", "year"],
        write_to_gdx=False,
        section="variables:",
        toLDB=True,
        noMode=True,
    ),
    ParameterInfo(
        name="lower_bound",
        gams_name="lower_bound",
        indexsets=["node", "pseudotechnology", "year"],
        write_to_gdx=False,
        section="variables:",
        toLDB=True,
        noMode=True,
    ),
    # constraints on activity
    # TODO (@danielhuppmann, 26/11/2015): integrate this with con1a/con2a in systems
    ParameterInfo(
        name="con1a_pseudotec",
        gams_name="con1a",
        indexsets=["node", "pseudotechnology", "year", "*"],
        column_names=["node", "pseudotechnology", "year", "relation"],
        write_to_gdx=False,
        section="variables:",
        toLDB=True,
        noMode=True,
    ),
    ParameterInfo(
        name="con2a_pseudotec",
        gams_name="con2a",
        indexsets=["node", "pseudotechnology", "year", "*"],
        column_names=["node", "pseudotechnology", "year", "relation"],
        write_to_gdx=False,
        section="variables:",
        toLDB=True,
        noMode=True,
    ),
    # renewables representation
    ParameterInfo(
        name="renewable_potential",
        gams_name="renewable_potential",
        indexsets=["node", "commodity", "grade", "level", "year"],
    ),
    ParameterInfo(
        name="renewable_capacity_factor",
        gams_name="renewable_capacity_factor",
        indexsets=["node", "commodity", "grade", "level", "year"],
    ),
    ParameterInfo(
        name="reliability_factor",
        gams_name="reliability_factor",
        indexsets=[
            "node",
            "technology",
            "year",
            "commodity",
            "level",
            "time",
            "rating",
        ],
        column_names=[
            "node",
            "technology",
            "year_act",
            "commodity",
            "level",
            "time",
            "rating",
        ],
        is_tec=True,
    ),
    ParameterInfo(
        name="peak_load_factor",
        gams_name="peak_load_factor",
        indexsets=["node", "commodity", "level", "year", "time"],
    ),
    ParameterInfo(
        name="flexibility_factor",
        gams_name="flexibility_factor",
        indexsets=[
            "node",
            "technology",
            "year",
            "year",
            "node",
            "commodity",
            "level",
            "time",
            "rating",
        ],
        column_names=[
            "node_loc",
            "technology",
            "year_vtg",
            "year_act",
            "node",
            "commodity",
            "level",
            "time",
            "rating",
        ],
    ),
    ParameterInfo(
        name="rating_bin",
        gams_name="rating_bin",
        indexsets=[
            "node",
            "technology",
            "year",
            "commodity",
            "level",
            "time",
            "rating",
        ],
        column_names=[
            "node",
            "technology",
            "year_act",
            "commodity",
            "level",
            "time",
            "rating",
        ],
        is_tec=True,
    ),
    # relations (relations1, relations2, relationsc)
    # right-hand side
    ParameterInfo(
        name="righthandside",
        gams_name="rhs",
        indexsets=["node", "*", "year", "*"],
        column_names=["node", "relation_name", "year", "dir"],
        write_to_gdx=False,
        section="relationsX:",
        toLDB=True,
        noMode=True,
        noPar=True,
        noTs2C=True,
    ),
    # right-hand side (if both upper and lower bounds exists)
    ParameterInfo(
        name="range",
        gams_name="rng",
        indexsets=["node", "*", "year"],
        column_names=["node", "relation_name", "year"],
        write_to_gdx=False,
        section="relationsX:",
        toLDB=True,
        noMode=True,
        noPar=True,
        noTs2C=True,
    ),
    # initial value
    # NOTE deactivated for unknown reasons
    # ParameterInfo(
    #     name="initial_value",
    #     gams_name="initval",
    #     indexsets=["node", "*", "year"],
    #     column_names=["node", "relation_name", "year"],
    #     section="relationsX:",
    #     noMode=True,
    # ),
    # availability (plant load factor) - it is not clear whether we really need this at
    # all
    # NOTE deactivated for unknown reasons
    # ParameterInfo(
    #     name="availability",
    #     gams_name="plf",
    #     indexsets=["node", "*", "year"],
    #     column_names=["node", "relation_name", "year"],
    #     section="relationsX:",
    #     noMode=True,
    # ),
    # cost of relations
    # NOTE same gams_name as one above, maybe unique iif combined with section?
    ParameterInfo(
        name="cost",
        gams_name="cost",
        indexsets=["node", "*", "year"],
        column_names=["node", "relation_name", "year"],
        write_to_gdx=False,
        section="relationsX:",
        toLDB=True,
        noMode=True,
    ),
    # taxes and subsidies
    ParameterInfo(
        name="tax",
        gams_name="tax",
        indexsets=["node", "type_tec", "year"],
        column_names=["node_loc", "type_tec", "year_act"],
    ),
    ParameterInfo(
        name="subsidy",
        gams_name="subsidy",
        indexsets=["node", "type_tec", "year"],
        column_names=["node_loc", "type_tec", "year_act"],
    ),
    # emission
    ParameterInfo(
        name="historical_emission",
        gams_name="historical_emission",
        indexsets=["node", "type_emission", "type_tec", "type_year"],
    ),
    ParameterInfo(
        name="emission_scaling",
        gams_name="emission_scaling",
        indexsets=["type_emission", "emission"],
    ),
    ParameterInfo(
        name="bound_emission",
        gams_name="bound_emission",
        indexsets=["node", "type_emission", "type_tec", "type_year"],
    ),
    ParameterInfo(
        name="tax_emission",
        gams_name="tax_emission",
        indexsets=["node", "type_emission", "type_tec", "type_year"],
    ),
    # land-use emulator
    ParameterInfo(
        name="land_cost",
        gams_name="land_cost",
        indexsets=["node", "land_scenario", "year"],
    ),
    ParameterInfo(
        name="land_input",
        gams_name="land_input",
        indexsets=["node", "land_scenario", "year", "commodity", "level", "time"],
    ),
    ParameterInfo(
        name="land_output",
        gams_name="land_output",
        indexsets=["node", "land_scenario", "year", "commodity", "level", "time"],
    ),
    ParameterInfo(
        name="land_use",
        gams_name="land_use",
        indexsets=["node", "land_scenario", "year", "land_type"],
    ),
    ParameterInfo(
        name="land_emission",
        gams_name="land_emission",
        indexsets=["node", "land_scenario", "year", "emission"],
    ),
    ParameterInfo(
        name="initial_land_scen_up",
        gams_name="initial_land_scen_up",
        indexsets=["node", "land_scenario", "year"],
    ),
    ParameterInfo(
        name="growth_land_scen_up",
        gams_name="growth_land_scen_up",
        indexsets=["node", "land_scenario", "year"],
    ),
    ParameterInfo(
        name="initial_land_scen_lo",
        gams_name="initial_land_scen_lo",
        indexsets=["node", "land_scenario", "year"],
    ),
    ParameterInfo(
        name="growth_land_scen_lo",
        gams_name="growth_land_scen_lo",
        indexsets=["node", "land_scenario", "year"],
    ),
    ParameterInfo(
        name="initial_land_up",
        gams_name="initial_land_up",
        indexsets=["node", "year", "land_type"],
    ),
    ParameterInfo(
        name="initial_land_lo",
        gams_name="initial_land_lo",
        indexsets=["node", "year", "land_type"],
    ),
    ParameterInfo(
        name="growth_land_up",
        gams_name="growth_land_up",
        indexsets=["node", "year", "land_type"],
    ),
    ParameterInfo(
        name="growth_land_lo",
        gams_name="growth_land_lo",
        indexsets=["node", "year", "land_type"],
    ),
    ParameterInfo(
        name="dynamic_land_up",
        gams_name="dynamic_land_up",
        indexsets=["node", "land_scenario", "year", "land_type"],
    ),
    ParameterInfo(
        name="dynamic_land_lo",
        gams_name="dynamic_land_lo",
        indexsets=["node", "land_scenario", "year", "land_type"],
    ),
    # generic relations (included as legacy from MESSAGE V)
    ParameterInfo(
        name="relation_upper",
        gams_name="relation_upper",
        indexsets=["relation", "node", "year"],
        column_names=["relation", "node_rel", "year_rel"],
    ),
    ParameterInfo(
        name="relation_lower",
        gams_name="relation_lower",
        indexsets=["relation", "node", "year"],
        column_names=["relation", "node_rel", "year_rel"],
    ),
    ParameterInfo(
        name="relation_cost",
        gams_name="relation_cost",
        indexsets=["relation", "node", "year"],
        column_names=["relation", "node_rel", "year_rel"],
    ),
    ParameterInfo(
        name="relation_new_capacity",
        gams_name="relation_new_capacity",
        indexsets=["relation", "node", "year", "technology"],
        column_names=["relation", "node_rel", "year_rel", "technology"],
        is_tec=True,
    ),
    ParameterInfo(
        name="relation_total_capacity",
        gams_name="relation_total_capacity",
        indexsets=["relation", "node", "year", "technology"],
        column_names=["relation", "node_rel", "year_rel", "technology"],
        is_tec=True,
    ),
    ParameterInfo(
        name="relation_activity",
        gams_name="relation_activity",
        indexsets=[
            "relation",
            "node",
            "year",
            "node",
            "technology",
            "year",
            "mode",
        ],
        column_names=[
            "relation",
            "node_rel",
            "year_rel",
            "node_loc",
            "technology",
            "year_act",
            "mode",
        ],
        is_tec=True,
    ),
    # auxiliary parameters
    ParameterInfo(
        name="duration_period", gams_name="duration_period", indexsets=["year"]
    ),
    ParameterInfo(name="duration_time", gams_name="duration_time", indexsets=["time"]),
    ParameterInfo(name="interestrate", gams_name="interestrate", indexsets=["year"]),
    # historical and reference values
    # new capacity installed before the start of the model horizon
    ParameterInfo(
        name="historical_extraction",
        gams_name="historical_extraction",
        indexsets=["node", "commodity", "grade", "year"],
    ),
    ParameterInfo(
        name="historical_new_capacity",
        gams_name="historical_new_capacity",
        indexsets=["node", "technology", "year"],
        column_names=["node_loc", "technology", "year_vtg"],
    ),
    ParameterInfo(
        name="historical_activity",
        gams_name="historical_activity",
        indexsets=["node", "technology", "year", "mode", "time"],
        column_names=["node_loc", "technology", "year_act", "mode", "time"],
    ),
    ParameterInfo(
        name="historical_land",
        gams_name="historical_land",
        indexsets=["node", "land_scenario", "year"],
    ),
    # reference extraction, investment, activity and relation level
    ParameterInfo(
        name="ref_extraction",
        gams_name="ref_extraction",
        indexsets=["node", "commodity", "grade", "year"],
    ),
    ParameterInfo(
        name="ref_new_capacity",
        gams_name="ref_new_capacity",
        indexsets=["node", "technology", "year"],
        column_names=["node_loc", "technology", "year_vtg"],
    ),
    ParameterInfo(
        name="ref_activity",
        gams_name="ref_activity",
        indexsets=["node", "technology", "year", "mode", "time"],
        column_names=["node_loc", "technology", "year_act", "mode", "time"],
    ),
    ParameterInfo(
        name="ref_relation",
        gams_name="ref_relation",
        indexsets=["relation", "node", "year"],
        column_names=["relation", "node_rel", "year_rel"],
    ),
    # fixed decision variable values (for 'slicing', i.e., fixing of decision variables)
    ParameterInfo(
        name="fixed_extraction",
        gams_name="fixed_extraction",
        indexsets=["node", "commodity", "grade", "year"],
    ),
    ParameterInfo(
        name="fixed_stock",
        gams_name="fixed_stock",
        indexsets=["node", "commodity", "level", "year"],
    ),
    ParameterInfo(
        name="fixed_new_capacity",
        gams_name="fixed_new_capacity",
        indexsets=["node", "technology", "year"],
        column_names=["node_loc", "technology", "year_vtg"],
    ),
    ParameterInfo(
        name="fixed_capacity",
        gams_name="fixed_capacity",
        indexsets=["node", "technology", "year", "year"],
        column_names=["node_loc", "technology", "year_vtg", "year_act"],
    ),
    ParameterInfo(
        name="fixed_activity",
        gams_name="fixed_activity",
        indexsets=["node", "technology", "year", "year", "mode", "time"],
        column_names=["node_loc", "technology", "year_vtg", "year_act", "mode", "time"],
    ),
    ParameterInfo(
        name="fixed_land",
        gams_name="fixed_land",
        indexsets=["node", "land_scenario", "year"],
    ),
    # parameters for MACRO
    ParameterInfo(
        name="historical_gdp", gams_name="historical_gdp", indexsets=["node", "year"]
    ),
    # parameters for share constraints
    ParameterInfo(
        name="share_commodity_up",
        gams_name="share_commodity_up",
        indexsets=["shares", "node", "year", "time"],
        column_names=["shares", "node_share", "year_act", "time"],
    ),
    ParameterInfo(
        name="share_commodity_lo",
        gams_name="share_commodity_lo",
        indexsets=["shares", "node", "year", "time"],
        column_names=["shares", "node_share", "year_act", "time"],
    ),
    ParameterInfo(
        name="share_mode_up",
        gams_name="share_mode_up",
        indexsets=["shares", "node", "technology", "mode", "year", "time"],
        column_names=["shares", "node_share", "technology", "mode", "year_act", "time"],
    ),
    ParameterInfo(
        name="share_mode_lo",
        gams_name="share_mode_lo",
        indexsets=["shares", "node", "technology", "mode", "year", "time"],
        column_names=["shares", "node_share", "technology", "mode", "year_act", "time"],
    ),
    # parameters for addon formulation
    ParameterInfo(
        name="addon_conversion",
        gams_name="addon_conversion",
        indexsets=["node", "technology", "year", "year", "mode", "time", "type_addon"],
        column_names=[
            "node",
            "technology",
            "year_vtg",
            "year_act",
            "mode",
            "time",
            "type_addon",
        ],
    ),
    ParameterInfo(
        name="addon_up",
        gams_name="addon_up",
        indexsets=["node", "technology", "year", "mode", "time", "type_addon"],
        column_names=["node", "technology", "year_act", "mode", "time", "type_addon"],
    ),
    ParameterInfo(
        name="addon_lo",
        gams_name="addon_lo",
        indexsets=["node", "technology", "year", "mode", "time", "type_addon"],
        column_names=[
            "node",
            "technology",
            "year_act",
            "mode",
            "time",
            "type_addon",
        ],
    ),
]

# List of required parameters
REQUIRED_PARAMETERS = [parameter for parameter in PARAMETERS if parameter.write_to_gdx]


@dataclass
class DefaultParameterData:
    name: str
    data: dict[str, Union[list[int], list[str]]]  # based on current usage


DEFAULT_PARAMETER_DATA = [
    DefaultParameterData(
        name="duration_time", data={"time": ["year"], "values": [1], "units": ["%"]}
    )
]


@dataclass
class VariableInfo:
    name: str
    gams_name: str
    indexsets: Optional[list[str]] = None
    column_names: Optional[list[str]] = None


# List of required variable names and indexsets they are linked to, including
# column_names if they differ
# NOTE this includes a key 'gams_name' because apparently the names in the gams code
# differ. Not yet sure how best to handle this, but we'll likely receive data under the
# names used as keys here and need to ensure it's written to the correct names in the
# gdx.
REQUIRED_VARIABLES = [
    # TODO Only leaving these here if I want plain dicts after all
    # {"objective": {"gams_name": "OBJ", "indexsets": None, "column_names": None}},
    # {
    #     "extraction": {
    #         "gams_name": "EXT",
    #         "indexsets": ["node", "commodity", "grade", "year"],
    #         "column_names": None,
    #     }
    # },
    # {
    #     "stock": {
    #         "gams_name": "STOCK",
    #         "indexsets": ["node", "commodity", "level", "year"],
    #         "column_names": None,
    #     }
    # },
    # {
    #     "new capacity",
    #     {
    #         "gams_name": "CAP_NEW",
    #         "indexsets": ["node", "technology", "year"],
    #         "column_names": ["node_loc", "technology", "year_vtg"],
    #     },
    # },
    # {
    #     "maintained capacity",
    #     {
    #         "gams_name": "CAP",
    #         "indexsets": ["node", "technology", "year", "year"],
    #         "column_names": ["node_loc", "technology", "year_vtg", "year_act"],
    #     },
    # },
    # {
    #     "activity": {
    #         "gams_name": "ACT",
    #         "indexsets": ["node", "technology", "year", "year", "mode", "time"],
    #         "column_names": [
    #             "node_loc",
    #             "technology",
    #             "year_vtg",
    #             "year_act",
    #             "mode",
    #             "time",
    #         ],
    #     }
    # },
    # {
    #     "emissions": {
    #         "gams_name": "EMISS",
    #         "indexsets": ["node", "emission", "type_tec", "year"],
    #         "column_names": None,
    #     }
    # },
    # {
    #     "land scenario share": {
    #         "gams_name": "LAND",
    #         "indexsets": ["node", "land_scenario", "year"],
    #         "column_names": None,
    #     }
    # },
    VariableInfo(name="objective", gams_name="OBJ"),
    VariableInfo(
        name="extraction",
        gams_name="EXT",
        indexsets=["node", "commodity", "grade", "year"],
        column_names=None,
    ),
    VariableInfo(
        name="stock",
        gams_name="STOCK",
        indexsets=["node", "commodity", "level", "year"],
        column_names=None,
    ),
    VariableInfo(
        name="new capacity",
        gams_name="CAP_NEW",
        indexsets=["node", "technology", "year"],
        column_names=["node_loc", "technology", "year_vtg"],
    ),
    VariableInfo(
        name="maintained capacity",
        gams_name="CAP",
        indexsets=["node", "technology", "year", "year"],
        column_names=["node_loc", "technology", "year_vtg", "year_act"],
    ),
    VariableInfo(
        name="activity",
        gams_name="ACT",
        indexsets=["node", "technology", "year", "year", "mode", "time"],
        column_names=["node_loc", "technology", "year_vtg", "year_act", "mode", "time"],
    ),
    VariableInfo(
        name="emissions",
        gams_name="EMISS",
        indexsets=["node", "emission", "type_tec", "year"],
        column_names=None,
    ),
    VariableInfo(
        name="land scenario share",
        gams_name="LAND",
        indexsets=["node", "land_scenario", "year"],
        column_names=None,
    ),
    VariableInfo(
        name="relation (lhs)",
        gams_name="REL",
        indexsets=["relation", "node", "year"],
        column_names=["relation", "node_rel", "year_rel"],
    ),
    # variables for MACRO (partly also used for MESSAGE reporting)
    VariableInfo(
        name="demand (at solution)",
        gams_name="DEMAND",
        indexsets=["node", "commodity", "level", "year", "time"],
        column_names=None,
    ),
    VariableInfo(
        name="commodity price (at solution)",
        gams_name="PRICE_COMMODITY",
        indexsets=["node", "commodity", "level", "year", "time"],
        column_names=None,
    ),
    VariableInfo(
        name="emission price",
        gams_name="PRICE_EMISSION",
        indexsets=["node", "type_emission", "type_tec", "year"],
        column_names=None,
    ),
    VariableInfo(
        name="cost by node and year",
        gams_name="COST_NODAL",
        indexsets=["node", "year"],
        column_names=None,
    ),
    VariableInfo(
        name="cost net of trade and emission costs",
        gams_name="COST_NODAL_NET",
        indexsets=["node", "year"],
        column_names=None,
    ),
    VariableInfo(
        name="gross domestic product (MACRO)",
        gams_name="GDP",
        indexsets=["node", "year"],
        column_names=None,
    ),
    VariableInfo(
        name="total investment (MACRO)",
        gams_name="I",
        indexsets=["node", "year"],
        column_names=None,
    ),
    VariableInfo(
        name="total consumption (MACRO)",
        gams_name="C",
        indexsets=["node", "year"],
        column_names=None,
    ),
]


# NOTE identical to VariableInfo
EquationInfo = VariableInfo

# List of required equation names and indexsets they are linked to, including
# column_names if they differ
# NOTE this includes a key 'gams_name' because apparently the names in the gams code
# differ. Not yet sure how best to handle this, but we'll likely receive data under the
# names used as keys here and need to ensure it's written to the correct names in the
# gdx.
REQUIRED_EQUATIONS = [
    EquationInfo(
        name="commodity balance",
        gams_name="RESOURCE_HORIZON",
        indexsets=["node", "commodity", "grade"],
    ),
    # NOTE The following two were uncommented in ixmp_source for an unknown reason
    # in preparation of MESSAGEix release 1.2
    # EquationInfo(
    #     name="relation upper bound",
    #     gams_name="RELATION_CONSTRAINT_UP",
    #     indexsets=["relation", "node", "year"],
    #     column_names=["relation", "node_rel", "year_rel"],
    # ),
    # EquationInfo(
    #     name="relation_lower_bound",
    #     gams_name="RELATION_CONSTRAINT_LO",
    #     indexsets=["relation", "node", "year"],
    #     column_names=["relation", "node_rel", "year_rel"],
    # ),
]
