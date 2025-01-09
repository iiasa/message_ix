import logging
from typing import TYPE_CHECKING

try:
    from pyam.str import get_variable_components
except ImportError:  # Python < 3.10 → pyam-iamc < 3
    from pyam.utils import get_variable_components


if TYPE_CHECKING:
    import pyam

log = logging.getLogger(__name__)


def exclude_flow(flow: tuple[str, str], exclude: list[str]) -> bool:
    """Return :any:`True` if either the source or target of `flow` is in `exclude`."""
    return flow[0] in exclude or flow[1] in exclude


def get_source_and_target(variable: str) -> tuple[str, str]:
    """Get source and target for the `variable` flow."""
    start_idx, end_idx = get_start_and_end_index(variable)
    return (
        get_variable_components(variable, start_idx, join=True),
        get_variable_components(variable, end_idx, join=True),
    )


def get_start_and_end_index(variable: str) -> tuple[list[int], list[int]]:
    """Get indices of source and target in variable name."""
    return (
        ([1, 2], [3, 4])
        if get_variable_components(variable, 0) == "in"
        else ([3, 4], [1, 2])
    )


def map_for_sankey(
    iam_df: "pyam.IamDataFrame", node: str, exclude: list[str] = []
) -> dict[str, tuple[str, str]]:
    """Maps input to output flows to enable Sankey diagram.

    Parameters
    ----------
    iam_df : :class:`pyam.IamDataframe`
        Data to plot as Sankey diagram.
    node : str
        The node (MESSAGEix) or region (pyam) to plot.
    exclude : list[str], optional
        Flows to omit from the diagram. By default, nothing is excluded.

    Returns
    -------
    dict
        mapping from variable names to 2-tuples of their (inputs, output) flows.
    """
    result = {
        var: get_source_and_target(var)
        for var in iam_df.filter(region=node + "*").variable
        if not exclude_flow(get_source_and_target(var), exclude)
    }

    if not result:
        log.warning(
            f"No mapping entries generated for {node=}, {exclude=} and data:\n"
            + repr(iam_df)
        )

    return result
