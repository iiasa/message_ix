import os
import re

import ixmp.model_settings as model_settings

from . import default_paths
from .core import (  # noqa: F401
    DEFAULT_SOLVE_OPTIONS,
    Scenario,
)


model_file = os.path.join(default_paths.model_path(), '{model}_run.gms')
in_file = os.path.join(default_paths.data_path(), 'MsgData_{case}.gdx')
out_file = os.path.join(default_paths.output_path(), 'MsgOutput_{case}.gdx')
iter_file = os.path.join(default_paths.output_path(),
                         'MsgIterationReport_{case}.gdx')
solve_args = ['--in="{inp}"', '--out="{outp}"', '--iter="' + iter_file + '"']

for msg in ['MESSAGE', 'MESSAGE-MACRO']:
    model_settings.register_model(
        msg,
        model_settings.ModelConfig(model_file='"{}"'.format(model_file),
                                   inp=in_file,
                                   outp=out_file,
                                   args=solve_args)
    )


# retrieve MESSAGEix version number from model/version.gms
fname = os.path.join(default_paths.model_path(), 'version.gms')
fname = fname if os.path.exists(fname) else \
    os.path.join(os.path.dirname(os.path.realpath(__file__)),
                 'model', 'version.gms')  # only exists here on install
with open(fname) as f:
    s = str(f.readlines())

__version__ = '{}.{}.{}'.format(
    re.search('VERSION_MAJOR "(.+?)"', s).group(1),
    re.search('VERSION_MINOR "(.+?)"', s).group(1),
    re.search('VERSION_PATCH "(.+?)"', s).group(1),
)
