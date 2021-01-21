from message_ix.testing import make_austria


def test_make_austria(test_mp):
    make_austria(test_mp, solve=False)

    # commented: this is tested via austria_load_scenario.ipynb
    # scenario = make_austria(test_mp, solve=True)
