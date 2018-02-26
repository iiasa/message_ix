import os
from message_ix import default_paths
import ixmp.model_settings as model_settings


model_file = os.path.join(default_paths.MODEL_DIR, '{model}_run.gms')
in_file = os.path.join(default_paths.DATA_DIR, 'MsgData_{case}.gdx')
out_file = os.path.join(default_paths.OUTPUT_DIR, 'MsgOutput_{case}.gdx')
iter_file = os.path.join(default_paths.OUTPUT_DIR,
                         'MsgIterationReport_{case}.gdx')
solve_args = '--in={inp} --out={outp} --iter=' + iter_file

for msg in ['MESSAGE', 'MESSAGE-MACRO']:
    model_settings.register_model(
            msg,
            model_settings.ModelConfig(model_file=model_file,
                                       inp=in_file,
                                       outp=out_file,
                                       args=solve_args)
        )
