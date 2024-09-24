from typing import Any, List, Optional, Tuple, Union

from pyam import IamDataFrame

try:
    from pyam.str import get_variable_components
except ImportError:  # Python < 3.10, pandas < 2.0
    from pyam.utils import get_variable_components

try:
    from typing import LiteralString
except ImportError:  # Python < 3.11
    from typing_extensions import LiteralString


def map_for_sankey(
    iam_df: IamDataFrame,
    year: int,
    region: str,
    exclude: List[Optional[str]] = [],
) -> dict[str, Tuple[Union[List, Any, LiteralString], Union[List, Any, LiteralString]]]:
    """Maps input to output flows to enable Sankey plots.

    Parameters
    ----------
    iam_df: :class:`pyam.IamDataframe`
        The IAMC-format DataFrame holding the data to plot as Sankey diagrams.
    year: int
        The year to display in the Sankey diagram.
    region: str
        The region to display in the Sankey diagram.
    exclude: list[str], optional
        If provided, exclude these keys from the Sankey diagram. Defaults to an empty
        list, i.e. showing all flows.

    Returns
    -------
    mapping: dict
        A mapping from variable names to their inputs and outputs.
    """
    return {
        var: get_source_and_target(var)
        for var in iam_df.filter(region=region + "*", year=year).variable
        if not exclude_flow(get_source_and_target(var), exclude)
    }


def get_source_and_target(
    variable: str,
) -> Tuple[Union[List, Any, LiteralString], Union[List, Any, LiteralString]]:
    """Get source and target for the `variable` flow."""
    start_idx, end_idx = set_start_and_end_index(variable)
    return (
        get_variable_components(variable, start_idx, join=True),
        get_variable_components(variable, end_idx, join=True),
    )


def set_start_and_end_index(variable: str) -> Tuple[List[int], List[int]]:
    """Get indices of source and target in variable name."""
    return (
        ([1, 2], [3, 4])
        if get_variable_components(variable, 0) == "in"
        else ([3, 4], [1, 2])
    )


def exclude_flow(
    flow: Tuple[Union[List, Any, LiteralString], Union[List, Any, LiteralString]],
    exclude: List[Optional[str]],
) -> bool:
    """Exclude sources or targets of variable flow if requested."""
    if flow[0] in exclude or flow[1] in exclude:
        return True
    return False
