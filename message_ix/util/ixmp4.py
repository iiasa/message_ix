from typing import Union

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
