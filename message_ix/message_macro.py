from collections import ChainMap

from .macro import MACRO
from .message import MESSAGE


class MESSAGE_MACRO(MESSAGE, MACRO):
    """Model class for MESSAGE_MACRO."""

    name = "MESSAGE-MACRO"
    #: All equations, parameters, sets, and variables in the MESSAGE-MACRO formulation.
    items = ChainMap(MESSAGE.items, MACRO.items)

    keyword_to_solve_arg = (
        MACRO.keyword_to_solve_arg
        + MESSAGE.keyword_to_solve_arg
        + [
            ("convergence_criterion", float, "CONVERGENCE_CRITERION"),
            ("max_adjustment", float, "MAX_ADJUSTMENT"),
            ("max_iteration", int, "MAX_ITERATION"),
        ]
    )

    @classmethod
    def initialize(cls, scenario, with_data=False):
        MESSAGE.initialize(scenario)
        MACRO.initialize(scenario, with_data)
