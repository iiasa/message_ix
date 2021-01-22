import logging
from pathlib import Path

from ixmp import config
from ixmp.model import MODELS
from pkg_resources import DistributionNotFound, get_distribution

from .core import Scenario
from .models import MACRO, MESSAGE, MESSAGE_MACRO
from .reporting import Reporter
from .util import make_df

__all__ = [
    "MACRO",
    "MESSAGE",
    "MESSAGE_MACRO",
    "MODELS",
    "Scenario",
    "Reporter",
    "config",
    "make_df",
]

try:
    __version__ = get_distribution(__name__).version
except DistributionNotFound:
    # Package is not installed
    __version__ = "999"

# Register configuration keys with ixmp core and set default
config.register("message model dir", Path, Path(__file__).parent / "model")

# Register models with ixmp core
MODELS["MACRO"] = MACRO
MODELS["MESSAGE"] = MESSAGE
MODELS["MESSAGE-MACRO"] = MESSAGE_MACRO

# Create the top-level logger
log = logging.getLogger(__name__)
