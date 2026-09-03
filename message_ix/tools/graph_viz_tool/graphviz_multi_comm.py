import os
import warnings

import graphviz
import pandas as pd

warnings.filterwarnings("ignore", category=RuntimeWarning)


# --------------------------
# Load or extract I/O (caching logic preserved)
# --------------------------
def load_or_extract_io(scen, model, scenario, node, year, commodities):
    in_file = f"{model}_{scenario}_inputs.csv"
    out_file = f"{model}_{scenario}_outputs.csv"
    dem_file = f"{model}_{scenario}_demand.csv"

    if (
        os.path.exists(in_file)
        and os.path.exists(out_file)
        and os.path.exists(dem_file)
    ):
        print(f"Reading cached data: {in_file}, {out_file}, {dem_file}")
        df_in = pd.read_csv(in_file)
        df_out = pd.read_csv(out_file)
        df_dem = pd.read_csv(dem_file)
        return df_in, df_out, df_dem

    print("Extracting from scenario…")
    df_in = scen.par("input", {"node_loc": node, "year_act": year}).copy()
    df_out = scen.par("output", {"node_loc": node, "year_act": year}).copy()
    df_dem = scen.par("demand", {"node": node, "year": year}).copy()

    # Normalize column names
    df_in = df_in.rename(columns={"commodity": "comm_in", "level": "level_in"})
    df_out = df_out.rename(columns={"commodity": "comm_out", "level": "level_out"})
    df_dem = df_dem.rename(columns={"commodity": "comm", "level": "level"})

    # Filter to commodities of interest
    if commodities:
        df_in = df_in[df_in["comm_in"].isin(commodities)].copy()
        df_out = df_out[df_out["comm_out"].isin(commodities)].copy()
        df_dem = df_dem[df_dem["comm"].isin(commodities)].copy()

    # Save to CSV
    df_in.to_csv(in_file, index=False)
    df_out.to_csv(out_file, index=False)
    df_dem.to_csv(dem_file, index=False)
    print(f"Saved to {in_file}, {out_file}, {dem_file}")

    return df_in, df_out, df_dem


# --------------------------
# Small helper: enforce comm_* and level_* names (safe-guard)
# --------------------------
def ensure_comm_level_cols(df_in, df_out, df_dem=None):
    if "comm_in" not in df_in.columns:
        if "commodity" in df_in.columns:
            df_in = df_in.rename(columns={"commodity": "comm_in"})
        else:
            df_in["comm_in"] = ""
    if "level_in" not in df_in.columns:
        if "level" in df_in.columns:
            df_in = df_in.rename(columns={"level": "level_in"})
        else:
            df_in["level_in"] = ""

    if "comm_out" not in df_out.columns:
        if "commodity" in df_out.columns:
            df_out = df_out.rename(columns={"commodity": "comm_out"})
        else:
            df_out["comm_out"] = ""
    if "level_out" not in df_out.columns:
        if "level" in df_out.columns:
            df_out = df_out.rename(columns={"level": "level_out"})
        else:
            df_out["level_out"] = ""

    if df_dem is not None:
        if "comm" not in df_dem.columns and "commodity" in df_dem.columns:
            df_dem = df_dem.rename(columns={"commodity": "comm"})
        if "level" not in df_dem.columns:
            df_dem["level"] = ""

    return df_in, df_out, df_dem


