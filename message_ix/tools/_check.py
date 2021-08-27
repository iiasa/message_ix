from functools import partial
from inspect import getdoc
from logging import ERROR as FAIL
from logging import NOTSET as PASS
from logging import WARNING
from typing import Any, Dict, Iterable, Tuple, Union

from message_ix.reporting import Reporter

CHECKS = []


def append(func):
    CHECKS.append(func)
    return func


class Result:
    """Container class for a check result and associated messages."""

    description: str
    result: int
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
            return f"{result_str} {self.description}:\n{self.message}"

    def __repr__(self):
        return str(self)


def check(scenario, config=None) -> Dict[str, Tuple[bool, Any]]:
    """Check that data in `scenario` is consistent with the MESSAGE(-MACRO) formulation.

    :func:`check` applies multiple checks, including:

    1. ``technical_lifetime`` (maybe also ``var_cost`` missing for corresponding with
       ``input``/``output`` values.
    2. Period “gaps” in data.

    Other checks that could be added include:
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


def key_str(dims, key):
    return " ".join(f"{d}={k}" for d, k in zip(dims, key))


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
    return rep.add(
        "check gaps in input", partial(check_gaps, dim="ya"), rep.full_key("input"), "y"
    )


@append
def gaps_tl(rep):
    return rep.add(
        "check gaps in technical_lifetime",
        partial(check_gaps, dim="yv"),
        rep.full_key("technical_lifetime"),
        "y",
    )


def munge_docstring(func):
    """Prepare Result.description and Result.messages from ``func.__doc__``."""
    lines = getdoc(func).split("\n")
    return lines[0].rstrip("."), lines[2:]


@append
def tl_integer(rep):
    """Non-integer values for technical_lifetime.

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
def map_tec(rep):
    def _(scen):
        return Result("map_tec is present", FAIL, repr(scen.set("map_tec")))

    return rep.add("map_tec", _, "scenario")
