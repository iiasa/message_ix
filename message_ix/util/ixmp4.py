from typing import Any, Literal, Union

import ixmp
import ixmp.backend


def on_ixmp4backend(obj: Union["ixmp.Platform", "ixmp.TimeSeries"]) -> bool:
    """:any:`True` if `ts` is stored on :class:`IXMP4Backend`.

    .. todo:: Move upstream, to :mod:`ixmp`.
    """
    if "ixmp4" not in ixmp.backend.available():
        return False

    from ixmp.backend.ixmp4 import IXMP4Backend

    return isinstance(
        (obj if isinstance(obj, ixmp.Platform) else obj.platform)._backend,
        IXMP4Backend,
    )


def add_or_extend_item_list(
    kwargs: dict[str, Any], key: Literal["equ_list", "var_list"], item_list: list[str]
) -> None:
    """Add `key` to `kwargs` and set it to or expand it with `item_list`."""
    if key not in kwargs:
        kwargs[key] = item_list
    else:
        kwargs[key].extend(item_list)
