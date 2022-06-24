from datetime import datetime
from typing import Dict

import pytest
from pydantic import BaseModel, Field

from rath.json.encoders import dumps


class TestInput(BaseModel):
    start_time: datetime = Field(alias="startTime")
    some_dict: Dict[str, float] = Field(alias="someDict")


@pytest.fixture
def example_input():
    return TestInput(
        startTime=datetime.utcnow(),
        someDict={
            "a": 1.0,
            "b": 2.0,
        },
    )


def test_json_dumps(example_input):
    """
    Tests that extended json dumps() method does not throw exception when
    serializing a pydantic model
    :param example_input: Example pydantic model.
    """
    dumps(example_input)


def test_json_dumps_throws_for_unknown_type():
    """
    Tests that extended json dumps() method still raises TypeError for unknown type
    """
    with pytest.raises(TypeError):
        dumps(bytes([0x01, 0x02, 0x03, 0x04, 0x05, 0x06]))


def test_json_roundtrip(example_input):
    """
    Tests that extended json dumps() method produces output
    that matches input on a round trip
    :param example_input: Example pydantic model.
    """
    json_string = dumps(example_input)
    round_trip = TestInput.parse_raw(json_string)
    assert example_input == round_trip
