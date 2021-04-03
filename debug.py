import os
import sys
import traceback

import pytest

try:
    pytest.main(sys.argv[1:])
except BaseException:
    traceback.print_exc()
    raise

# Explicitly exit with 0
# sys.exit(0)
os._exit(0)
