# this is a python implementation of the VBA RES tool developed by a former IIASA
# collaborator from Iran (name?).
# The original tool (including VBA source code) can be downloaded here:
# https://github.com/user-attachments/files/18109634/Fw_.VBA.Macros.to.Visualize.RES.diagram.zip

import pandas as pd
from graphviz import Digraph
import message_ix
import random


def random_color_hex() -> str:
    return "#{:06x}".format(random.randint(0, 0xFFFFFF))


class GraphData:
    def __init__(self, scenario: message_ix.Scenario, config):
        inp, out = self.get_scenario_data(scenario, config)
        self.levels = self.gen_level_data(out, config)
        self.technologies = self.gen_technology_data(inp, out, config)

    def get_scenario_data(self, scenario, config):
        filters = {"level": config.get("levels").keys()}
        if len(config.get("technologies")):
            filters["technology"] = config.get("technologies").keys()
        out = scenario.par("output", filters=filters)
        inp = scenario.par("input", filters=filters)

        # filter out flows with 0 values
        out = out[out["value"] != 0]
        inp = inp[inp["value"] != 0]
        return inp, out

    def gen_technology_data(
        self, inp: pd.DataFrame, out: pd.DataFrame, config
    ) -> pd.DataFrame:
        """Create technology dataframe required to generate RES diagram.

        Takes unique combinations of level, commodity and technology columns from
        input and output parameters of a scenario. Joins them for output and input and
        generates a y-coordinate for each combination. Y coordinates are assigned by
        sorting the technologies by input commodity.

        Parameters
        ----------
        inp
            Input parameter data from a message_ix scenario
        out
            Output parameter data from a message_ix scenario

        Returns
        -------
        pd.DataFrame
        """

        tec_out = out[["technology", "commodity", "level"]].drop_duplicates()
        tec_out = tec_out.rename(
            columns={"commodity": "comm_out", "level": "level_out"}
        )
        tec_inp = inp[["technology", "commodity", "level"]].drop_duplicates()
        tec_inp = tec_inp.rename(columns={"commodity": "comm_in", "level": "level_in"})

        tecs = tec_inp.set_index("technology").join(tec_out.set_index("technology"))
        tecs = tecs[
            (tecs["level_in"].isin(config.get("levels").keys()))
            & (tecs["level_out"].isin(config.get("levels").keys()))
        ]
        tecs = tecs.reset_index()
        tecs_new = pd.DataFrame()
        for level in tecs["level_in"].unique():
            prims = (
                tecs[tecs["level_in"] == level].copy(deep=True).sort_values(["comm_in"])
            )
            prims["y_coord"] = prims.reset_index().index.to_list()
            tecs_new = pd.concat([tecs_new, pd.DataFrame(prims)])
        return tecs_new

    def gen_level_data(self, out: pd.DataFrame, config) -> pd.DataFrame:
        """Create commodity level dataframe required to generate RES diagram.

        Takes unique combinations of level-commodity columns.
        X-coordinates are assigned by grouping the commodities by level.

        Parameters
        ----------
        out
            Output parameter data from a message_ix scenario

        Returns
        -------
        pd.DataFrame
        """

        levels = out[["commodity", "level"]].drop_duplicates().set_index("level")
        levels_new = pd.DataFrame()
        for level in levels.index.get_level_values(0):
            prims = levels.loc[[level]].copy(deep=True)
            prims["rank"] = prims.rank()
            levels_new = pd.concat([levels_new, pd.DataFrame(prims)])
        levels_new = levels_new.reset_index().drop_duplicates()
        levels_new["x_coord"] = levels_new.apply(
            lambda x: x["rank"] + config.get("levels").get(x.level, 0), axis=1
        )
        return levels_new


