"""Get all parameters related to a certain technology/commodity/year ect. from the data base

"""
from typing import Optional

import ixmp
import message_ix

from . import get_tech_description


def main(model_ref: str, scen_ref: str, filters: dict, filename: str, version_ref: Optional[int] = None):
    print('>> message_ix.tools.get_tech_data...')

    # Handle default arguments
    ref_kw = dict(model=model_ref, scen=scen_ref)
    if version_ref:
        ref_kw['version'] = version_ref

    # Load the ixmp Platform
    mp = ixmp.Platform(dbtype='HSQLDB')

    # Loading the reference scenario
    base = message_ix.Scenario(mp, **ref_kw)

    # Calling the main function
    get_tech_description(base=base, filters=filters, filename=filename)

    mp.close_db()

# Execute the script
main()
