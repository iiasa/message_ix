from collections import ChainMap
from copy import copy, deepcopy
from pathlib import Path
import re

from ixmp import config
import ixmp.model.gams

from .macro import MACRO_ITEMS


#: Solver options used by :meth:`message_ix.Scenario.solve`.
DEFAULT_CPLEX_OPTIONS = {
    'advind': 0,
    'lpmethod': 2,
    'threads': 4,
    'epopt': 1e-6,
}

# Common indices for some parameters in MESSAGE_ITEMS
_idx_common = ['node', 'technology', 'level', 'commodity', 'year', 'time']

# NB only a partial list; see https://github.com/iiasa/message_ix/issues/254
#: List of ixmp items for MESSAGE.
MESSAGE_ITEMS = {
    # Index sets
    # Storage level
    'level_storage': dict(ix_type='set'),
    # Storage reservoir technology
    'storage_tec': dict(ix_type='set'),

    # Mapping set: mapping of storage reservoir to charger/discharger
    'map_tec_storage': dict(ix_type='set',
                            idx_sets=['node', 'technology', 'storage_tec',
                                      'level', 'commodity']),

    # Parameters
    # Order of sub-annual time steps
    'time_order': dict(ix_type='par', idx_sets=['lvl_temporal', 'time']),
    # Initial amount of storage
    'storage_initial': dict(ix_type='par', idx_sets=_idx_common),
    # Storage losses as a percentage of installed capacity
    'storage_self_discharge': dict(ix_type='par', idx_sets=_idx_common),
}


def _template(*parts):
    """Helper to make a template string relative to model_dir."""
    return str(Path('{model_dir}', *parts))


class GAMSModel(ixmp.model.gams.GAMSModel):
    """Extended :class:`ixmp.model.gams.GAMSModel` for MESSAGE & MACRO."""
    #: Default model options.
    defaults = ChainMap({
        # New keys for MESSAGE & MACRO
        'model_dir': Path(__file__).parent / 'model',

        # Override keys from GAMSModel
        'model_file': _template('{model_name}_run.gms'),
        'in_file': _template('data', 'MsgData_{case}.gdx'),
        'out_file': _template('output', 'MsgOutput_{case}.gdx'),
        'solve_args': [
            '--in="{in_file}"',
            '--out="{out_file}"',
            '--iter="{}"'.format(
                _template('output', 'MsgIterationReport_{case}.gdx')),
            ],

        # Disable the feature to put input/output GDX files, list files, etc.
        # in a temporary directory
        'use_temp_dir': False,
    }, ixmp.model.gams.GAMSModel.defaults)

    @classmethod
    def initialize(cls, scenario):
        """Set up *scenario* with required sets and parameters for MESSAGE.

        See Also
        --------
        :data:`MESSAGE_ITEMS`
        """
        # Initialize the ixmp items
        cls.initialize_items(scenario, MESSAGE_ITEMS)

    def __init__(self, name=None, **model_options):
        # Update the default options with any user-provided options
        model_options.setdefault('model_dir', config.get('message model dir'))
        self.cplex_opts = copy(DEFAULT_CPLEX_OPTIONS)
        self.cplex_opts.update(model_options.pop('solve_options', {}))

        super().__init__(name, **model_options)

    def run(self, scenario):
        """Execute the model.

        GAMSModel creates a file named ``cplex.opt`` in the model directory
        containing the options in :obj:`DEFAULT_CPLEX_OPTIONS`, or any
        overrides passed to :meth:`~message_ix.Scenario.solve`.

        .. warning:: GAMSModel can solve Scenarios in two or more Python
           processes simultaneously; but using *different* CPLEX options in
           each process may produced unexpected results.
        """
        # If two runs are kicked off simulatenously with the same
        # self.model_dir, then they will try to write the same optfile, and may
        # write different contents.
        #
        # TODO Re-enable the 'use_temp_dir' feature from ixmp.GAMSModel
        #      (disabled above). Then cplex.opt will be specific to that
        #      directory.

        # Write CPLEX options into an options file
        optfile = self.model_dir / 'cplex.opt'
        lines = ('{} = {}'.format(*kv) for kv in self.cplex_opts.items())
        optfile.write_text('\n'.join(lines))

        try:
            result = super().run(scenario)
        finally:
            # Remove the optfile regardless of whether the run completed
            # without error. The file may have been removed already by another
            # run (in a separate process) that completed before this one.
            # py37 compat: check for existence instead of using
            # unlink(missing_ok=True)
            if optfile.exists():
                optfile.unlink()

        return result


class MESSAGE(GAMSModel):
    """Model class for MESSAGE."""
    name = 'MESSAGE'


class MACRO(GAMSModel):
    """Model class for MACRO."""
    name = 'MACRO'

    #: MACRO uses the GAMS ``break;`` statement, and thus requires GAMS 24.8.1
    #: or later.
    GAMS_min_version = '24.8.1'

    def __init__(self, *args, **kwargs):
        version = gams_release()
        if version < self.GAMS_min_version:
            message = ('{0.name} requires GAMS >= {0.GAMS_min_version}; '
                       'found {1}').format(self, version)
            raise RuntimeError(message)

        super().__init__(*args, **kwargs)

    @classmethod
    def initialize(cls, scenario, with_data=False):
        """Initialize the model structure."""
        # NB some scenarios already have these items. This method simply adds
        #    any missing items.

        # FIXME the Java code under the JDBCBackend (ixmp_source) refuses to
        #       initialize these items with specified idx_sets—even if the
        #       sets are correct.
        items = deepcopy(MACRO_ITEMS)
        for name in 'C', 'COST_NODAL', 'COST_NODAL_NET', 'DEMAND', 'GDP', 'I':
            items[name].pop('idx_sets')

        # Initialize the ixmp items
        cls.initialize_items(scenario, items)


class MESSAGE_MACRO(MACRO):
    """Model class for MESSAGE_MACRO."""
    name = 'MESSAGE-MACRO'

    def __init__(self, *args, **kwargs):
        # Remove M-M iteration options from kwargs and convert to GAMS
        # command-line options
        mm_iter_args = []
        for name in 'convergence_criterion', 'max_adjustment', 'max_iteration':
            try:
                mm_iter_args.append(f'--{name.upper()}={kwargs.pop(name)}')
            except KeyError:
                continue

        # Let the parent constructor handle other solve_args
        super().__init__(*args, **kwargs)

        # Append to the prepared solve_args
        self.solve_args.extend(mm_iter_args)


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
