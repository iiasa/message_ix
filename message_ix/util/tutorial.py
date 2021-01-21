from contextlib import contextmanager
from functools import partial

import message_ix
from message_ix.reporting import Key, Reporter, computations

PLOTS = [
    ("activity", computations.stacked_bar, "out:nl-t-ya", "GWa"),
    ("capacity", computations.stacked_bar, "CAP:nl-t-ya", "GW"),
    ("demand", computations.stacked_bar, "demand:n-c-y", "GWa"),
    ("extraction", computations.stacked_bar, "EXT:n-c-g-y", "GW"),
    ("new capacity", computations.stacked_bar, "CAP_NEW:nl-t-yv", "GWa"),
    ("prices", computations.stacked_bar, "PRICE_COMMODITY:n-c-y", "¢/kW·h"),
]


def prepare_plots(rep: Reporter, input_costs="$/GWa") -> None:
    """Prepare `rep` to generate plots for tutorial energy models.

    Makes available several keys:

    - ``plot activity``
    - ``plot extraction``
    - ``plot capacity``
    - ``plot prices``

    To control the contents of each plot, use :meth:`.set_filters` on `rep`.
    """
    # Conversion factors between input units and plotting units
    # TODO use exact units in all tutorials
    # TODO allow the correct units to pass through reporting
    cost_unit_conv = {
        "$/GWa": 1.0,
        "$/MWa": 1e3,
        "$/kWa": 1e6,
    }.get(input_costs)

    # Basic setup of the reporter
    rep.configure(units={"replace": {"-": ""}})

    # Add one node to the reporter for each plot
    for title, func, key_str, units in PLOTS:
        # Convert the string to a Key object so as to reference its .dims
        key = Key.from_str_or_key(key_str)

        # Operation for the reporter
        comp = partial(
            # The function to use, e.g. stacked_bar()
            func,
            # Other keyword arguments to the plotting function
            dims=key.dims,
            units=units,
            title=f"Energy System {title.title()}",
            cf=1.0 if title != "Prices" else (cost_unit_conv * 100 / 8760),
        )

        # Add the computation under a key like "plot activity"
        rep.add(f"plot {title}", (comp, key))

    # TODO re-add plot_fossil_supply_curve()
    rep.add("plot fossil supply curve", lambda: "(Not implemented)")


@contextmanager
def read_scenario(platform, name, scen):
    mp = platform
    mp.open_db()
    ds = message_ix.Scenario(mp, name, scen)

    yield ds

    mp.close_db()


@contextmanager
def make_scenario(platform, country, name, base_scen, scen):
    mp = platform

    mp.open_db()
    base_ds = message_ix.Scenario(mp, name, base_scen)

    by = "by 'tutorial/utils/run_scenarios.py:make_scenario()'"
    ds = base_ds.clone(
        name,
        scen,
        "scenario generated {}, {} - {}".format(by, name, scen),
        keep_solution=False,
    )
    ds.check_out()

    yield ds

    ds.commit("changes committed {}, {} - {}".format(by, name, scen))
    ds.set_as_default()
    ds.solve("MESSAGE")

    mp.close_db()
