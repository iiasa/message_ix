import numpy as np
import pandas as pd
import pandas.testing as pdt

from message_ix import make_df
from message_ix.testing import make_westeros


def test_soft_constraint(request, test_mp):
    s = make_westeros(test_mp, request=request)

    common = dict(technology="coal_ppl", time="year")

    with s.transact("Add soft constraints"):
        # Reduce dynamic constraint from 10% to 5%, so that soft relaxation of the
        # constraint is required for the scenario to be feasible
        gae = "growth_activity_up"
        s.add_par(gae, s.par(gae).assign(value=0.05))

        # Add soft constraint
        sau = "soft_activity_up"
        s.add_par(
            sau,
            make_df(
                sau, **common, node_loc="Westeros", year_act=700, value=0.7, unit="-"
            ),
        )

    s.solve(var_list=["ACT_UP"])

    # The value for 'ACT_UP' should be equal to the historical activity of coal_ppl
    ha = s.par("historical_activity", filters={"technology": "coal_ppl"})
    exp = pd.DataFrame(
        dict(**common, node=["Westeros"], year=700, lvl=ha.at[0, "value"], mrg=0.0)
    )
    obs = s.var("ACT_UP")

    pdt.assert_frame_equal(exp, obs, check_like=True, check_dtype=False)

    # Ensure that the objective function is the same
    assert np.isclose(s.var("OBJ")["lvl"], 173408.40625)
