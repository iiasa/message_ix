# -*- coding: utf-8 -*-
"""
Created on Mon Mar 20 15:41:32 2023

@author: pratama
"""

import os

import numpy as np
import pandas as pd
import yaml

from message_ix.models import MESSAGE_ITEMS
from message_ix.utils import make_df


def generate_df(
    scenario,
    filepath="",
):
    if not filepath:
        module_path = os.path.abspath(__file__)  # get the module path
        package_path = os.path.dirname(
            os.path.dirname(module_path)
        )  # get the package path
        path = os.path.join(
            package_path, "add_dac/tech_data.yaml"
        )  # join the current working directory with a filename
        with open(path, "r") as stream:
            tech_data = yaml.safe_load(stream)
    else:
        with open(filepath, "r") as stream:
            tech_data = yaml.safe_load(stream)

    # Set up dictionary of parameter indices list
    par_idx = {}
    data = {}

    # Create dicitonary of parameter indices and data
    for tech in set(tech_data):
        # add vintage and active years and update tech_data for each tech
        years_vtg_act = scenario.vintage_and_active_years()
        years_vtg_act = years_vtg_act[
            years_vtg_act["year_vtg"] >= tech_data[tech]["year_init"]
        ]
        tech_data[tech]["year_vtg"] = years_vtg_act["year_vtg"].to_list()
        tech_data[tech]["year_act"] = years_vtg_act["year_act"].to_list()

        # collect parameter indices and update data
        par_idx.update(
            {
                tech: {
                    name: {
                        idx: []
                        for idx in list(
                            MESSAGE_ITEMS[tech_data[tech][name]["par_name"]].get(
                                "idx_names"
                            )
                        )
                    }
                    for name in set(tech_data[tech])
                    - set(["year_init", "year_vtg", "year_act"])
                }
            }
        )

        data.update({tech: {name: [] for name in list(par_idx[tech].keys())}})

    # If those are not provided, then this block of code is needed to retrieve them from the data input
    regions = []
    emissions = []
    times = []
    modes = []
    commodities = []
    levels = []
    relations = []

    set_elements_dict = {
        "node_loc": {"data": regions, "name": "node"},
        "emission": {"data": emissions, "name": "emission"},
        "mode": {"data": modes, "name": "mode"},
        "time": {"data": times, "name": "time"},
        "commodity": {"data": commodities, "name": "commodity"},
        "level": {"data": levels, "name": "level"},
        "time_origin": {"data": times, "name": "time"},
        "time_dest": {"data": times, "name": "time"},
        "relation": {"data": relations, "name": "relation"},
        "node_rel": {"data": regions, "name": "node"},
    }

    # Create DataFrame for all parameters
    for tec, val in data.items():
        for name in val.keys():
            # tec = 'DACCS'
            # name = 'emission_factor_co2'

            kwargs = {}
            if all(idx in par_idx[tec][name] for idx in ["year_vtg", "year_act"]):
                kwargs = {
                    "year_vtg": tech_data[tec]["year_vtg"],
                    "year_act": tech_data[tec]["year_act"],
                }
            elif "year_vtg" in par_idx[tec][name]:
                kwargs = {"year_vtg": sorted(set(tech_data[tec]["year_vtg"]))}
            else:
                kwargs = {"year_act": sorted(set(tech_data[tec]["year_act"]))}
                # if 'year_rel' is present, the values are assumed from 'year_act' values
                if "year_rel" in par_idx[tec][name]:
                    kwargs.update({"year_rel": sorted(set(tech_data[tec]["year_act"]))})

            df = make_df(
                tech_data[tec][name]["par_name"],
                technology=tec,
                value=tech_data[tec][name]["value"],
                unit=tech_data[tec][name]["unit"],
                **kwargs,
            )

            # create empty dataframe
            idx_exp = [
                e
                for e in par_idx[tec][name]
                if e
                not in [
                    "technology",
                    "year_vtg",
                    "year_act",
                    "year_rel",
                    "node_origin",
                    "node_dest",
                    "time_origin",
                    "time_dest",
                ]
            ]

            for idx in idx_exp:
                default = (
                    {
                        e: 1
                        for e in list(scenario.set(set_elements_dict[idx]["name"]))[1:]
                    }
                    if idx in ["node_loc", "mode"]
                    else {
                        e: 1 for e in list(scenario.set(set_elements_dict[idx]["name"]))
                    }
                )

                listidx = list(tech_data[tec][name].get(idx, default))
                listdfidx = []
                for e in listidx:
                    df1 = df.copy()
                    df1[idx] = [e] * len(df)
                    listdfidx.append(df1)
                df = pd.concat(listdfidx, ignore_index=True)

            # assigning values for node and time related indices
            for idx in df.columns:
                if idx in ["node_origin", "node_dest"]:
                    df[idx] = df["node_loc"]
                if idx in ["time_origin", "time_dest"]:
                    df[idx] = df["time"]

            # Calculate values of row-by-row multipliers
            mult = []
            for i in range(len(df)):
                # node_loc factor
                _node_loc = (
                    tech_data[tec]
                    .get(name, {})
                    .get("node_loc", {})
                    .get(df.get("node_loc", {}).get(2), 1)
                )

                # year_vtg factor
                # _year_vtg = (1+rate)**delta_years
                _year_vtg = (
                    (
                        (
                            1
                            + tech_data[tec]
                            .get(name, {})
                            .get("year_vtg", {})
                            .get("rate", 0)
                        )
                        ** (df["year_vtg"][i] - tech_data[tech]["year_init"])
                    )
                    if "year_vtg" in df.columns
                    else 1
                )

                # year_act factor
                # _year_act = (1+rate)**(year_act-year_vtg) if both years present
                # _year_act = (1+rate)**(year_act-first_active_year) if no year_vtg
                _year_act = (
                    (
                        (
                            1
                            + tech_data[tec]
                            .get(name, {})
                            .get("year_act", {})
                            .get("rate", 0)
                        )
                        ** (
                            df["year_act"][i]
                            - (
                                df["year_vtg"][i]
                                if "year_vtg" in df.columns
                                else tech_data[tech]["year_init"]
                            )
                        )
                    )
                    if "year_act" in df.columns
                    else 1
                )

                # get mode multiplier from model_data
                _mode = (
                    tech_data[tec]
                    .get(name, {})
                    .get("mode", {})
                    .get(df.get("mode", {}).get(i), 1)
                )

                mult.append(
                    np.prod(
                        [
                            _node_loc,
                            _year_vtg,
                            _year_act,
                            _mode,
                        ]
                    )
                )

            # index adjusted df
            value = df["value"] * mult
            value = [round(e, 3) for e in value]
            df["value"] = value

            data[tec][name] = df

    return data


