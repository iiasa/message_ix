import collections
import copy

import pandas as pd


def make_df(base, **kwargs):
    """Extend or overwrite *base* with new values from *kwargs*.

    Parameters
    ----------
    base : dict, :class:`pandas.Series`, or :class:`pandas.DataFrame`
        Existing dataset to append to.
    **kwargs:
        Additional values to append to *base*.

    Returns
    -------
    :class:`pandas.DataFrame`
        *base* modified with *kwargs*.

    Examples
    --------
    Scalar values in *base* or *kwargs* are broadcast. The number of rows in
    the returned :class:`pandas.DataFrame` equals the length of the longest
    item in either argument.

    >>> base = {'foo': 'bar'}
    >>> make_df(base, baz=[42, 43, 44])
        foo	baz
    0	bar	42
    1	bar	43
    2	bar	44

    """
    if not isinstance(base, (collections.Mapping, pd.Series, pd.DataFrame)):
        raise ValueError('base argument must be a dictionary or Pandas object')
    base = copy.deepcopy(base)
    if not isinstance(base, collections.Mapping):
        base = base.to_dict()
    base.update(**kwargs)
    return pd.DataFrame(base)
