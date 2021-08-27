from functools import partial
from inspect import getdoc
from logging import ERROR as FAIL
from logging import NOTSET as PASS
from logging import WARNING
from typing import Dict, Iterable, List, Optional, Union

from message_ix import Reporter, Scenario

#: List of all check functions.
CHECKS = []

# Utility functions


def append(func):
    """Add `func` to `CHECKS`."""
    CHECKS.append(func)
    return func


def key_str(dims, key):
    return " ".join(f"{d}={k}" for d, k in zip(dims, key))


def munge_docstring(func):
    """Prepare Result.description and Result.messages from ``func.__doc__``."""
    lines = getdoc(func).split("\n")
    return lines[0].rstrip("."), lines[2:]


class Result:
    """Container class for a check result and associated messages.

    Use ``str(result)`` for a complete, formatted description of the result.
    """

    #: 1-line description of the check.
    description: str

    #: Outcome of the check. Either 0 (PASS), 30 (WARNING), or 40 (FAIL).
    result: int

    #: Descriptive message when :attr:`result` is not PASS.
    message: str = ""

    def __init__(
        self, desc: str, result: int, message_or_lines: Union[str, Iterable[str]] = ""
    ):
        self.description = desc
        self.result = (
            {True: PASS, False: FAIL}.get(result, result)
            if isinstance(result, bool)
            else result
        )
        self.message = (
            message_or_lines
            if isinstance(message_or_lines, str)
            else "\n".join(message_or_lines)
        )

    def __bool__(self):
        return self.result is PASS

    def __str__(self):
        if self.result is PASS:
            return f"PASS {self.description}"
        else:
            result_str = {WARNING: "WARNING", FAIL: "FAIL"}.get(self.result)
            return f"{result_str} {self.description}" + (
                f":\n{self.message}" if self.message else ""
            )

    def __repr__(self):
        return str(self)


def check(scenario: Scenario, config: Optional[Dict] = None) -> List[Result]:
    """Check that data in `scenario` is consistent with the MESSAGE(-MACRO) formulation.

    :func:`check` applies multiple checks; see :ref:`the list of checks
    <checks-summary>`.

    Parameters
    ----------
    scenario :
        Scenario to be checked, possibly without a model solution.
    config : optional
        Configuration for :class:`~message_ix.Reporter`.

    Returns
    -------
    list of :class:`.Result`
        The first object is an "overall" result: PASS iff all the other checks PASS.
        Subsequent object are results for individual checks.

    Example
    -------
    >>> from message_ix.tools import check
    >>> results = check(scen)
    >>> print(" ".join(map(str, results))
    PASS Overall
    PASS var_cost missing for corresponding input/output
    PASS Data gaps in ``input`` along the year_act dimension
    PASS Data gaps in ``technical_lifetime`` along the year_vtg dimension
    PASS Non-integer values for ``technical_lifetime``

    """
    # Create a Reporter
    config = config or dict()
    rep = Reporter.from_scenario(scenario, solved=False, **config)

    # Apply each function to the reporter; collect names and keys for check results
    keys = [func(rep) for func in CHECKS]

    # Add a key that collects all check results
    rep.add("check all", keys)

    # Trigger all checks
    results = rep.get("check all")

    # Prepare an overall Result object that gives overall success or failure
    results.insert(0, Result("Overall", all(map(bool, results))))

    return results


# Individual checks


@append
def var_cost(rep):
    def _(vc, input, output):
        # TODO implement the check
        return Result("var_cost missing for corresponding input/output", PASS)

    key = {k: rep.full_key(k) for k in "var_cost input output".split()}
    return rep.add(
        "check var_cost",
        _,
        key["var_cost"],
        key["input"],
        key["output"],
    )


def check_gaps(qty, years, dim):
    """Check `qty` for gaps in data along `dim`."""
    result = PASS
    messages = []

    # List of dimensions other than `dim`
    dims = list(qty.dims)
    dims.pop(dims.index(dim))

    # Find the nulls in `qty`, then iterate over groups of `dims`
    for key, group in qty.isnull().groupby(dims):
        # print(key, group)

        # Set of years for which `qty` is not null, i.e. data exists
        seen = set()
        for idx, null in group.drop(dims).to_series().items():
            if not null:
                seen.add(idx)

        # Elements from `years` that don't appear in `seen`
        gaps = list(
            filter(lambda y: min(seen) < y < max(seen) and y not in seen, years)
        )

        if len(gaps):
            # At least 1 gap; format a message
            result = WARNING
            messages.extend(
                [
                    f"- at indices: {key_str(dims, key)}",
                    f"  for {dim}: {min(seen)} < {repr(gaps)} < {max(seen)}",
                ]
            )

    return Result(f"Data gaps in '{qty.name}'", result, messages)


@append
def gaps_input(rep):
    """Data gaps in ``input`` along the year_act dimension."""
    return rep.add(
        "check gaps in input", partial(check_gaps, dim="ya"), rep.full_key("input"), "y"
    )


@append
def gaps_tl(rep):
    """Data gaps in ``technical_lifetime`` along the year_vtg dimension."""
    return rep.add(
        "check gaps in technical_lifetime",
        partial(check_gaps, dim="yv"),
        rep.full_key("technical_lifetime"),
        "y",
    )


@append
def tl_integer(rep):
    """Non-integer values for ``technical_lifetime``.

    See https://github.com/iiasa/message_ix/issues/503.
    """

    def _(tl):
        # Quick check: convert all values to integer and look for changed values
        mask = tl.astype(int) != tl
        result = FAIL if mask.any() else PASS

        desc, messages = munge_docstring(tl_integer)

        # Process item-wise, only if there was some failure
        for key, non_int in mask.groupby(list(tl.dims)) if result is FAIL else ():
            if non_int.item():
                messages.append(f"- {tl.loc[key]} at indices: {key_str(tl.dims, key)}")

        return Result(desc, result, messages)

    return rep.add("check tl integer", _, rep.full_key("technical_lifetime"))


# @append
# def map_tec(rep):
#     def _(scen):
#         return Result("map_tec is present", FAIL, repr(scen.set("map_tec")))
#
#     return rep.add("map_tec", _, "scenario")
