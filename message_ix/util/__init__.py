import copy
import warnings
from collections import ChainMap, defaultdict
from collections.abc import Mapping

import pandas as pd
from pandas.api.types import is_scalar

from message_ix.macro import MACRO_ITEMS
from message_ix.models import MESSAGE_ITEMS


def make_df(name, **data):
    """Return a data frame for parameter `name` filled with `data`.

    :func:`make_df` always returns a data frame with the columns required by
    :meth:`.add_par`: the dimensions of the parameter `name`, plus 'value' and
    'unit'. Columns not listed in `data` are left empty.

    Examples
    --------
    >>> make_df(
    ...    "demand", node=["foo", "bar"], commodity="baz", value=[1.2, 3.4]
    ... )
      node commodity level  year  time  value  unit
    0  foo       baz  None  None  None    1.2  None
    1  bar       baz  None  None  None    3.4  None

    Code that uses the deprecated signature:

    >>> base = {"year": [2020, 2021, 2022]}
    >>> make_df(base, value=1., unit="y")
       year  value unit
    0     1    1.0    y
    1     2    1.0    y
    2     3    1.0    y

    can either be adjusted to use the new signature:

    >>> make_df("duration_period", **base, value=1., unit="y")

    or, emulated using the built-in pandas method :meth:`~.DataFrame.assign`:

    >>> pd.DataFrame(base).assign(value=1., unit="y")

    The former is recommended, because it will ensure the result has the correct
    columns for the parameter.

    Parameters
    ----------
    name : str
        Name of a parameter listed in :data:`MESSAGE_ITEMS` or
        :data:`MACRO_ITEMS`.
    data : optional
        Contents for dimensions of the parameter, its 'value', or 'unit'.
        Other keys are ignored.

    Returns
    -------
    pandas.DataFrame

    Raises
    ------
    ValueError
        if `name` is not the name of a MESSAGE or MACRO parameter; if arrays in
        `data` have uneven lengths.
    """
    if isinstance(name, (Mapping, pd.Series, pd.DataFrame)):
        return _deprecated_make_df(name, **data)

    # Get parameter information
    try:
        info = ChainMap(MESSAGE_ITEMS, MACRO_ITEMS)[name]
    except KeyError:
        raise ValueError(f"{repr(name)} is not a MESSAGE or MACRO parameter")

    if info["ix_type"] != "par":
        raise ValueError(f"{repr(name)} is {info['ix_type']}, not par")

    # Index names, if not given explicitly, are the same as the index sets
    idx_names = info.get("idx_names", info["idx_sets"])

    # Columns for the resulting data frame
    columns = list(idx_names) + ["value", "unit"]

    # Default values for every column
    data = ChainMap(data, defaultdict(lambda: None))

    # Arguments for pd.DataFrame constructor
    args = dict(data={})

    # Flag if all values in `data` are scalars
    all_scalar = True

    for column in columns:
        # Update flag
        all_scalar &= is_scalar(data[column])
        # Store data
        args["data"][column] = data[column]

    if all_scalar:
        # All values are scalars, so the constructor requires an index to be
        # passed explicitly.
        args["index"] = [0]

    return pd.DataFrame(**args)


def _deprecated_make_df(base, **kwargs):
    """Extend or overwrite *base* with new values from *kwargs*.

    .. deprecated:: 3.2

       - For MESSAGE and MACRO parameters, use :meth:`make_df`.
       - To manipulate other dictionaries, use :meth:`dict.update`.
       - To add or overwrite columns in a data frame, use
         :meth:`pandas.DataFrame.assign`.

    Parameters
    ----------
    base : dict, :class:`pandas.Series`, or :class:`pandas.DataFrame`
        Existing dataset to append to.
    **kwargs:
        Additional values to append to *base*.

    Returns
    -------
    pandas.DataFrame
        *base* modified with *kwargs*.

    Examples
    --------
    Scalar values in *base* or *kwargs* are broadcast. The number of rows in
    the returned :class:`pandas.DataFrame` equals the length of the longest
    item in either argument.

    >>> base = {'foo': 'bar'}
    >>> make_df(base, baz=[42, 43, 44])
       foo  baz
    0  bar  42
    1  bar  43
    2  bar  44
    """
    warnings.warn(
        "make_df() with a mapping or pandas object. Use make_df(), "
        "DataFrame.from_dict(), and/or DataFrame.assign().",
        DeprecationWarning,
    )

    base = copy.deepcopy(base)
    if not isinstance(base, Mapping):
        base = base.to_dict()
    base.update(**kwargs)
    return pd.DataFrame(base)
