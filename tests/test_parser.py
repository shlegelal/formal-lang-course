import pytest
from pathlib import Path

from test_utils import load_test_res
from project.interpretator.parser import check, save_to_dot, parse


@pytest.mark.parametrize(
    "text, is_correct", map(lambda r: (r[0], r[1]), load_test_res("test_check"))
)
def test_check(text: str, is_correct: bool):
    assert check(text) == is_correct


# @pytest.mark.parametrize(
#     "text, expected", map(lambda r: (r[0], r[1]), load_test_res("test_save_dot"))
# )
# def test_save_dot(text: str, expected: str, tmp_path: Path):
#     path = tmp_path / "test_grammar.dot"
#     parser = parse(text)
#     save_to_dot(parser, str(path))
#     with open(path, "r") as f:
#         actual = f.read()
#         assert actual == expected
