from pathlib import Path


DEFAULT_MODEL_PATH = Path(__file__).parent / 'model'
CONFIG_PATH = Path('~', '.local', 'message_ix', 'config.json').expanduser()
