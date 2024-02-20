# -*- coding: utf-8 -*-
"""
Created on Mon Mar 20 15:41:32 2023

@author: pratama
"""

import os
from collections.abc import Mapping

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
            package_path, "add_dac/DAC_all_data.yaml"
        )  # join the current working directory with a filename
        with open(path, "r") as stream:
            tech_data = yaml.safe_load(stream)
    else:
        with open(filepath, "r") as stream:
            tech_data = yaml.safe_load(stream)

    # create dictionary of parameter indices list
    par_idx = {}
    data = {}
    for tech in set(tech_data) - set(["model_data"]):
        par_idx.update(
            {
                tech: {
                    par: {idx: [] for idx in list(MESSAGE_ITEMS[par].get("idx_names"))}
                    for par in set(tech_data[tech])
                }
            }
        )
        data.update({tech: {par: [] for par in list(par_idx[tech].keys())}})

    first_active_year = tech_data["model_data"].get("first_active_year")
    years_vtg_act = scenario.vintage_and_active_years()
    years_vtg_act = years_vtg_act[years_vtg_act["year_vtg"] >= first_active_year]

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

    for tec in par_idx.keys():
        if tec not in set(scenario.set("technology")):
            scenario.add_set("technology", tec)
        for par in par_idx[tec]:
            for idx in set_elements_dict.keys():
                if idx in par_idx[tec][par].keys():
                    if len(set_elements_dict[idx]["data"]) != 0:
                        par_idx[tec][par][idx] = set_elements_dict[idx]["data"]
                    elif len(set_elements_dict[idx]["data"]) == 0:
                        if (
                            tech_data["model_data"]
                            .get(tec, {})
                            .get(par, {})
                            .get(idx, {})
                            != {}
                        ):
                            par_idx[tec][par][idx] = list(
                                tech_data["model_data"][tec][par][idx].keys()
                            )
                        else:
                            if idx in [
                                "node_loc",
                                "mode",
                            ]:  # to not including 'World' and 'all' mode
                                par_idx[tec][par][idx] = list(
                                    scenario.set(set_elements_dict[idx]["name"])
                                )[1:]
                            else:
                                par_idx[tec][par][idx] = list(
                                    scenario.set(set_elements_dict[idx]["name"])
                                )
                        # check and add set if not already exist
                        for e_idx in par_idx[tec][par][idx]:
                            if e_idx not in set(
                                scenario.set(set_elements_dict[idx]["name"])
                            ):
                                scenario.add_set(set_elements_dict[idx]["name"], e_idx)

    # Creating basic DataFrame
    count = 0
    for tech, par_dict in tech_data.items():
        if tech != "model_data":
            for par, par_data in par_dict.items():
                if not isinstance(par_data, Mapping):
                    par_data = {"value": par_data, "unit": "-"}
                # identify parameters by year dimension
                # then add the year data as kwargs as input for basic dataframe
                if all(e in par_idx[tech][par] for e in ["year_vtg", "year_act"]):
                    kwargs = {
                        "year_vtg": years_vtg_act["year_vtg"],
                        "year_act": years_vtg_act["year_act"],
                    }
                elif "year_vtg" in par_idx[tech][par]:
                    kwargs = {"year_vtg": sorted(set(years_vtg_act["year_vtg"]))}
                else:
                    kwargs = {"year_act": sorted(set(years_vtg_act["year_act"]))}
                    # if 'year_rel' is present, the values are assumed from 'year_act' values
                    if "year_rel" in par_idx[tech][par]:
                        kwargs.update(
                            {"year_rel": sorted(set(years_vtg_act["year_act"]))}
                        )

                # create parameter's basic dataframe and
                # add it to the data parameter list
                data[tech][par].append(
                    make_df(
                        par,
                        technology=tech,
                        value=par_data["value"],
                        unit=par_data["unit"],
                        **kwargs,
                    )
                )

                # duplicate the basic data using the length of each set
                # as the duplication factor
                for s in set_elements_dict.keys():
                    if s in par_idx[tech][par] and s not in ["year_vtg", "year_act"]:
                        elist = par_idx[tech][par][s]
                        data[tech][par] = data[tech][par] * len(elist)
                        for e in range(len(elist)):
                            kwarg = {s: elist[e]}
                            # print(tech,par,s)
                            data[tech][par][e] = data[tech][par][e].assign(**kwarg)
                    data[tech][par] = [
                        pd.concat(data[tech][par]).reset_index(drop=True)
                    ]
                    if "node_origin" in data[tech][par][0].columns:
                        data[tech][par][0]["node_origin"] = data[tech][par][0][
                            "node_loc"
                        ]
                    if "node_dest" in data[tech][par][0].columns:
                        data[tech][par][0]["node_dest"] = data[tech][par][0]["node_loc"]
                    if "node_rel" in data[tech][par][0].columns:
                        data[tech][par][0]["node_rel"] = data[tech][par][0]["node_loc"]

    data = {
        t: {k: pd.concat(v).reset_index(drop=True) for k, v in data[t].items()}
        for t in data.keys()
    }

    # Expanded DataFrame
    data_expand = {tech: {par: [] for par in data[tech].keys()} for tech in data.keys()}

    for tech, par_data in tech_data["model_data"].items():
        if tech != "first_active_year":
            for par in data[tech].keys():
                multiplier = []
                for i in range(len(data[tech][par])):
                    # Calculate multipliers for each element in a dimensional array.
                    # For each element, this function searches for corresponding factors
                    # in the model-specific data (model_data).
                    # If no factors are found, the multiplier is set to 1.
                    # If factors are found, the function uses the factor that matches
                    # the corresponding element in the data[par] row.

                    # get regional multiplier from model_data
                    # m_reg = par_data.get(par,{}).get('node_loc',{}).get(reg,1)
                    m_node_loc = (
                        par_data.get(par, {})
                        .get("node_loc", {})
                        .get(data[tech][par].get("node_loc", {}).get(i), 1)
                    )

                    # get year_vtg escalation rate from model_data
                    # then calculate year_vtg multiplier
                    # m_year_vtg = (1+rate)**delta_years
                    m_year_vtg = (
                        (
                            (
                                1
                                + par_data.get(par, {})
                                .get("year_vtg", {})
                                .get("rate", 0)
                            )
                            ** (data[tech][par]["year_vtg"][i] - first_active_year)
                        )
                        if "year_vtg" in data[tech][par].columns
                        else 1
                    )

                    # same as m_year_vtg
                    # m_year_act = (1+rate)**(year_act-year_vtg) if both years present
                    # m_year_act = (1+rate)**(year_act-first_active_year) if no year_vtg
                    m_year_act = (
                        (
                            (
                                1
                                + par_data.get(par, {})
                                .get("year_act", {})
                                .get("rate", 0)
                            )
                            ** (
                                data[tech][par].get("year_act", {}).get(i, 0)
                                - (
                                    data[tech][par]["year_vtg"][i]
                                    if "year_vtg" in data[tech][par].columns
                                    else first_active_year
                                )
                            )
                        )
                        if "year_act" in data[tech][par].columns
                        else 1
                    )

                    m_year_rel = (
                        (
                            (
                                1
                                + par_data.get(par, {})
                                .get("year_rel", {})
                                .get("rate", 0)
                            )
                            ** (
                                data[tech][par].get("year_rel", {}).get(i, 0)
                                - (
                                    data[tech][par]["year_vtg"][i]
                                    if "year_vtg" in data[tech][par].columns
                                    else (
                                        data[tech][par]["year_act"][i]
                                        if "year_act" in data[tech][par].columns
                                        else first_active_year
                                    )
                                )
                            )
                        )
                        if "year_rel" in data[tech][par].columns
                        else 1
                    )
                    # To do: Check again what this m_year_rel is doing.

                    # get mode multiplier from model_data
                    m_mode = (
                        par_data.get(par, {})
                        .get("mode", {})
                        .get(data[tech][par].get("mode", {}).get(i), 1)
                    )

                    # get emission multiplier from model_data
                    m_emission = (
                        par_data.get(par, {})
                        .get("emission", {})
                        .get(data[tech][par].get("emission", {}).get(i), 1)
                    )

                    # get relation multiplier
                    m_relation = (
                        par_data.get(par, {})
                        .get("relation", {})
                        .get(data[tech][par].get("relation", {}).get(i), 1)
                    )

                    multiplier.append(
                        np.prod(
                            [
                                m_node_loc,
                                m_year_vtg,
                                m_year_act,
                                m_year_act,
                                m_mode,
                                m_emission,
                                m_relation,
                            ]
                        )
                    )

                value = data[tech][par]["value"] * multiplier

                # assigning data expansion
                data_expand[tech][par].append(
                    data[tech][par].assign(value=value)  # , **kwargs)
                )

    all_params = []
    for t in data_expand.keys():
        for par in data_expand[t].keys():
            if par not in all_params:
                all_params.append(par)

    data_to_scenario = {par: [] for par in all_params}

    for k, v in data_expand.items():
        for k2, v2 in v.items():
            data_to_scenario[k2].append(v2[0])

    data_expand = {k: pd.concat(v) for k, v in data_to_scenario.items()}

    return data_expand


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
        with pd.ExcelWriter(
            "printed_data.xlsx", engine="xlsxwriter", mode="w"
        ) as writer:
            for sheet_name, sheet_data in data.items():
                sheet_data.to_excel(writer, sheet_name=sheet_name, index=False)
    else:
        data = generate_df(scenario, filepath)
        with pd.ExcelWriter(
            "printed_tech_data.xlsx", engine="xlsxwriter", mode="w"
        ) as writer:
            for sheet_name, sheet_data in data_expand.items():
                sheet_data.to_excel(writer, sheet_name=sheet_name, index=False)


