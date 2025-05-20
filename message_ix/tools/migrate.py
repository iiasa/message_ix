"""Tools for migrating :class:`Scenario` data across versions of :mod:`message_ix`."""

import logging
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from message_ix import Scenario

log = logging.getLogger(__name__)


def initial_new_capacity_up_v311(
    s: "Scenario", *, safety_factor: float = 1.0, debug: bool = False
) -> None:
    """Adapt values of |initial_new_capacity_up|.

    This function adapts data in line with the revised formulation of
    ``NEW_CAPACITY_CONSTRAINT_UP`` per :pull:`924`. In particular, it:

    - Computes the *effective* value of the constraint on ``CAP_NEW`` under the old
      formulation.
    - Computes new values for the parameter that give the same effective constraint,
      using values for |growth_new_capacity_up| and |duration_period| in the `scenario`.
    - Updates initial_new_capacity_up with these values.

    *All* values in initial_new_capacity_up are rewritten in this way.
    """
    # TODO Move this to top level when dropping support for Python 3.9
    from itertools import pairwise

    if migration_applied(s, "initial_new_capacity_up_v311"):
        log.info(
            "Migration 'initial_new_capacity_up_v311' already applied to this scenario"
        )
        return

    # Common dimensions of `incu` and `gncu`
    dims = ["node_loc", "technology", "year_vtg"]

    # Retrieve data from the scenario
    # - Sort each data frame for the benefit of DataFrame.merge()
    incu = (
        s.par("initial_new_capacity_up")
        .rename(columns={"value": "value_old"})
        .sort_values(dims, ignore_index=True)
    )
    gncu = (
        s.par("growth_new_capacity_up")
        .rename(columns={"value": "gncu"})
        .drop("unit", axis=1)
        .sort_values(dims, ignore_index=True)
    )
    dp = (
        s.par("duration_period")
        .rename(columns={"value": "dp", "year": "year_vtg"})
        .drop("unit", axis=1)
        .sort_values("year_vtg", ignore_index=True)
    )

    # Mapping from each period ('year' set element) to the next period. Map the last
    # period to a high value, outside the horizon.
    y = sorted(s.set("year"))
    y_shift = {a: b for a, b in pairwise(y)} | {y[-1]: y[-1] * 2}

    # Compute k_gncu by the same method as the current GAMS implementation

    # Compute gncu_1, gncu_2
    df0 = (
        gncu.merge(dp, how="left")
        .eval("gncu_1 = (1 + gncu) ** dp")
        .eval("gncu_2 = (gncu_1 - 1) / (dp * log(1 + gncu))")
    )
    # - Merge with y-shifted values:
    #   - Populate y_shift; replace year_vtg with this column.
    #   - Rename gncu_[12] → gncu_[12]_prev.
    #   - Merge on (nl, t, yv)
    # - Fill NaNs with 1.0
    # - Compute k_gncu.
    # - Select columns. To DEBUG, replace the column selection with slice(None).
    k_gncu = (
        df0.merge(
            df0.assign(y_shift=lambda df: df.year_vtg.replace(y_shift))
            .drop(["dp", "gncu", "year_vtg"], axis=1)
            .rename(
                columns={
                    "gncu_1": "gncu_1_prev",
                    "gncu_2": "gncu_2_prev",
                    "y_shift": "year_vtg",
                }
            ),
            how="left",
        )
        .fillna(1.0)
        .eval("k_gncu = gncu_1_prev * gncu_2 / gncu_2_prev")[dims + ["k_gncu"]]
    )

    # Compute the new value of the constraint

    # - Merge dp, gncu, and k_gncu, keeping only the keys (unique `dims`) from `incu`.
    # - Compute `k_old`, the multiplier on `incu` in the old GAMS implementation:
    #   - k_old0 as an expression using growth_new_capacity_up.
    #   - Use k_old0 if gncu is populated (not NaN) and non-zero; else duration_period.
    # - Compute the effective value of the constraint on CAP_NEW in the old
    #   implementation.
    # - Compute the new value for initial_new_capacity_up consistent with the current
    #   GAMS implementation.
    result = (
        incu.merge(dp, how="left")
        .merge(gncu, how="left")
        .merge(k_gncu, how="left")
        .eval("k_old0 = (((1 + gncu) ** dp) - 1) / gncu")
        .assign(k_old=lambda df: df.k_old0.where(df.gncu.notna() & df.gncu != 0, df.dp))
        .eval("CAP_NEW_up = value_old * k_old")
        .eval("value = CAP_NEW_up / k_gncu * @safety_factor")
    )

    if debug:  # pragma: no cover
        result.to_csv("result.csv", index=False)
        result.describe().to_csv("result-describe.csv")

    assert len(result) == len(incu), (len(result), len(incu))
    assert not result.value.isna().any()

    with s.transact("Adjust initial_new_capacity_up"):
        s.add_par("initial_new_capacity_up", result[dims + ["value", "unit"]])


def migration_applied(scenario: "Scenario", name: str) -> bool:
    """Record and confirm whether migration `name` has been applied.

    If `scenario` contains a set named "message_ix_migration_applied" with an element
    `name`, this indicates the migration has already been applied, and the function
    returns True. Otherwise, the function creates the set (if necessary), adds the
    element `name`, and returns False.

    Returns
    -------
    bool :
        :any:`True` if migration `name` has been applied. :any:`False` if not.
    """
    with scenario.transact(f"Record migration {name!r}"):
        try:
            scenario.init_set("message_ix_migration_applied")
        except ValueError:
            pass
        if name in scenario.set("message_ix_migration_applied").values:
            return True
        else:
            scenario.add_set("message_ix_migration_applied", name)
            return False


def v311(scenario: "Scenario") -> None:
    """Adapt data in `s` for changes between :mod:`message_ix` v3.10.0 and v3.11.0.

    This calls :func:`initial_new_capacity_up_v311`.
    """
    initial_new_capacity_up_v311(scenario)
