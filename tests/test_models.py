from message_ix.models import gams_release


def test_gams_release():
    result = gams_release().split('.')
    assert len(result) == 3 and result[0] >= '24'
