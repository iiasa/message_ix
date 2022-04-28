import numpy as np
import pandas as pd
import pandas.testing as pdt

from message_ix.testing import make_westeros


def test_soft_constraint(test_mp):
    s = make_westeros(test_mp, quiet=True)
    s.check_out()

    # Reduce dynamic constraint to require
    # soft_constraint to make a feasible scenario.
    # Change from 10% to 5%.
    df = s.par("growth_activity_up")
    df.value = 0.05
    s.add_par("growth_activity_up", df)
    s.init_var("ACT_UP", ["node", "technology", "year", "time"])

    # Add soft constraints for 'coal_ppl'
    df = pd.DataFrame(
        {
            "node_loc": "Westeros",
            "technology": "coal_ppl",
            "year_act": 700,
            "time": "year",
            "value": [0.7],
            "unit": "-",
        }
    )
    s.add_par("soft_activity_up", df)

    s.commit("Soft constraints added")
    s.solve(var_list=["ACT_UP"])

    # Ensure that the value for 'ACT_UP' is correct.
    # The value of ACT_UP should be equal to the historical
    # activity of coal_ppl
    val = float(
        round(
            s.par("historical_activity", filters={"technology": "coal_ppl"})["value"], 6
        )
    )

    exp = pd.DataFrame(
        {
            "node": ["Westeros"],
            "technology": "coal_ppl",
            "year": 700,
            "time": "year",
            "lvl": val,
            "mrg": 0.0,
        }
    )

    obs = s.var("ACT_UP")

    pdt.assert_frame_equal(exp, obs, check_dtype=False)

    # Ensure that the objective function is the same
    assert np.isclose(s.var("OBJ")["lvl"], 173408.40625)
