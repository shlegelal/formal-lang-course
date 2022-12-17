import pytest

from project.litegql import parsing
from testing_utils import load_test_data
from testing_utils import load_test_ids


@pytest.mark.parametrize(
    "inp, is_correct",
    load_test_data("test_check", lambda d: (d["input"], d["is_correct"])),
    ids=load_test_ids("test_check"),
)
def test_check(inp: str, is_correct: bool):
    assert parsing.check(inp) == is_correct
