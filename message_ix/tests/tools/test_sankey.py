from typing import TYPE_CHECKING, cast

import pytest
from ixmp import Platform
from ixmp.testing import assert_logs

from message_ix.report import Reporter
from message_ix.testing import make_westeros
from message_ix.tools.sankey import map_for_sankey

if TYPE_CHECKING:
    import pyam

# NOTE This test likely doesn't need to be parametrized


def test_map_for_sankey(
    caplog: pytest.LogCaptureFixture, test_mp: Platform, request: pytest.FixtureRequest
) -> None:
    from genno.operator import concat

    scen = make_westeros(test_mp, solve=True, request=request)
    rep = Reporter.from_scenario(scen, units={"replace": {"-": ""}})
    df = cast(
        "pyam.IamDataFrame", concat(rep.get("in::pyam"), rep.get("out::pyam"))
    ).filter(year=700)

    # Set expectations
    expected_all = {
        "in|final|electricity|bulb|standard": ("final|electricity", "bulb|standard"),
        "in|secondary|electricity|grid|standard": (
            "secondary|electricity",
            "grid|standard",
        ),
        "out|final|electricity|grid|standard": ("grid|standard", "final|electricity"),
        "out|secondary|electricity|coal_ppl|standard": (
            "coal_ppl|standard",
            "secondary|electricity",
        ),
        "out|secondary|electricity|wind_ppl|standard": (
            "wind_ppl|standard",
            "secondary|electricity",
        ),
        "out|useful|light|bulb|standard": ("bulb|standard", "useful|light"),
    }

    # Load all variables
    assert expected_all == map_for_sankey(df, node="Westeros")

    x = "final|electricity"
    assert {k: v for (k, v) in expected_all.items() if x not in v} == map_for_sankey(
        df, node="Westeros", exclude=[x]
    )

    with assert_logs(caplog, "No mapping entries generated"):
        map_for_sankey(df, node="not_a_node")
