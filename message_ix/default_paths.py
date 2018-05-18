import os

fullpath = lambda *x: os.path.abspath(os.path.join(*x))

HERE = os.path.dirname(os.path.realpath(__file__))

CONFIG_PATH = fullpath(os.path.expanduser(
    '~', '.local', 'message_ix', 'config.json'))

if not os.path.exists(CONFIG_PATH):
    LOCAL_DIR = HERE
else:
    with open(CONFIG_PATH) as f:
        data = json.load(f)
        LOCAL_DIR = data['LOCAL_DIR']

ROOT_DIR = fullpath(LOCAL_DIR)
MODEL_DIR = fullpath(ROOT_DIR, 'model')
DATA_DIR = fullpath(ROOT_DIR, 'model', 'data')
OUTPUT_DIR = fullpath(ROOT_DIR, 'model', 'output')
