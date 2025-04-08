from message_ix.util.ixmp4 import add_or_extend_item_list


def test_add_or_extend_item_list() -> None:
    test_dict = {"equ_list": ["foo", "bar"]}

    # Test adding to existing key extends
    add_or_extend_item_list(kwargs=test_dict, key="equ_list", item_list=["baz"])
    expected = test_dict.copy()
    expected["equ_list"] = ["foo", "bar", "baz"]
    assert test_dict == expected

    # Test adding to new key adds the key
    add_or_extend_item_list(kwargs=test_dict, key="var_list", item_list=["foo"])
    expected["var_list"] = ["foo"]
    assert test_dict == expected
