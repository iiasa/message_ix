import logging
from pathlib import Path

try:
    from importlib.metadata import PackageNotFoundError, version
except ImportError:  # Python 3.7
    from importlib_metadata import PackageNotFoundError, version  # type: ignore

from ixmp import ModelError, config
from ixmp.model import MODELS

from .core import Scenario
from .models import MACRO, MESSAGE, MESSAGE_MACRO
from .reporting import Reporter
from .util import make_df

__all__ = [
    "MACRO",
    "MESSAGE",
    "MESSAGE_MACRO",
    "MODELS",
    "ModelError",
    "Reporter",
    "Scenario",
    "config",
    "make_df",
]

try:
    __version__ = version(__name__)
except PackageNotFoundError:  # pragma: no cover
    # Package is not installed
    __version__ = "999"

# Register configuration keys with ixmp core and set default
config.register("message model dir", Path, Path(__file__).parent / "model")
config.register("message solve options", dict)

# Register models with ixmp core
MODELS["MACRO"] = MACRO
MODELS["MESSAGE"] = MESSAGE
MODELS["MESSAGE-MACRO"] = MESSAGE_MACRO

# Create the top-level logger
log = logging.getLogger(__name__)
