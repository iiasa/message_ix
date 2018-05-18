import os
from message_ix import default_paths
import ixmp.model_settings as model_settings


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
                                   args=' '.join(solve_args))
    )
