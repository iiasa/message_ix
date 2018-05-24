import json
import os


DEFAULT_MODEL_PATH = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), 'model')

CONFIG_PATH = os.path.expanduser(os.path.join(
    '~', '.local', 'message_ix', 'config.json'))


def model_path():
    if not os.path.exists(CONFIG_PATH):
        return DEFAULT_MODEL_PATH

    with open(CONFIG_PATH, mode='r') as f:
        data = json.load(f)

    if 'MODEL_PATH' not in data:
        return DEFAULT_MODEL_PATH

    return data['MODEL_PATH']


def data_path():
    return os.path.join(model_path(), 'data')


def output_path():
    return os.path.join(model_path(), 'output')
