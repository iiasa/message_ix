from collections.abc import MutableMapping
from functools import partial

from ixmp.backend import ItemType

from message_ix.common import GAMSModel, Item, _boollike, _item_shorthand


class MACRO(GAMSModel):
    """Model class for MACRO."""

    name = "MACRO"

    #: All equations, parameters, sets, and variables in the MACRO formulation.
    items: MutableMapping[str, Item] = dict()

    #: MACRO uses the GAMS ``break;`` statement, and thus requires GAMS 24.8.1 or later.
    GAMS_min_version = "24.8.1"

    keyword_to_solve_arg = [("concurrent", _boollike, "MACRO_CONCURRENT")]

    @classmethod
    def initialize(cls, scenario, with_data=False):
        """Initialize the model structure."""
        # NB some scenarios already have these items. This method simply adds any
        #    missing items.

        # Initialize the ixmp items for MACRO
        cls.initialize_items(scenario, {k: v.to_dict() for k, v in cls.items.items()})


equ = partial(_item_shorthand, MACRO, ItemType.EQU)
par = partial(_item_shorthand, MACRO, ItemType.PAR)
_set = partial(_item_shorthand, MACRO, ItemType.SET)
var = partial(_item_shorthand, MACRO, ItemType.VAR)


#: ixmp items (sets, parameters, variables, and equations) for MACRO.
_set("sector")
_set("mapping_macro_sector", "sector c l")
par("MERtoPPP", "n y")
par("aeei", "n sector y")
par("cost_MESSAGE", "n y")
par("demand_MESSAGE", "n sector y")
par("depr", "node")
par("drate", "node")
par("esub", "node")
par("gdp_calibrate", "n y")
par("grow", "n y")
par("historical_gdp", "n y")
par("kgdp", "node")
par("kpvs", "node")
par("lakl", "node")
par("lotol", "node")
par("prfconst", "n sector")
par("price_MESSAGE", "n sector y")
var("C", "n y", "Total consumption")
var("COST_NODAL", "n y")
var("COST_NODAL_NET", "n y", "Net of trade and emissions cost")
var("DEMAND", "n c l y h")
var("EC", "n y")
var("GDP", "n y")
var("I", "n y", "Total investment")
var("K", "n y")
var("KN", "n y")
var("MAX_ITER", "")
var("N_ITER", "")
var("NEWENE", "n sector y")
var("PHYSENE", "n sector y")
var("PRICE", "n c l y h")
var("PRODENE", "n sector y")
var("UTILITY", "")
var("Y", "n y")
var("YN", "n y")
var("aeei_calibrate", "n sector y")
var("grow_calibrate", "n y")
equ("COST_ACCOUNTING_NODAL", "n y")
