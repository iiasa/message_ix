import pytest

from message_ix.models import MESSAGE_MACRO, gams_release


def test_gams_release():
    result = gams_release().split('.')
    assert len(result) == 3 and result[0] >= '24'


def test_message_macro():
    # Constructor runs successfully
    MESSAGE_MACRO()

    class _MM(MESSAGE_MACRO):
        """Dummy subclass requiring a non-existent GAMS version."""
        GAMS_min_version = '99.9.9'

    # Constructor complains about an insufficient GAMS version
    with pytest.raises(RuntimeError, match="MESSAGE-MACRO requires GAMS >= "
                       "99.9.9; found "):
        _MM()