# %% now modify everything below using data from the functions above
def add_dac(scenario, filepath=""):
    """
    Parameters
    ----------
    scenario    : message_ix.Scenario()
        MESSAGEix Scenario where the data will be included
    filepath    : string, path of the input file
        the default is in the module's folder
    """

    year_df = scenario.vintage_and_active_years()
    vintage_years, act_years = year_df["year_vtg"], year_df["year_act"]

    # Reading new technology database
    if not filepath:
        module_path = os.path.abspath(__file__)  # get the module path
        package_path = os.path.dirname(
            os.path.dirname(module_path)
        )  # get the package path
        path = os.path.join(
            package_path, "add_dac/DAC_all_data.yaml"
        )  # join the current working directory with a filename
        data = generate_df(scenario, path)
    else:
        data = generate_df(scenario, filepath)

    for par in data.keys():
        scenario.add_par(par, data[par])

    # Adding other requirements
    node_loc = [e for e in scenario.set("node") if e not in ["World", "R12_GLB"]]
    year_act = [e for e in scenario.set("year") if e >= 2025]

    # Creating dataframe for CO2_Emission_Global_Total relation
    CO2_global_par = []
    for tech in ["LT_DAC", "HT_DAC"]:
        for reg in node_loc:
            CO2_global_par.append(
                make_df(
                    "relation_activity",
                    relation="CO2_Emission_Global_Total",
                    node_rel="R12_GLB",
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
    type_emission_list = ["co2_storage_pot"]
    emission_list = ["CO2_storage"]

    type_tec_list = ["co2_potential"]
    technology_list = ["dacco2_tr_dis"]

    if "co2_storage_pot" not in scenario.set("type_emission"):
        scenario.add_set("type_emission", "co2_storage_pot")
    if "co2_potential" not in scenario.set("type_tec"):
        scenario.add_set("type_tec", "co2_potential")

    scenario.add_set("cat_emission", ["co2_storage_pot", "CO2_storage"])
    scenario.add_set("cat_tec", ["co2_potential", "dacco2_tr_dis"])
