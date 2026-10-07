from typing import List

import pandas as pd
import pyvis as pv
from message_ix_models.util import load_package_data

pyvis_hierarchy_config = {
    "enabled": True,
    "direction": "LR",
    "blockShifting": True,
    "edgeMinimization": False,
    "parentCentralization": False,
    "levelSeparation": 150,
    "treeSpacing": 200,
}

T_D_TECS_COLOR = "#f7cf26"


def load_technology_annotations():
    tec_codes = load_package_data("technology")
    tec_descriptions = {k: v.get("description") for k, v in tec_codes.items()}
    return tec_descriptions


class DynamicGraph:
    def __init__(self, commodities: List[str]):
        self.graph = pv.network.Network(
            layout="reingold_tilford",
            select_menu=True,
            directed=True,
            heading="commodity flow graph",
        )
        self.graph.options.physics.enabled = False
        self.graph.options.layout.hierarchical = pyvis_hierarchy_config
        self.tec_annotations = load_technology_annotations()
        self.commodities = commodities

    def add_graph_elements(
        self, levels: pd.DataFrame, tecs_in: pd.DataFrame, tecs_out: pd.DataFrame
    ):
        level_location = {k: 2 * v for v, k in enumerate(levels.level)}
        for row in levels.iterrows():
            row = row[1]
            self.graph.add_node(
                row.level, row.level, shape="box", level=level_location.get(row.level)
            )

        for row in tecs_in.iterrows():
            row = row[1]
            self.graph.add_node(
                row.technology,
                row.technology,
                level=level_location.get(row.level_in) + 1,
                title=self.tec_annotations.get(row.technology),
            )
            self.graph.add_edge(row.level_in, row.technology, title=row.comm_in)

        for row in tecs_out.iterrows():
            row = row[1]
            self.graph.add_node(
                row.technology,
                row.technology,
                level=level_location.get(row.level_out) - 1,
                title=self.tec_annotations.get(row.technology),
            )
            self.graph.add_edge(row.technology, row.level_out, title=row.comm_out)

    def highlight_transmission_tecs(self, tecs: pd.DataFrame):
        # highlight transmission technologies with different color
        transmission_tecs = tecs[
            (tecs["comm_in"] == tecs["comm_out"])
            & (tecs["comm_out"].isin(self.commodities))
        ].technology.to_list()
        for node in self.graph.nodes:
            if node.get("label") in transmission_tecs:
                node["color"] = T_D_TECS_COLOR


if __name__ == "__main__":
    import ixmp
    import message_ix
    import yaml
    from graphviz_res import GraphData

    mp = ixmp.Platform("<platform name>")
    scen = message_ix.Scenario(mp, model="<model name>", scenario="<scenario name>")

    # Load the YAML configuration file
    with open("graph_config.yaml", "r") as file:
        config = yaml.safe_load(file)

    scenario_data = GraphData(scen, config["graph"])

    commodities = ["coal"]
    graph = DynamicGraph(commodities)
    levels = scenario_data.levels[scenario_data.levels["commodity"].isin(commodities)]
    tecs_in = scenario_data.technologies[
        (scenario_data.technologies["comm_in"].isin(commodities))
    ]
    tecs_out = scenario_data.technologies[
        (scenario_data.technologies["comm_out"].isin(commodities))
    ]
    graph.add_graph_elements(levels, tecs_in, tecs_out)
    graph.highlight_transmission_tecs(scenario_data.technologies)
    graph.graph.save_graph("dynamic_commodity_graph_rendering.html")
