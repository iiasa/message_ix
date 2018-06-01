import os


DEFAULT_MODEL_PATH = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), 'model')

CONFIG_PATH = os.path.expanduser(os.path.join(
    '~', '.local', 'message_ix', 'config.json'))
