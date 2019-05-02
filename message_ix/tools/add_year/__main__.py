"""Add additional years to a MESSAGE model/scenario instance

\b
Examples:
$ python f_addYear.py --model_ref Austria_tutorial --scen_ref test_core \
                      --scen_new test_5y --years_new 2015,2025,2035,2045
$ python f_addNewYear.py --model_ref CD_Links_SSP2 --scen_ref baseline \
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

from . import addNewYear


def split_value(ctx, param, value, type=str):
    """Callback for validation of comma-separated parameter values.

    *value* is parsed as "[v1,v2,v3,...]" where:

    - the square brackets are optional, and
    - each value is of type *type*.
    """
    try:
        if value is None:
            value = ''
        return list(map(type, value.strip('[]').split(',')))
    except ValueError:
        raise click.BadParameter(param.human_readable_name, value)


@click.command(help=__doc__)
@click.option('--model_ref', help='reference model name', required=True)
@click.option('--scen_ref', help='reference scenario name', required=True)
@click.option('--version_ref', help='version number of reference scenario',
              default=None, type=int)
@click.option('--model_new', help='new model name', default=None)
@click.option('--scen_new', help='new scenario name', default=None)
@click.option('--create_new', help='create new scenario', type=bool,
              default=True, show_default=True)
@click.option('--years_new', help='new years to be added',
              callback=partial(split_value, type=int))
@click.option('--firstyear_new', help='new first model year', type=int,
              default=None)
@click.option('--lastyear_new', help='new last model year', type=int,
              default=None)
@click.option('--macro', help='also add years to MACRO parameters', type=bool,
              default=False, show_default=True)
@click.option('--baseyear_macro', help='new base year for MACRO', type=int,
              default=None)
@click.option('--parameter', help='names of parameters to add years',
              callback=split_value, default='all', show_default=True)
@click.option('--region', help='names of regions to add years',
              callback=split_value, default='all', show_default=True)
@click.option('--rewrite', help='rewrite parameters in the new scenario',
              type=bool, default=True, show_default=True)
@click.option('--unit_check', help='check units before adding new years',
              type=bool, default=False, show_default=True)
@click.option('--extrapol_neg', help='handle negative extrapolated values',
              type=float, default=0.5, show_default=True)
@click.option('--bound_extend', help='copy data from previous timestep',
              type=bool, default=True, show_default=True)
@click.option('--dry-run', help='Only parse arguments & exit.', is_flag=True)
def main(model_ref, scen_ref, version_ref, model_new, scen_new, create_new,
         years_new, firstyear_new, lastyear_new, macro, baseyear_macro,
         parameter, region, rewrite, unit_check, extrapol_neg, bound_extend,
         dry_run):

    start = timer()
    print('>> Running the script f_addYears.py...')

    # Handle default arguments
    ref_kw = dict(model=model_ref, scen=scen_ref)
    if version_ref:
        ref_kw['version'] = version_ref

    if model_new is None:
        model_new = model_ref

    if scen_new is None:
        # FIXME is this a good default?
        scen_new = scen_ref + '_5y'

    new_kw = dict(model=model_new, scen=scen_new)
    if create_new:
        new_kw.update(dict(
            version='new',
            scheme='MESSAGE',
            annotation='5 year modelling',
        ))

    # Output for debugging
    print(years_new)

    if dry_run:
        # Print arguments debugging and return
        print(
            'sc_ref:', ref_kw,
            'sc_new:', new_kw,
            'years_new:', years_new,
            'firstyear_new:', firstyear_new,
            'lastyear_new:', lastyear_new,
            'macro:', macro,
            'baseyear_macro:', baseyear_macro,
            'parameter:', parameter,
            'region:', region,
            'rewrite:', rewrite,
            'unit_check:', unit_check,
            'extrapol_neg:', extrapol_neg,
            'bound_extend:', bound_extend,
            sep='\n')
        return

    # Load the ixmp Platform
    mp = ixmp.Platform(dbtype='HSQLDB')

    # Loading the reference scenario and creating a new scenario to add the
    # additional years
    sc_ref = message_ix.Scenario(mp, **ref_kw)

    if create_new:
        sc_new = message_ix.Scenario(mp, **new_kw)
    else:
        sc_new = message_ix.Scenario(mp, **new_kw)
        if sc_new.has_solution():
            sc_new.remove_solution()
        sc_new.check_out()

    # Calling the main function
    addNewYear(
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
        bound_extend=bound_extend)

    end = timer()

    mp.close_db()

    print('> Elapsed time for adding new years:', round((end - start) / 60),
          'min and', round((end - start) % 60, 1), 'sec.')

    print('> New scenario with additional years is: "{}"|"{}"|{}'.format(
        sc_new.model, sc_new.scenario, str(sc_new.version)))


# Execute the script
main()
