"""Add years to a MESSAGE Scenario.

\b
Examples:
$ message-ix \
    --platform default --model Austria_tutorial --scenario test_core \
    add-years
    --scen_new test_5y --years_new 2015,2025,2035,2045
$ message-ix \
    --platform default --model CD_Links_SSP2 --scenario baseline \
    add-years
    --years_new "[2015,2025,2035,2045,2055,2120]"

If --create_new=False is given, the target Scenario must already exist.

If --extrapol_neg is an integer, negative extrapolated values are are replaced
with the product of the integer and an (which?) adjacent value. By default,
negative values may be produced.

If --bound_extend is True (the default), data from previous timestep is copied
if only one data point is available for extrapolation.

"""

from functools import partial
from timeit import default_timer as timer

import click
import ixmp

import message_ix

from . import add_year


def split_value(ctx, param, value, type=str):
    """Callback for validation of comma-separated parameter values.

    *value* is parsed as "[v1,v2,v3,...]" where:

    - the square brackets are optional, and
    - each value is of type *type*.
    """
    try:
        if value is None:
            value = ""

        if value == "all":
            return value
        else:
            return list(map(type, value.strip("[]").split(",")))
    except ValueError:
        raise click.BadParameter(param.human_readable_name, value)


@click.command("add-years", help=__doc__)
@click.option("--model_new", help="new model name", default=None)
@click.option("--scen_new", help="new scenario name", default=None)
@click.option(
    "--create_new",
    help="create new scenario",
    type=bool,
    default=True,
    show_default=True,
)
@click.option(
    "--years_new", help="new years to be added", callback=partial(split_value, type=int)
)
@click.option("--firstyear_new", help="new first model year", type=int, default=None)
@click.option("--lastyear_new", help="new last model year", type=int, default=None)
@click.option(
    "--macro",
    help="also add years to MACRO parameters",
    type=bool,
    default=False,
    show_default=True,
)
@click.option(
    "--baseyear_macro", help="new base year for MACRO", type=int, default=None
)
@click.option(
    "--parameter",
    help="names of parameters to add years",
    callback=split_value,
    default="all",
    show_default=True,
)
@click.option(
    "--region",
    help="names of regions to add years",
    callback=split_value,
    default="all",
    show_default=True,
)
@click.option(
    "--rewrite",
    help="rewrite parameters in the new scenario",
    type=bool,
    default=True,
    show_default=True,
)
@click.option(
    "--unit_check",
    help="check units before adding new years",
    type=bool,
    default=False,
    show_default=True,
)
@click.option(
    "--extrapol_neg",
    help="handle negative extrapolated values",
    type=float,
    default=0.5,
    show_default=True,
)
@click.option(
    "--bound_extend",
    help="copy data from previous timestep",
    type=bool,
    default=True,
    show_default=True,
)
@click.option("--dry-run", help="Only parse arguments & exit.", is_flag=True)
@click.pass_obj
def main(
    context,
    model_new,
    scen_new,
    create_new,
    years_new,
    firstyear_new,
    lastyear_new,
    macro,
    baseyear_macro,
    parameter,
    region,
    rewrite,
    unit_check,
    extrapol_neg,
    bound_extend,
    dry_run,
):
    # The reference scenario is loaded according to the options given to
    # the top-level message-ix (=ixmp) CLI
    try:
        # AttributeError if context is None
        sc_ref = context.get("scen", None)
        if not issubclass(type(sc_ref), ixmp.Scenario):
            raise AttributeError
    except AttributeError:
        raise click.UsageError(
            "add-years requires a base scenario; use"
            "--url or --platform, --model, --scenario, and "
            "optionally --version"
        )
    else:
        # the ixmp CLI pre-loads sc_ref as an ixmp.Scenario;
        # convert to a message_ix.Scenario
        sc_ref = message_ix.Scenario(
            mp=context["mp"],
            model=sc_ref.model,
            scenario=sc_ref.scenario,
            version=sc_ref.version,
        )

    start = timer()
    print(">> message_ix.tools.add_year...")

    # Handle default arguments
    if model_new is None:
        model_new = sc_ref.model

    if scen_new is None:
        # FIXME is this a good default?
        scen_new = sc_ref.scenario + "_5y"

    new_kw = dict(model=model_new, scenario=scen_new)
    if create_new:
        new_kw.update(
            dict(
                version="new",
                annotation="5 year modelling",
            )
        )

    # Output for debugging
    print(years_new)

    if dry_run:
        # Print arguments debugging and return
        print(
            "sc_ref:",
            (sc_ref.model, sc_ref.scenario, sc_ref.version),
            "sc_new:",
            new_kw,
            "years_new:",
            years_new,
            "firstyear_new:",
            firstyear_new,
            "lastyear_new:",
            lastyear_new,
            "macro:",
            macro,
            "baseyear_macro:",
            baseyear_macro,
            "parameter:",
            parameter,
            "region:",
            region,
            "rewrite:",
            rewrite,
            "unit_check:",
            unit_check,
            "extrapol_neg:",
            extrapol_neg,
            "bound_extend:",
            bound_extend,
        )
        return

    # Retrieve the Platform that sc_ref is stored on
    mp = sc_ref.platform

    # Load or create the new scenario to which to add years
    sc_new = message_ix.Scenario(mp, **new_kw)

    if not create_new:
        # Existing scenario: remove solution and check out
        if sc_new.has_solution():
            sc_new.remove_solution()
        sc_new.check_out()

    # Calling the main function
    add_year(
        sc_ref=sc_ref,
        sc_new=sc_new,
        years_new=years_new,
        firstyear_new=firstyear_new,
        lastyear_new=lastyear_new,
        macro=macro,
        baseyear_macro=baseyear_macro,
        parameter=parameter,
        region=region,
        rewrite=rewrite,
        unit_check=unit_check,
        extrapol_neg=extrapol_neg,
        bound_extend=bound_extend,
    )

    end = timer()

    mp.close_db()

    print(
        "> Elapsed time for adding new years:",
        round((end - start) / 60),
        "min and",
        round((end - start) % 60, 1),
        "sec.",
    )

    print(
        "> New scenario with additional years is:",
        f"ixmp://{sc_new.platform.name}/{sc_new.url}",
        sep="\n",
    )
