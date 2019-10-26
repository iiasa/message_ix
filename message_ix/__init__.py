import logging

from ixmp.model import MODELS

from .core import (  # noqa: F401
    DEFAULT_SOLVE_OPTIONS,
    Scenario,
)
from .models import MESSAGE, MESSAGE_MACRO

# Register models with ixmp core
MODELS['MESSAGE'] = MESSAGE
MODELS['MESSAGE-MACRO'] = MESSAGE_MACRO


__version__ = MESSAGE.read_version()

log = logging.getLogger(__name__)
