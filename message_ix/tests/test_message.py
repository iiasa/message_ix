import re
from collections import defaultdict
from typing import TYPE_CHECKING

import ixmp
import pytest
from ixmp.backend.jdbc import JDBCBackend

from message_ix import make_df
from message_ix.message import MESSAGE
from message_ix.testing import make_dantzig

if TYPE_CHECKING:
    from ixmp import Platform


pytestmark = pytest.mark.ixmp4_209


class TestMESSAGE:
    """Tests of :class:`.MESSAGE`."""

    def test_initialize(self, test_mp: "Platform") -> None:
        # Expected numbers of items by type
        exp = defaultdict(list)
        for name, spec in MESSAGE.items.items():
            exp[str(spec.type.name).lower()].append(name)

        # balance_equality is removed in initialize() for JDBC
        if isinstance(test_mp._backend, JDBCBackend):
            exp["set"].remove("balance_equality")

        # Use ixmp.Scenario to avoid invoking ixmp_source/Java code that automatically
        # populates empty scenarios
        s = ixmp.Scenario(test_mp, model="m", scenario="s", version="new")

        # Initialization succeeds on a totally empty scenario
        MESSAGE.initialize(s)

        # The expected items exist
        for ix_type, exp_names in exp.items():
            obs_names = getattr(s, f"{ix_type}_list")()
            assert sorted(obs_names) == sorted(exp_names)

    def test_initialize_filter_log(
        self, caplog: pytest.LogCaptureFixture, test_mp: "Platform"
    ) -> None:
        """Test :meth:`MESSAGE.initialize` logging under some conditions.

        For :class:`.Scenario` created with message_ix v3.10 or earlier, equations and
        variables may be initialized but have zero dimensions, thus empty lists of
        "index sets" and "index names". When :class:`.Scenario` is instantiated,
        :meth:`MESSAGE.initialize` is invoked, and in turn
        :meth:`ixmp.model.base.Model.initialize_items`. This method generates many log
        messages on level :data:`~logging.WARNING`.

        In order to prevent this log noise, :func:`.models._filter_log_initialize_items`
        is used. This test checks that it is effective.
        """
        # Use ixmp.Scenario to avoid invoking ixmp_source/Java code that automatically
        # populates empty scenarios
        s = ixmp.Scenario(test_mp, model="m", scenario="s", version="new")

        # Initialize an equation with no dimensions. This mocks the state of a Scenario
        # created with message_ix v3.10 or earlier.
        s.init_equ("NEW_CAPACITY_BOUND_LO", idx_sets=[], idx_names=[])

        s.commit("")
        s.set_as_default()
        caplog.clear()

        # Initialize items.
        MESSAGE.initialize(s)

        # Messages related to re-initializing items with 0 dimensions are filtered and
        # do not reach `caplog`. This assertion fails with message_ix v3.10.
        message_pattern = re.compile(
            r"Existing index (name|set)s of 'NEW_CAPACITY_BOUND_LO' \[\] do not match "
            r"\('node', '.*', 'year'\)"
        )
        extra = list(filter(message_pattern.match, caplog.messages))
        assert not extra, f"{len(extra)} unwanted log messages: {extra}"

    def test_bound_activity_lo(
        self, request: pytest.FixtureRequest, test_mp: "Platform"
    ) -> None:
        """Test setting of ``ACT.lo`` via ``bound_activity_lo``."""
        scenario = make_dantzig(test_mp, solve=False, request=request)

        # Modify scenario to set:
        # - A very high var_cost for one technology.
        # - A negative bound_activity_lo for that technology.
        #
        # This forces the solver to choose a negative ACT, and limits the magnitude.
        common = dict(
            node_loc="seattle",
            technology="transport_from_seattle",
            year_act=1963,
            year_vtg=1963,
            mode="to_chicago",
            time="year",
            unit="-",
        )

        with scenario.transact("test_bound_activity_lo"):
            b_a_l = "bound_activity_lo"
            scenario.add_par(b_a_l, make_df(b_a_l, **common, value=-100))
            scenario.add_par("var_cost", make_df("var_cost", **common, value=1e6))

        scenario.solve()

        # The solver chooses the constrained value for ACT
        common.pop("unit")
        assert -100 == scenario.var("ACT", filters=common)["lvl"].item()