def print_df(scenario, filepath=""):
    if not filepath:
        module_path = os.path.abspath(__file__)  # get the module path
        package_path = os.path.dirname(
            os.path.dirname(module_path)
        )  # get the package path
        path = os.path.join(
            package_path, "add_dac/tech_data.yaml"
        )  # join the current working directory with a filename
        data = generate_df(scenario, path)
        for tec, val in data.items():
            with pd.ExcelWriter(f"{tec}.xlsx", engine="xlsxwriter", mode="w") as writer:
                for sheet_name, sheet_data in val.items():
                    sheet_data.to_excel(writer, sheet_name=sheet_name, index=False)
    else:
        data = generate_df(scenario, filepath)
        for tec, val in data.items():
            with pd.ExcelWriter(f"{tec}.xlsx", engine="xlsxwriter", mode="w") as writer:
                for sheet_name, sheet_data in val.items():
                    sheet_data.to_excel(writer, sheet_name=sheet_name, index=False)


def add_dac(scenario, filepath=""):
    """
    Parameters
    ----------
    scenario    : message_ix.Scenario()
        MESSAGEix Scenario where the data will be included
    filepath    : string, path of the input file
        the default is in the module's folder
    """

    # year_df = scenario.vintage_and_active_years()
    # vintage_years, act_years = year_df["year_vtg"], year_df["year_act"]
    if "CO2_storage" not in scenario.set("emission"):
        scenario.add_set("emission", "CO2_storage")
    if "co2_storage_pot" not in scenario.set("type_emission"):
        scenario.add_set("type_emission", "co2_storage_pot")
    if "co2_potential" not in scenario.set("type_tec"):
        scenario.add_set("type_tec", "co2_potential")
    if "dacco2_tr_dis" not in scenario.set("technology"):
        scenario.add_set("technology", "dacco2_tr_dis")

    scenario.add_set("cat_emission", ["co2_storage_pot", "CO2_storage"])
    scenario.add_set("cat_tec", ["co2_potential", "dacco2_tr_dis"])

    # Reading new technology database
    if not filepath:
        module_path = os.path.abspath(__file__)  # get the module path
        package_path = os.path.dirname(
            os.path.dirname(module_path)
        )  # get the package path
        path = os.path.join(
            package_path, "add_dac/tech_data.yaml"
        )  # join the current working directory with a filename
        data = generate_df(scenario, path)
    else:
        data = generate_df(scenario, filepath)

    if not filepath:
        module_path = os.path.abspath(__file__)  # get the module path
        package_path = os.path.dirname(
            os.path.dirname(module_path)
        )  # get the package path
        path = os.path.join(
            package_path, "add_dac/tech_data.yaml"
        )  # join the current working directory with a filename
        with open(path, "r") as stream:
            tech_data = yaml.safe_load(stream)
    else:
        with open(filepath, "r") as stream:
            tech_data = yaml.safe_load(stream)

    # Adding parameters by technology and name
    for tec, val in data.items():
        if tec not in set(scenario.set("technology")):
            scenario.add_set("technology", tec)

        for name in val.keys():
            if tech_data[tec][name]["par_name"] == "relation_activity":
                if tech_data[tec][name]["relation"][0] not in set(
                    scenario.set("relation")
                ):
                    scenario.add_set("relation", tech_data[tec][name]["relation"][0])
            scenario.add_par(tech_data[tec][name]["par_name"], data[tec][name])

    # Adding other requirements
    n_nodes = np.int32(len(scenario.set("node")) - 2)  # excluding 'World' and 'RXX_GLB'
    reg_exception = ["World", f"R{n_nodes}_GLB"]
    node_loc = [e for e in scenario.set("node") if e not in reg_exception]
    year_act = [e for e in scenario.set("year") if e >= 2025]

    # Creating dataframe for CO2_Emission_Global_Total relation
    # TODO: next verion should be able to check RXX_GLB
    # according to regional config used by the scenario

    CO2_global_par = []
    for tech in set(tech_data.keys()) - set(["dacco2_tr_dis", "DAC_mpen"]):
        for reg in node_loc:
            CO2_global_par.append(
                make_df(
                    "relation_activity",
                    relation="CO2_Emission_Global_Total",
                    node_rel=f"R{n_nodes}_GLB",
                    year_rel=year_act,
                    node_loc=reg,
                    technology=tech,
                    year_act=year_act,
                    mode="M1",
                    value=-1,
                    unit="-",
                )
            )
    CO2_global_par = pd.concat(CO2_global_par)

    # Adding the dataframe to the scenario
    scenario.add_par("relation_activity", CO2_global_par)

    # Setting up sets requirements
    # type_emission_list = ["co2_storage_pot"]
    # emission_list = ["CO2_storage"]
    # type_tec_list = ["co2_potential"]
    # technology_list = ["dacco2_tr_dis"]
