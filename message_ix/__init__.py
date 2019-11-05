import logging
from pathlib import Path

from ixmp import config
from ixmp.model import MODELS

from .core import Scenario  # noqa: F401
from .models import MESSAGE, MESSAGE_MACRO


__all__ = [
    'MESSAGE',
    'MESSAGE_MACRO',
    'MODELS',
    'Scenario',
    'config',
]

# Register configuration keys with ixmp core and set default
config.register('message model dir', Path, Path(__file__).parent / 'model')


# Register models with ixmp core
MODELS['MESSAGE'] = MESSAGE
MODELS['MESSAGE-MACRO'] = MESSAGE_MACRO


__version__ = MESSAGE.read_version()

log = logging.getLogger(__name__)
