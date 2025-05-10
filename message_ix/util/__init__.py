import copy
import re
import warnings
from collections import ChainMap, defaultdict
from collections.abc import Mapping
from pathlib import Path
from typing import TYPE_CHECKING, Optional

import pandas as pd
from ixmp.backend import ItemType
from pandas.api.types import is_scalar

from message_ix.models import MACRO, MESSAGE

if TYPE_CHECKING:
    from message_ix.core import Scenario


def copy_model(
    path: Path,
    overwrite: bool = False,
    set_default: bool = False,
    quiet: bool = False,
    *,
    source_dir: Optional[Path] = None,
) -> None:
    """Copy the MESSAGE GAMS files to a new `path`.

    Parameters
    ----------
    overwrite : bool
        If :any:`True`, overwrite existing files.
    set_default : bool
        If :any:`True`, update the ixmp configuration setting "message model dir".
    quiet : bool
        If :any:`False`, print actions to stdout; otherwise display nothing.
    source_dir : Path, optional
        If given, copy model files from this directory instead of the main one.
    """
    from shutil import copyfile

    import ixmp

    import message_ix

    path = Path(path).resolve()

    if quiet:

        def output(str):
            pass

    else:
        output = print

    src_dir = (
        source_dir
        if source_dir
        else Path(message_ix.__file__).resolve().parent.joinpath("model")
    )

    def _exclude_path(p: Path) -> bool:
        # Skip certain files
        if p.suffix in (".gdx", ".log", ".lst") or re.search("225[a-z]+", str(p)):
            return False
        return True

    paths = filter(_exclude_path, list(src_dir.rglob("*")))

    # Iterate over pre-filtered paths in `src_dir`
    for original_path in paths:
        # Construct the destination path
        dst = path / original_path.relative_to(src_dir)

        # Create parent directory
        dst.parent.mkdir(parents=True, exist_ok=True)

        if original_path.is_dir():
            # No further action for directories
            continue

        # Display output
        if dst.exists():
            if not overwrite:
                output(f"{dst} exists, will not overwrite")

                # Skip copyfile() below
                continue
            else:
                output(f"Overwrite {dst}")
        else:
            output(f"Copy to {dst}")

        copyfile(original_path, dst)

    if set_default:
        ixmp.config.set("message model dir", path)
        ixmp.config.save()


def make_df(name, **data):
    """Return a data frame for parameter or indexed set `name` filled with `data`.

    :func:`make_df` always returns a data frame with the columns required by either:

    - :meth:`.add_par`: the dimensions of the parameter `name`, plus 'value' and 'unit'.
    - :meth:`.add_set`: the dimensions of the indexed set `name`.

    Columns not listed in `data` are left empty.

    The `data` keyword arguments can be passed in many ways; see the
    :ref:`python:tut-keywordargs` and “Function Examples” sections of the Python
    introductory tutorial, or the examples below.

    Examples
    --------

    >>> make_df(
    ...    "demand", node=["foo", "bar"], commodity="baz", value=[1.2, 3.4]
    ... )
      node  commodity  level  year  time  value  unit
    0  foo        baz   None  None  None    1.2  None
    1  bar        baz   None  None  None    3.4  None

    Pass some values as direct keyword arguments, and others by unpacking a dictionary:

    >>> common = dict(
    ...    commodity="light",
    ...    level="useful",
    ...    time="year",
    ...    unit="GWa",
    ... )
    >>> make_df(
    ...    "demand",
    ...    node=["Westeros", "Middle-earth"],
    ...    year=[680, 700],
    ...    value=[50, 80],
    ...    # Use values from `common` as additional keyword args:
    ...    **common,
    ... )
               node  commodity   level  year  time  value  unit
    0      Westeros      light  useful   680  year     50   GWa
    1  Middle-earth      light  useful   700  year     50   GWa

    Code that uses the deprecated signature, such as:

    >>> base = {"year": [2020, 2021, 2022]}
    >>> make_df(base, value=1., unit="y")
       year  value  unit
    0     1    1.0     y
    1     2    1.0     y
    2     3    1.0     y

    or:

    >>> base = dict(
    ...    node=["Westeros", "Middle-earth"],
    ...    year=[680, 700],
    ...    time="year",
    ...    unit="-",
    ... )
    >>> make_df(base, mode="standard")
               node  year  time  unit      mode
    0      Westeros   680  year     -  standard
    1  Middle-earth   700  year     -  standard

    …can either be adjusted to use the new signature:

    >>> make_df("duration_period", **base, value=1., unit="y")

    or, emulated using the :meth:`pandas.DataFrame.assign` method:

    >>> pd.DataFrame(base).assign(value=1., unit="y")

    The former is recommended, because it will ensure the result has the correct columns
    for the parameter.

    Parameters
    ----------
    name : str
        Name of a parameter listed in :attr:`.MESSAGE.items` or :attr:`.MACRO.items`.
    data : optional
        Contents for dimensions of the parameter, its 'value', or 'unit'. Other keys are
        ignored.

    Returns
    -------
    pandas.DataFrame

    Raises
    ------
    ValueError
        if `name` is not the name of a MESSAGE or MACRO parameter; if arrays in `data`
        have uneven lengths.
    """
    if isinstance(name, (Mapping, pd.Series, pd.DataFrame)):
        return _deprecated_make_df(name, **data)

    # Get item information
    try:
        info = ChainMap(MESSAGE.items, MACRO.items)[name]
    except KeyError:
        raise ValueError(f"{repr(name)} is not a MESSAGE or MACRO parameter")

    # Index names, if not given explicitly, are the same as the index sets
    dims = info.dims or info.coords

    # Columns for the resulting data frame
    columns = list(dims) + (["value", "unit"] if info.type == ItemType.PAR else [])

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


def expand_dims(scenario: "Scenario", name, **data):
    """Expand dimensions of parameter `name` on `scenario`, filling with `data`.

    This function is for use when an existing parameter `name` has dimensions that are a
    subset of those that would be created by :func:`make_df`, i.e. those given by
    :attr:`.MESSAGE.items`.

    This can occur when the underlying structure of MESSAGE and the model core is
    enhanced by adding dimensions to existing parameters. Existing scenario data in
    users' databases can not then be automatically updated.

    :func:`expand_dims` helps users to update this data manually. It:

    1. Retrieves the existing parameter data for `name`.
    2. Passes this existing data, plus any `data` given as keyword arguments, to
       :func:`make_df`. The result must be a data frame with no empty values; in other
       words, `data` must include all the dimensions to be added to `name`.
    3. Re-initializes the parameter `name` on `scenario`, with the dimensions given by
       :attr:`.MESSAGE.items`.
    4. Adds the expanded data.

    The modifications (steps 3 and 4) are wrapped using :meth:`.transact`.
    """
    # NB could be improved by allowing `data` to include callables; these would be
    #    pd.DataFrame.apply(…)'d to each row in order to compute values for the new
    #    dimension(s).

    # Create the expanded data
    new_data = make_df(name, **scenario.par(name), **data)
    assert not new_data.isna().any(axis=None), "Expanded data are incomplete"

    with scenario.transact(f"expand_dims({name}, …)"):
        # Remove the parameter entirely, and re-initialize
        scenario.remove_par(name)
        MESSAGE.initialize_items(scenario, {name: MESSAGE.items[name].to_dict()})

        # Add the expanded data
        scenario.add_par(name, new_data)
