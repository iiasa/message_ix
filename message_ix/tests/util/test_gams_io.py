import pandas as pd
from ixmp import Platform
from ixmp.util.ixmp4 import ContainerData
from pytest import FixtureRequest

from message_ix import Scenario
from message_ix.testing import make_westeros
from message_ix.util.gams_io import (
    add_auxiliary_items_to_container_data_list,
    add_default_data_to_container_data_list,
    store_message_version,
)
from message_ix.util.scenario_data import HELPER_INDEXSETS, HELPER_TABLES


def test_store_message_version() -> None:
    data: list[ContainerData] = []
    store_message_version(container_data=data)
    expected_names = ["version_part", "MESSAGE_ix_version"]
    for index, item in enumerate(data):
        assert item.name == expected_names[index]


def test_add_default_data_to_container_data_list(test_mp: Platform) -> None:
    scenario = Scenario(mp=test_mp, model="model", scenario="scenario", version="new")

    # Test with empty 'technology' set
    data: list[ContainerData] = []

    for name in ("cat_tec", "type_tec_land"):
        add_default_data_to_container_data_list(
            container_data=data, name=name, scenario=scenario
        )
    expected = [
        pd.DataFrame(columns=["type_tec", "technology"]),
        pd.DataFrame({"type_tec": ["all"]}),
    ]

    # Add some test data
    scenario.add_set(name="type_tec", key="foo")
    scenario.add_set(name="technology", key="bar")
    scenario.add_set(name="type_tec_land", key={"type_tec": ["foo"]})

    for name2 in ("cat_tec", "type_tec_land"):
        add_default_data_to_container_data_list(
            container_data=data, name=name2, scenario=scenario
        )

    # Assert new and default data are merged correctly
    expected.extend(
        [
            pd.DataFrame({"type_tec": ["all"], "technology": ["bar"]}),
            pd.DataFrame({"type_tec": ["foo", "all"]}),
        ]
    )

    for index, item in enumerate(data):
        assert isinstance(item.records, pd.DataFrame)
        pd.testing.assert_frame_equal(item.records, expected[index])


# TODO Why is this test slower for IXMP4Backend?
def test_add_auxiliary_items_to_container_data_list(
    test_mp: Platform, request: FixtureRequest
) -> None:
    scenario = make_westeros(mp=test_mp, emissions=True, solve=False, request=request)
    data: list[ContainerData] = []

    add_auxiliary_items_to_container_data_list(container_data=data, scenario=scenario)

    # Test the container data list contains all helper items listed in scenario_data
    expected = HELPER_INDEXSETS.copy()
    expected.extend(HELPER_TABLES)

    # TODO Iterating over 34 items here, but how to do this faster? Is it sufficient to
    # compare len()?
    for index, item in enumerate(data):
        assert item.name == expected[index].name
