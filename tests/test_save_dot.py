from pathlib import Path

import networkx as nx
import pytest

from project.utils import graph_utils
from testing_utils import load_test_data
from testing_utils import load_test_ids


def _check_build_and_save_dot_then_load_is_isomorphic(
    first_cycle_num: int,
    second_cycle_num: int,
    tmp_path: Path,
):
    path = (tmp_path / "test_graph.dot").as_posix()

    expected_graph = graph_utils.build_and_save_labeled_two_cycles_graph_as_dot(
        first_cycle_num, "a", second_cycle_num, "b", path
    )

    actual_graph = nx.drawing.nx_pydot.read_dot(path)
    # Convert string node labels back to ints
    int_mapping = dict(map(lambda n: (n, int(n)), actual_graph.nodes))
    actual_graph = nx.relabel_nodes(actual_graph, int_mapping)

    assert nx.is_isomorphic(
        actual_graph,
        expected_graph,
        node_match=dict.__eq__,
        edge_match=nx.isomorphism.categorical_edge_match("label", None),
    )


class TestSaveDotThenLoadIsIsomorphic:
    @pytest.mark.parametrize(
        "first_cycle_num, second_cycle_num",
        load_test_data(
            "TestSaveDotThenLoadIsIsomorphic.test_zero_nodes_produces_value_error",
            lambda d: (d["first_cycle_num"], d["second_cycle_num"]),
        ),
        ids=load_test_ids(
            "TestSaveDotThenLoadIsIsomorphic.test_zero_nodes_produces_value_error"
        ),
    )
    def test_zero_nodes_produces_value_error(
        self, first_cycle_num: int, second_cycle_num: int, tmp_path: Path
    ):
        with pytest.raises(ValueError):
            _check_build_and_save_dot_then_load_is_isomorphic(
                first_cycle_num, second_cycle_num, tmp_path
            )

    @pytest.mark.parametrize(
        "first_cycle_num, second_cycle_num",
        load_test_data(
            "TestSaveDotThenLoadIsIsomorphic.test_saved_and_loaded_is_isomorphic",
            lambda d: (d["first_cycle_num"], d["second_cycle_num"]),
        ),
        ids=load_test_ids(
            "TestSaveDotThenLoadIsIsomorphic.test_saved_and_loaded_is_isomorphic"
        ),
    )
    def test_saved_and_loaded_is_isomorphic(
        self, first_cycle_num: int, second_cycle_num: int, tmp_path: Path
    ):
        _check_build_and_save_dot_then_load_is_isomorphic(
            first_cycle_num,
            second_cycle_num,
            tmp_path,
        )


class TestDotContents:
    @pytest.mark.parametrize(
        "first_cycle_num, second_cycle_num, expected_contents",
        load_test_data(
            "TestDotContents.test_saved_contents_are_correct",
            lambda d: (
                d["first_cycle_num"],
                d["second_cycle_num"],
                d["expected_contents"],
            ),
        ),
        ids=load_test_ids("TestDotContents.test_saved_contents_are_correct"),
    )
    def test_saved_contents_are_correct(
        self,
        first_cycle_num: int,
        second_cycle_num: int,
        expected_contents: str,
        tmp_path: Path,
    ):
        path = (tmp_path / "test_graph.dot").as_posix()

        graph_utils.build_and_save_labeled_two_cycles_graph_as_dot(
            first_cycle_num, "a", second_cycle_num, "b", path
        )

        with open(path, "r") as f:
            contents = f.read()
            assert contents == expected_contents
