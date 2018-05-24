import argparse

from message_ix.config import config


def config_cli():
    parser = argparse.ArgumentParser()
    model_path = 'Copy model files to a new path and configure MESSAGEix to use those files.'
    parser.add_argument('--model_path', help=model_path, default=None)
    overwrite = 'Overwrite existing files.'
    parser.add_argument('--overwrite', help=overwrite, action='store_true')
    args = parser.parse_args()
    config(model_path=args.model_path, overwrite=args.overwrite)
