import sys
import pytest
import traceback

try:
    pytest.main(sys.argv[1:])
except BaseException:
    traceback.print_exc()
    raise
