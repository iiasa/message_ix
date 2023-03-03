import pandas as pd
import pytest
from pandas.testing import assert_frame_equal

from message_ix.testing import make_westeros


@pytest.mark.parametrize(
    "model_horizon",
    [
        [[700, 710, 715, 720], [3.746712, 4.149163, 8.731826, 9.182337]],
        [[695, 700, 710, 720], [3.560014, 3.746712, 2.074581, 2.302091]],
    ],
)
def test_NEW_CAPACITY_UP(test_mp, model_horizon):
    """This test ensures that the correct value for "CAP_NEW" is calculated.

    This test checks that when the period length changes within the model,
    the parameter "CAP_NEW" is correctly calculated.
    We check this for the transition from 10 to 5-year timesteps, and from
    5 to 10-year timesteps.
    The values against which the test results are being compared are based
    on the assumption that due to the carbon price, the capacity installation
    of `wind_ppl` is maximized.
    Hence the values are derived by applying the parameters of `wind_ppl`
    directly to the `NEW_CAPACITY_BOUND_UP` equation."
    """
    tax_emission = pd.DataFrame(
        {
            "node": "Westeros",
            "type_emission": "GHG",
            "type_tec": "all",
            "type_year": model_horizon[0],
            "value": 30,
            "unit": "???",
        }
    )

    # Create a westeros baseline scenario including emissions
    s = make_westeros(test_mp, emissions=True, model_horizon=model_horizon[0])

    # Make changes
    with s.transact("prepare for test"):
        # Add tax_emission
        s.add_par("tax_emission", tax_emission)

        # Remove `coal_ppl` related growth constraint to avoid infeasibility
        # when applying the capacity constraint
        rem_df = s.par("growth_activity_up", filters={"technology": "coal_ppl"})
        s.remove_par("growth_activity_up", rem_df)

        # Add `initial_new_capacity_up` for `wind_ppl`
        df = pd.DataFrame(
            {
                "node_loc": "Westeros",
                "technology": "wind_ppl",
                "year_vtg": model_horizon[0],
                "value": 0.001,
                "unit": "GW",
            }
        )
        s.add_par("initial_new_capacity_up", df)

        # Add `growth_new_capacity_up` for `wind_ppl`
        df.value = 0.01
        s.add_par("growth_new_capacity_up", df)

    # Solve scenario
    s.solve()

    # Retrieve results
    obs = s.var("CAP_NEW", filters={"technology": "wind_ppl"}).set_index("node_loc")

    # Expected results
    exp = pd.DataFrame(
        {
            "node_loc": "Westeros",
            "technology": "wind_ppl",
            "year_vtg": model_horizon[0],
            "lvl": model_horizon[1],
            "mrg": 0.0,
        }
    ).set_index("node_loc")

    assert_frame_equal(exp, obs, check_dtype=False)
