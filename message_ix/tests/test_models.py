from contextlib import nullcontext
from typing import TYPE_CHECKING

import pytest

from message_ix.message import shift_period
from message_ix.testing import make_dantzig

if TYPE_CHECKING:
    from ixmp import Platform


@pytest.mark.parametrize(
    "name",
    (
        "DIMS",
        "Item",
        "MACRO",
        "MESSAGE",
        "MESSAGE_MACRO",
        pytest.param("FOO", marks=pytest.mark.xfail(raises=AttributeError)),
    ),
)
def test_deprecated_import(name: str) -> None:
    import message_ix.models

    ctx = (
        nullcontext()
        if name == "FOO"
        else pytest.warns(
            DeprecationWarning, match=f"from message_ix.models import {name}"
        )
    )

    with ctx:
        getattr(message_ix.models, name)


@pytest.mark.parametrize(
    "y0",
    (
        # Not implemented: shifting to an earlier period
        pytest.param(1962, marks=pytest.mark.xfail(raises=NotImplementedError)),
        # Does nothing
        1963,
        # Not implemented with ixmp.JDBCBackend
        pytest.param(1964, marks=pytest.mark.xfail(raises=NotImplementedError)),
        pytest.param(1965, marks=pytest.mark.xfail(raises=NotImplementedError)),
    ),
)
def test_shift_period(test_mp: "Platform", y0: int) -> None:
    s = make_dantzig(test_mp, solve=True, multi_year=True)

    shift_period(s, y0)
