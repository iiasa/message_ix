from typing import Any, Optional

import pandas as pd

try:
    from pyam.str import get_variable_components as gvc
except ImportError:  # Python < 3.10, pandas < 2.0
    from pyam.utils import get_variable_components as gvc


def sankey_mapper(
    df: pd.DataFrame,
    year: int,
    region: str,
    exclude: list[Optional[str]] = [],
) -> dict[str, Any]:
    mapping = {}

    for var in df.filter(region=region + "*", year=year).variable:
        is_input = gvc(var, 0) == "in"
        (start_idx, end_idx) = ([1, 2], [3, 4]) if is_input else ([3, 4], [1, 2])
        source = gvc(var, start_idx, join=True)
        target = gvc(var, end_idx, join=True)
        if source in exclude or target in exclude:
            continue
        mapping[var] = (source, target)

    return mapping
