from contextlib import nullcontext

import pytest


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
