from importlib import import_module
from warnings import warn

# Names formerly in this module, importable with deprecation warning.
_DEPRECATED_IMPORT = {
    "DIMS": "common",
    "Item": "common",
    "MACRO": "macro",
    "MESSAGE": "message",
    "MESSAGE_MACRO": "message_macro",
}


def __getattr__(name: str):
    try:
        submodule = "message_ix." + _DEPRECATED_IMPORT[name]
    except KeyError:
        raise AttributeError(name)

    warn(
        f"from message_ix.models import {name}\n"
        f"Instead, use:\n    from {submodule} import {name}",
        DeprecationWarning,
        stacklevel=2,
    )

    return getattr(import_module(submodule), name)
