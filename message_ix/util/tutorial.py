import logging
from contextlib import contextmanager
from functools import partial

from message_ix import Scenario
from message_ix.report import Key, Reporter, operator

log = logging.getLogger(__name__)

PLOTS = [
    ("activity", operator.stacked_bar, "out:nl-t-ya", "GWa"),
    ("capacity", operator.stacked_bar, "CAP:nl-t-ya", "GW"),
    ("demand", operator.stacked_bar, "demand:n-c-y", "GWa"),
    ("extraction", operator.stacked_bar, "EXT:n-c-g-y", "GW"),
    ("new capacity", operator.stacked_bar, "CAP_NEW:nl-t-yv", "GWa"),
    ("prices", operator.stacked_bar, "PRICE_COMMODITY:n-c-y", "¢/kW·h"),
]


def prepare_plots(rep: Reporter, input_costs="$/GWa") -> None:
    """Prepare `rep` to generate plots for tutorial energy models.

    Makes available several keys:

    - ``plot activity``
    - ``plot demand``
    - ``plot extraction``
    - ``plot fossil supply curve``
    - ``plot capacity``
    - ``plot new capacity``
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
    }.get(input_costs, 1.0)

    # Basic setup of the reporter
    rep.configure(units={"replace": {"-": ""}})

    # Add one node to the reporter for each plot
    for title, func, key_str, units in PLOTS:
        # Convert the string to a Key object so as to reference its .dims
        key = Key(key_str)

        # Operation for the reporter
        comp = partial(
            # The function to use, e.g. stacked_bar()
            func,
            # Other keyword arguments to the plotting function
            dims=key.dims,
            units=units,
            title=f"Energy System {title.title()}",
            cf=1.0 if title != "prices" else (cost_unit_conv * 100 / 8760),
            stacked=title != "prices",
        )

        # Add the computation under a key like "plot activity"
        rep.add(f"plot {title}", (comp, key))

    rep.add(
        "plot fossil supply curve",
        (
            partial(
                operator.plot_cumulative,
                labels=("Fossil supply", "Resource volume", "Cost"),
            ),
            "resource_volume:n-g",
            "resource_cost:n-g-y",
        ),
    )


@contextmanager
def solve_modified(base: Scenario, new_name: str):
    """Context manager for a cloned scenario.

    At the end of the block, the modified Scenario yielded by :func:`solve_modified` is
    committed, set as default, and solved. Use in a ``with:`` statement to make small
    modifications and leave a variable in the current scope with the solved scenario.

    Examples
    --------
    >>> with solve_modified(base_scen, "new name") as s:
    ...     s.add_par( ... )  # Modify the scenario
    ...     # `s` is solved at the end of the block

    Yields
    ------
    .Scenario
        Cloned from `base`, with the scenario name `new_name` and no solution.
    """
    s = base.clone(
        scenario=new_name,
        annotation=f"Cloned by solve_modified() from {repr(base.scenario)}",
        keep_solution=False,
    )
    s.check_out()

    yield s

    s.commit("Commit by solve_modified() at end of 'with:' statement")
    s.set_as_default()
    s.solve()
