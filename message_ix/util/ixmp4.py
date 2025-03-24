from typing import Any, Literal


def add_or_extend_item_list(
    kwargs: dict[str, Any], key: Literal["equ_list", "var_list"], item_list: list[str]
) -> None:
    """Add `key` to `kwargs` and set it to or expand it with `item_list`."""
    if key not in kwargs:
        kwargs[key] = item_list
    else:
        kwargs[key].extend(item_list)
