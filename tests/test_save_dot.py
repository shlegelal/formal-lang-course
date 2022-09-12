import networkx as nx
from pathlib import Path

import pytest

from project import utils


def _check_build_and_save_dot_then_load_is_isomorphic(
    first_cycle_num: int,
    second_cycle_num: int,
    tmp_path: Path,
):
    path = (tmp_path / "test_graph.dot").as_posix()

    expected_graph = utils.build_and_save_labeled_two_cycles_graph_as_dot(
        first_cycle_num, "a", second_cycle_num, "b", path
    )

    actual_graph = nx.drawing.nx_pydot.read_dot(path)
    # Have to convert string node labels back to ints
    int_mapping = dict(map(lambda n: (n[0], int(n[0])), actual_graph.nodes))
    actual_graph = nx.relabel_nodes(actual_graph, int_mapping)

    assert nx.is_isomorphic(expected_graph, actual_graph)


class TestSaveDotThenLoadIsIsomorphic:
    def test_zero_to_zero(self, tmp_path: Path):
        with pytest.raises(ValueError):
            _check_build_and_save_dot_then_load_is_isomorphic(0, 0, tmp_path)

    def test_zero_to_many(self, tmp_path: Path):
        with pytest.raises(ValueError):
            _check_build_and_save_dot_then_load_is_isomorphic(0, 3, tmp_path)

    def test_many_to_zero(self, tmp_path: Path):
        with pytest.raises(ValueError):
            _check_build_and_save_dot_then_load_is_isomorphic(3, 0, tmp_path)

    def test_one_to_one(self, tmp_path: Path):
        _check_build_and_save_dot_then_load_is_isomorphic(1, 1, tmp_path)

    def test_many_to_many(self, tmp_path: Path):
        _check_build_and_save_dot_then_load_is_isomorphic(10, 10, tmp_path)


class TestDotContents:
    def test_saved_contents_are_correct(self, tmp_path: Path):
        path = (tmp_path / "test_graph.dot").as_posix()

        utils.build_and_save_labeled_two_cycles_graph_as_dot(2, "a", 2, "b", path)

        with open(path, "r") as f:
            contents = f.read()
            assert (
                contents == "digraph  {"
                "1;2;0;3;4;"
                "1 -> 2  [key=0, label=a];"
                "2 -> 0  [key=0, label=a];"
                "0 -> 1  [key=0, label=a];"
                "0 -> 3  [key=0, label=b];"
                "3 -> 4  [key=0, label=b];"
                "4 -> 0  [key=0, label=b];"
                "}"
            )