class GraphBuilder:
    def __init__(self):
        self.graph = Digraph(engine="neato")
        self.color_dict = {}

    def add_level_nodes(self, levels: pd.DataFrame) -> None:
        """Add the commodity levels to the RES stored in the "levels" DataFrame.

        Each commodity level pair needs to be mapped to an x-coordinate.

        Parameters
        ----------
        dot
            Graph to add node to
        levels
            DataFrame that contains [commodity, level and x_coord] as columns
        color_map
            Dictionary that contains a color mapping for each commodity in levels
        """
        for row in levels.iterrows():
            row = row[1]
            x = row["x_coord"]
            id = row["commodity"] + "-" + row["level"]
            label = row["commodity"]
            y = 55
            self.graph.node(
                f"{id}",
                label="",
                xlabel=label,
                labelloc="t",
                shape="rect",
                style="filled",
                height=f"{y*2}",
                width="0.0001",
                pos=f"{x},{y}!",
                color=self.color_dict[label],
            )

    def add_phantom_level_node(
        self, id: str, x: int, y: int, hide: bool = True
    ) -> None:
        """Add a "level" phantom node to the RES at the given coordinates.

        Levels are represented as thin vertical lines in the RES.

        Parameters
        ----------
        id
            Identifier of new level node
        x
            X-coordinate of node
        y
            Y-coordinate of node
        hide
            phantom nodes are hidden by default, can be set to False for debugging
        """

        label = "" if hide else id
        style = "invisible" if hide else "solid"
        self.graph.node(
            id,
            label=label,
            pos=f"{x},{y}!",
            shape="rect",
            height="0.005",
            width="0.0001",
            style=style,
        )

    def add_tec_node(
        self, name: str, x: int, y: int, height: float, log: bool = False
    ) -> None:
        """Add a technology node to the RES at the specified coordinates.

        Technologies are represented as rectangles in the RES with given height.

        Parameters
        ----------
        name
            Identifier of new node
        x
            X-coordinate of node
        y
            Y-coordinate of node
        height
            height of node shape
        log
            If True print out name and y value for debugging
        """

        if log:
            print(name, y)
        self.graph.node(
            name,
            label=name,
            fontsize="20",
            shape="rect",
            style="filled",
            color="lightblue",
            pos=f"{x},{y}!",
            height=f"{height}",
        )

    def add_phantom_tec_node(
        self, id: str, x: int, y: int, label: str, hide: bool = True
    ) -> None:
        """Add a "technology" phantom node to the RES at the given coordinates.

        Parameters
        ----------
        dot
            Graph to add node to
        name
            Identifier of new node
        x
            X-coordinate of node
        y
            Y-coordinate of node
        label
            (hidden) label of node
        hide
            If False do not hide phantom nodes to debug placement issues
        """
        style = "invisible" if hide else "solid"
        self.graph.node(
            id, label=label, fontsize="20", pos=f"{x},{y}!", shape="rect", style=style
        )

    def add_edge(self, origin: str, destination: str, color: str) -> None:
        self.graph.edge(origin, destination, color=color)

    def build_graph(self, graph_data: GraphData) -> None:
        levels = graph_data.levels
        tecs = graph_data.technologies
        self.color_dict = {k: random_color_hex() for k in levels["commodity"].unique()}
        self.add_level_nodes(levels)

        phantom_node_in_prev = None
        phantom_node_out_prev = None
        for tec in tecs.technology.unique():
            if tec == "furnace_biomass_refining":
                continue
            rows = tecs[tecs["technology"] == tec]
            y = rows["y_coord"].min() * 1.5
            name = tec
            tec_x_coord = (
                levels[levels["level"] == rows["level_in"].values[0]].x_coord.max()
                + 2.5
            )
            height = rows.index.size - 1
            self.add_tec_node(
                name, tec_x_coord, y + height * 0.25, 0.3 + height * 0.35, log=False
            )

            for i, row in enumerate(rows.iterrows()):
                y_in = y + i / 4
                y_out = y + i / 4 - 0.1
                row = row[1]
                phantom_in_x_coord = levels[
                    (levels["level"] == row["level_in"])
                    & (levels["commodity"] == row["comm_in"])
                ].x_coord.values[0]
                phantom_node_id_in = f"{row['level_in']}_{name}_{row['comm_in']}"
                if phantom_node_id_in != phantom_node_in_prev:
                    self.add_phantom_level_node(
                        phantom_node_id_in, phantom_in_x_coord, y_in, hide=True
                    )
                    self.add_phantom_tec_node(
                        phantom_node_id_in + "_tec", tec_x_coord, y_in, name, hide=True
                    )
                    self.add_edge(
                        phantom_node_id_in,
                        phantom_node_id_in + "_tec",
                        self.color_dict[row["comm_in"]],
                    )
                phantom_node_in_prev = phantom_node_id_in

                phantom_out_x_coord = levels[
                    (levels["level"] == row["level_out"])
                    & (levels["commodity"] == row["comm_out"])
                ].x_coord.values[0]
                phantom_node_id_out = f"{row['level_out']}_{name}_{row['comm_out']}"
                if phantom_node_id_out != phantom_node_out_prev:
                    self.add_phantom_level_node(
                        phantom_node_id_out, phantom_out_x_coord, y_out, hide=True
                    )
                    self.add_phantom_tec_node(
                        phantom_node_id_out + "_tec",
                        tec_x_coord,
                        y_out,
                        name,
                        hide=True,
                    )
                    self.add_edge(
                        phantom_node_id_out + "_tec",
                        phantom_node_id_out,
                        self.color_dict[row["comm_out"]],
                    )
                phantom_node_out_prev = phantom_node_id_out

    def render(self, filename: str) -> None:
        self.graph.render(filename, format="svg", cleanup=False)

    def calculate_level_line_height(self):
        # the vertical lines that represent the commodities at each level
        # need to be long enough to fit all the technology nodes. At the moment,
        # the height is hardcoded and manually adjusted.
        raise NotImplementedError

    def calculate_node_height(self):
        # if technology nodes should be different height based on the amount of connected edges
        # then node height needs to be calculated
        raise NotImplementedError


if __name__ == "__main__":
    import ixmp
    import message_ix
    import yaml

    # Load the YAML configuration file
    with open("graph_config.yaml", "r") as file:
        config = yaml.safe_load(file)

    mp = ixmp.Platform("<platform name>")
    scen = message_ix.Scenario(mp, model="<model name>", scenario="<scenario name>")

    scenario_data = GraphData(scen, config["graph"])

    graph_builder = GraphBuilder()
    graph_builder.build_graph(scenario_data)
    graph_builder.render("res_graphviz_rendering")
