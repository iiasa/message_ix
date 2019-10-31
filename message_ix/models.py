from collections import ChainMap
from copy import copy
from pathlib import Path
import re

from ixmp.model.gams import GAMSModel

from message_ix import default_paths as dp


model_file = Path(dp.model_path(), '{model_name}_run.gms')
in_file = Path(dp.data_path(), 'MsgData_{case}.gdx')
out_file = Path(dp.output_path(), 'MsgOutput_{case}.gdx')
iter_file = Path(dp.output_path(), 'MsgIterationReport_{case}.gdx')

#: Solver options used by :meth:`message_ix.Scenario.solve`.
DEFAULT_CPLEX_OPTIONS = {
    'advind': 0,
    'lpmethod': 2,
    'threads': 4,
    'epopt': 1e-6,
}


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

    def __init__(self, name=None, **model_options):
        # Update the default options with any user-provided options
        self.cplex_opts = copy(DEFAULT_CPLEX_OPTIONS)
        self.cplex_opts.update(model_options.pop('solve_options', {}))

        super().__init__(name, **model_options)

    def run(self, scenario):
        """Execute the model.

        :class:`MESSAGE` creates a file named ``cplex.opt`` in the model
        directory, containing the options in :obj:`DEFAULT_CPLEX_OPTIONS`,
        or any overrides passed to :meth:`~message_ix.Scenario.solve`.
        """
        # This is not safe against race conditions; if two runs are kicked off
        # simulatenously with the same dp.model_path, then they will try to
        # write/unlink the same optfile.
        #
        # TODO enhance GAMSModel (in ixmp) to run GAMS in a temporary
        #      directory, copying source and GDX files if needed. Then the
        #      cplex.opt file will be specific to that directory.

        # Write CPLEX options into an options file
        optfile = dp.model_path() / 'cplex.opt'
        lines = ('{} = {}'.format(*kv) for kv in self.cplex_opts.items())
        optfile.write_text('\n'.join(lines))

        try:
            result = super().run(scenario)
        finally:
            # Remove the optfile regardless of whether the run completed
            # without error
            optfile.unlink()

        return result


class MESSAGE_MACRO(MESSAGE):
    name = 'MESSAGE-MACRO'
