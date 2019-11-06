import logging

from ixmp.model import MODELS

from .core import Scenario  # noqa: F401
# TODO also import MACRO (once it is created)
from .models import MESSAGE, MESSAGE_MACRO

# Register models with ixmp core
# MODELS['MACRO'] = MACRO
MODELS['MESSAGE'] = MESSAGE
MODELS['MESSAGE-MACRO'] = MESSAGE_MACRO


__version__ = MESSAGE.read_version()

log = logging.getLogger(__name__)
