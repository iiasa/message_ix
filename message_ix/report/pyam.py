from typing import TYPE_CHECKING, Optional, TypedDict

if TYPE_CHECKING:
    import pandas


class CollapseMessageColsKw(TypedDict, total=False):
    """Type hint for :class:`dict` of keyword args to :func:`collapse_message_cols`."""

    df: "pandas.DataFrame"
    var: Optional[str]
    kind: Optional[str]
    var_cols: list[str]


def collapse_message_cols(
    df: "pandas.DataFrame",
    var: Optional[str] = None,
    kind: Optional[str] = None,
    var_cols=[],
) -> "pandas.DataFrame":
    """:mod:`genno.compat.pyam` `collapse=...` callback for MESSAGEix quantities.

    Wraps :func:`~genno.compat.pyam.util.collapse` with arguments particular to
    MESSAGEix.

    Parameters
    ----------
    var : str
        Name for 'variable' column.
    kind : None or 'ene' or 'emi', optional
        Determines which other columns are combined into the 'region' and 'variable'
        columns:

        - 'ene': 'variable' is
          ``'<var>|<level>|<commodity>|<technology>|<mode>'`` and 'region' is
          ``'<region>|<node_dest>'`` (if `var='out'`) or
          ``'<region>|<node_origin>'`` (if `'var='in'`).
        - 'emi': 'variable' is ``'<var>|<emission>|<technology>|<mode>'``.
        - Otherwise: 'variable' is ``'<var>|<technology>'``.
    """
    from genno.compat.pyam import util

    columns = dict(variable=[var] if var else [])

    if kind == "ene":
        # Region column
        columns["region"] = ["nd" if var == "out" else "no"]
        columns["variable"].extend(["l", "c", "t", "m"])
    elif kind == "emi":
        columns["variable"].extend(["e", "t", "m"])
    else:
        columns["variable"].extend(["t"] + var_cols)

    return util.collapse(df, columns=columns, sep="|")