# --------------------------
# Update Graphviz plotting
# --------------------------
def plot_flows_graphviz(df_in, df_out, df_dem, model, scenario, commodities):
    dot = graphviz.Digraph(comment=f"{model} {scenario} flows", format="png")
    dot.attr(rankdir="LR", splines="ortho")

    # Set of demand commodity.level
    demand_comms = (
        {f"{r.comm}.{r.level}" for r in df_dem.itertuples()}
        if not df_dem.empty
        else set()
    )

    # --- Build sets of techs connected to main commodities ---
    techs_in = df_in[df_in["comm_in"].isin(commodities)]["technology"].unique()
    techs_out = df_out[df_out["comm_out"].isin(commodities)]["technology"].unique()
    techs = set(techs_in).union(techs_out)

    # --- Main commodities actually connected ---
    main_in = df_in[df_in["technology"].isin(techs)][["comm_in", "level_in"]]
    main_out = df_out[df_out["technology"].isin(techs)][["comm_out", "level_out"]]

    main_comms = {
        f"{r.comm_in}.{r.level_in}"
        for r in main_in.itertuples()
        if r.comm_in in commodities
    } | {
        f"{r.comm_out}.{r.level_out}"
        for r in main_out.itertuples()
        if r.comm_out in commodities
    }

    # --- Extra commodities connected to those techs ---
    extra_in = {
        f"{r.comm_in}.{r.level_in}"
        for r in main_in.itertuples()
        if r.comm_in not in commodities
    }
    extra_out = {
        f"{r.comm_out}.{r.level_out}"
        for r in main_out.itertuples()
        if r.comm_out not in commodities
    }
    extra_comms = extra_in | extra_out

    # --- Add commodity nodes ---
    for c in main_comms:
        if c in demand_comms:
            dot.node(
                c,
                label=c,
                shape="ellipse",
                style="filled",
                fillcolor="violet",
                color="black",
                fontcolor="black",
            )
        else:
            dot.node(
                c,
                label=c,
                shape="ellipse",
                style="filled",
                fillcolor="lightgray",
                color="black",
                fontcolor="black",
            )

    for c in extra_comms:
        dot.node(c, label=c, shape="ellipse", color="red", fontcolor="red")

    # --- Technology nodes ---
    for t in techs:
        dot.node(t, shape="box", style="rounded,filled", fillcolor="lightblue")

    # --- Deduplicate edges by (src, dst, type) ---
    edges_seen = {}
    for _, row in df_in[df_in["technology"].isin(techs)].iterrows():
        src = f"{row.comm_in}.{row.level_in}"
        key = (src, row.technology, "in")
        year_vtg = row.get("year_vtg", row.year_act)
        edges_seen.setdefault(key, []).append(year_vtg)

    for _, row in df_out[df_out["technology"].isin(techs)].iterrows():
        dst = f"{row.comm_out}.{row.level_out}"
        key = (row.technology, dst, "out")
        year_vtg = row.get("year_vtg", row.year_act)
        edges_seen.setdefault(key, []).append(year_vtg)

    # --- Draw edges ---
    for (src, dst, typ), years in edges_seen.items():
        latest = max(years)
        multiple = len(set(years)) > 1
        style = "dashed" if multiple else "solid"
        color = "red" if (src in extra_comms or dst in extra_comms) else "black"
        dot.edge(src, dst, style=style, color=color)

    # --- Legend ---
    with dot.subgraph(name="cluster_legend") as c:
        c.attr(label="Legend", fontsize="10", rankdir="LR")
        c.node("solid_arrow", label="single vintage", shape="plaintext")
        c.edge("solid_arrow", "dashed_arrow", style="solid")
        c.node("dashed_arrow", label="multiple vintages", shape="plaintext")
        c.edge("solid_arrow", "dashed_arrow", style="dashed")

        # Region/year info
        c.node("region_year", label=f"Region: {NODE}, Year: {YEAR}", shape="plaintext")

        # Boxes meaning
        c.node(
            "tech_box",
            label="Technology",
            shape="box",
            style="rounded,filled",
            fillcolor="lightblue",
        )
        c.node(
            "comm_grey",
            label="Commodity",
            shape="ellipse",
            style="filled",
            fillcolor="lightgray",
        )
        c.node(
            "comm_violet",
            label="Demand commodity",
            shape="ellipse",
            style="filled",
            fillcolor="violet",
        )
        # c.node(
        #     "comm_red",
        #     label="Extra linked commodity",
        #     shape="ellipse",
        #     color="red",
        #     fontcolor="red",
        # )

    # --- Save ---
    png_name = f"{model}_{scenario}_ascii_flows"
    svg_name = f"{model}_{scenario}_ascii_flows"

    dot.format = "png"
    dot.render(filename=png_name, cleanup=True)
    dot.format = "svg"
    dot.render(filename=svg_name, cleanup=True)

    print(f"Saved Graphviz PNG: {png_name}.png, SVG: {svg_name}.svg")


# --------------------------
# Main
# --------------------------
if __name__ == "__main__":
    """
    Note: need to delete the csv files if you are re-running with different 
    commodities
    """
    # ==== User-editable configuration ====
    PLATFORM_NAME = "<database_name>"  # only used if CSV cache missing
    MODEL = "<model_name>"  # e.g. "MESSAGEix-Nexus"
    SCENARIO = "<scenario_name>"
    NODE = "R12_CHN"
    YEAR = 2050
    # Define the commodities you want (only these will be kept)
    COMMODITIES = [
        "electr",
        "coal",
    ]
    # =====================================

    in_file = f"{MODEL}_{SCENARIO}_inputs.csv"
    out_file = f"{MODEL}_{SCENARIO}_outputs.csv"
    dem_file = f"{MODEL}_{SCENARIO}_demand.csv"

    # If cached CSVs exist, load without connecting to ixmp
    if (
        os.path.exists(in_file)
        and os.path.exists(out_file)
        and os.path.exists(dem_file)
    ):
        print("Loading cached CSVs…")
        df_in = pd.read_csv(in_file)
        df_out = pd.read_csv(out_file)
        df_dem = pd.read_csv(dem_file)
        # Normalize column names (old CSVs may be different)
        df_in, df_out, df_dem = ensure_comm_level_cols(df_in, df_out, df_dem)
        # Apply commodity filter again (defensive)
        if COMMODITIES:
            df_in = df_in[df_in["comm_in"].isin(COMMODITIES)].copy()
            df_out = df_out[df_out["comm_out"].isin(COMMODITIES)].copy()
    else:
        # Need to connect and extract
        import ixmp

        import message_ix

        mp = ixmp.Platform(PLATFORM_NAME)
        scen = message_ix.Scenario(mp, model=MODEL, scenario=SCENARIO)
        df_in, df_out, df_dem = load_or_extract_io(
            scen, MODEL, SCENARIO, NODE, YEAR, COMMODITIES
        )
        # Explicit cleanup
        mp.close_db()

    # Final safety normalization (ensure col names exist)
    df_in, df_out, df_dem = ensure_comm_level_cols(df_in, df_out, df_dem)

    # Plots
    plot_flows_graphviz(df_in, df_out, df_dem, MODEL, SCENARIO, COMMODITIES)
