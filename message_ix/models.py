from collections import ChainMap
from copy import copy
from pathlib import Path
import re

from ixmp import config
from ixmp.model.gams import GAMSModel


#: Solver options used by :meth:`message_ix.Scenario.solve`.
DEFAULT_CPLEX_OPTIONS = {
    'advind': 0,
    'lpmethod': 2,
    'threads': 4,
    'epopt': 1e-6,
}


def _template(*parts):
    """Helper to make a template string relative to model_dir."""
    return str(Path('{model_dir}', *parts))


class MESSAGE(GAMSModel):
    name = 'MESSAGE'

    #: Default model options.
    defaults = ChainMap({
        # New keys for MESSAGE
        'model_dir': Path(__file__).parent / 'model',
        # Update keys from GAMSModel
        'model_file': _template('{model_name}_run.gms'),
        'in_file': _template('data', 'MsgData_{case}.gdx'),
        'out_file': _template('output', 'MsgOutput_{case}.gdx'),
        'solve_args': [
            '--in="{in_file}"',
            '--out="{out_file}"',
            '--iter="{}"'.format(
                _template('output', 'MsgIterationReport_{case}.gdx')),
            ],
    }, GAMSModel.defaults)

    @classmethod
    def read_version(cls):
        """Retrieve MESSAGE version string from version.gms."""
        version_file = Path(config.get('message model dir'), 'version.gms')
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
        model_options.setdefault('model_dir', config.get('message model dir'))
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
        optfile = self.model_dir / 'cplex.opt'
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

    #: MESSAGE-MACRO uses the GAMS ``break;`` statement, and thus requires GAMS
    #: 24.8.1 or later.
    GAMS_min_version = '24.8.1'

    def __init__(self, *args, **kwargs):
        version = gams_release()
        if version < self.GAMS_min_version:
            message = ('{0.name} requires GAMS >= {0.GAMS_min_version}; '
                       'found {1}').format(self, version)
            raise RuntimeError(message)

        super().__init__(*args, **kwargs)


def gams_release():
    """Return the GAMS release as a string, e.g. '24.7.4'."""
    # TODO move this upstream to ixmp.model.gams
    # NB check_output(['gams'], ...) does not work, because GAMS writes
    #    directly to the console instead of to stdout.
    #    check_output(['gams', '-LogOption=3'], ...) does not work, because
    #    GAMS does not accept options without an input file to execute.
    import os
    from tempfile import mkdtemp
    from subprocess import check_output

    # Create a temporary GAMS program that does nothing
    tmp_dir = Path(mkdtemp())
    gms = tmp_dir / 'null.gms'
    gms.write_text('$exit;')

    # Execute, capturing stdout
    output = check_output(
        ['gams', 'null', '-LogOption=3'],
        shell=os.name == 'nt',
        cwd=tmp_dir,
        universal_newlines=True)

    # Clean up
    gms.unlink()
    gms.with_suffix('.lst').unlink()
    tmp_dir.rmdir()

    # Find and return the version string
    pattern = r'^GAMS ([\d\.]+)\s*Copyright'
    return re.search(pattern, output, re.MULTILINE).groups()[0]
