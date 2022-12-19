import pytest
from pathlib import Path

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


@pytest.mark.parametrize(
    "inp, expected_contents",
    load_test_data(
        "test_save_parse_tree_as_dot", lambda d: (d["input"], d["expected"])
    ),
    ids=load_test_ids("test_save_parse_tree_as_dot"),
)
def test_save_parse_tree_as_dot(inp: str, expected_contents: str, tmp_path: Path):
    path = tmp_path / "test_grammar.dot"
    parsing.save_parse_tree_as_dot(inp, path)
    with open(path, "r") as f:
        contents = f.read()
        assert contents == expected_contents
