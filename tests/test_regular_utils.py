from networkx import MultiDiGraph
from pyformlang.regular_expression import Regex
import pytest

from load_test_res import load_test_res
from project.utils.graph_utils import generate_labeled_two_cycles_graph
from project.utils.regular_utils import tensor_rpq, bfs_rpq
from test_automata_utils import build_graph_by_srt


@pytest.mark.parametrize(
    "query, start_states, final_states, expected",
    map(
        lambda res: (
                res[0],
                set(res[1]) if len(res[1]) else None,
                set(res[2]) if len(res[2]) else None,
                set(map(tuple, res[3])),
        ),
        load_test_res("test_rpq_labeled_two_cycles_graph_query"),
    ),
)
@pytest.mark.parametrize(
    "graph",
    map(
        lambda res: generate_labeled_two_cycles_graph(res[0], res[1]),
        load_test_res("test_rpq_labeled_two_cycles_graph"),
    ),
)
def test_tensor_rpq_labeled_two_cycles_graph(
        graph: MultiDiGraph,
        query: str,
        start_states: set | None,
        final_states: set | None,
        expected: set,
):
    assert tensor_rpq(graph, Regex(query), start_states, final_states) == expected


@pytest.mark.parametrize("query", load_test_res("test_rpq_empty_graph_query"))
def test_tensor_rpq_empty_graph(query: str):
    assert tensor_rpq(MultiDiGraph(), Regex(query), None, None) == set()


@pytest.mark.parametrize(
    "graph, query, starts, finals, expected",
    map(
        lambda res: (
                build_graph_by_srt(res[0]),
                res[1],
                set(res[2]) if len(res[2]) else None,
                set(res[3]) if len(res[3]) else None,
                set(map(tuple, res[4]))
        ),
        load_test_res("test_bst_rpq"),
    ),
)
def test_tensor_rpq_labeled_two_cycles_graph(
        graph: MultiDiGraph,
        query: str,
        starts: set | None,
        finals: set | None,
        expected: set,
):
    actual = tensor_rpq(graph, Regex(query), starts, finals)
    assert actual == expected


@pytest.mark.parametrize(
    "graph, query, starts, finals, res",
    map(
        lambda res: (
                build_graph_by_srt(res[0]),
                res[1],
                set(res[2]) if len(res[2]) else None,
                set(res[3]) if len(res[3]) else None,
                res[4],

        ),
        load_test_res("test_bst_rpq"),
    ),
)
@pytest.mark.parametrize(
    "separated",
    [False, True]
)
def test_rpq_by_bfs(
        graph: MultiDiGraph,
        query: str,
        starts: set | None,
        finals: set | None,
        separated: bool,
        res: list,
):
    actual = bfs_rpq(graph, Regex(query), starts, finals, separated)
    expected = set(map(tuple, res)) if separated else set(map(lambda r: r[1], res))
    assert actual == expected


@pytest.mark.parametrize(
    "query, starts, finals, res",
    map(
        lambda res: (
                res[0],
                set(res[1]) if len(res[1]) else None,
                set(res[2]) if len(res[2]) else None,
                set(map(tuple, res[3])),
        ),
        load_test_res("test_rpq_labeled_two_cycles_graph_query"),
    ),
)
@pytest.mark.parametrize(
    "separated",
    [False, True]
)
@pytest.mark.parametrize(
    "graph",
    map(
        lambda res: generate_labeled_two_cycles_graph(res[0], res[1]),
        load_test_res("test_rpq_labeled_two_cycles_graph"),
    ),
)
def test_bfs_rpq_labeled_two_cycles_graph(
        graph: MultiDiGraph,
        query: str,
        starts: set | None,
        finals: set | None,
        res: set,
        separated: bool,
):
    actual = bfs_rpq(graph, Regex(query), starts, finals, separated)
    expected = set(map(tuple, res)) if separated else set(map(lambda r: r[1], res))
    assert actual == expected
