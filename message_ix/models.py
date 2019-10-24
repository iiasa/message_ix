from collections import ChainMap
from pathlib import Path
import re

from ixmp.model.gams import GAMSModel

from message_ix import default_paths as dp


model_file = Path(dp.model_path(), '{model_name}_run.gms')
in_file = Path(dp.data_path(), 'MsgData_{case}.gdx')
out_file = Path(dp.output_path(), 'MsgOutput_{case}.gdx')
iter_file = Path(dp.output_path(), 'MsgIterationReport_{case}.gdx')


class MESSAGE(GAMSModel):
    name = 'MESSAGE'

    #: Default model options.
    defaults = ChainMap({
        'model_file': str(model_file),
        'in_file': str(in_file),
        'out_file': str(out_file),
        'solve_args': [
            '--in="{in_file}"',
            '--out="{out_file}"',
            '--iter="{}"'.format(iter_file),
            ],
    }, GAMSModel.defaults)

    @classmethod
    def read_version(cls):
        """Retrieve MESSAGE version string from version.gms."""
        version_file = Path(dp.model_path(), 'version.gms')
        if not version_file.exists():
            # Only exists here on install
            version_file = Path(__file__).parent / 'model' / 'version.gms'

        s = version_file.read_text()

        return '{}.{}.{}'.format(
            re.search('VERSION_MAJOR "(.+?)"', s).group(1),
            re.search('VERSION_MINOR "(.+?)"', s).group(1),
            re.search('VERSION_PATCH "(.+?)"', s).group(1),
        )


class MESSAGE_MACRO(MESSAGE):
    name = 'MESSAGE-MACRO'
