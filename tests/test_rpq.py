import pytest
import networkx as nx

from project import rpq
from testing_utils import load_test_data
from testing_utils import dot_str_to_graph


@pytest.mark.parametrize(
    "graph, query, starts, finals, expected",
    load_test_data(
        "test_rpq_by_tensor",
        lambda d: (
            dot_str_to_graph(d["graph"]),
            d["query"],
            d["starts"],
            d["finals"],
            {tuple(pair) for pair in d["expected"]},
        ),
    ),
)
def test_rpq_by_tensor(
    graph: nx.Graph,
    query: str,
    starts: set | None,
    finals: set | None,
    expected: set[tuple],
):
    actual = rpq.rpq_by_tensor(graph, query, starts, finals)

    assert actual == expected


@pytest.mark.parametrize(
    "graph, query, starts, finals, expected",
    load_test_data(
        "test_rpq_by_tensor",
        lambda d: (
            dot_str_to_graph(d["graph"]),
            d["query"],
            d["starts"],
            d["finals"],
            {end for _, end in d["expected"]},
        ),
    ),
)
def test_rpq_by_bfs_for_all(
    graph: nx.Graph,
    query: str,
    starts: set | None,
    finals: set | None,
    expected: set,
):
    actual = rpq.rpq_by_bfs(graph, query, starts, finals)

    assert actual == expected


@pytest.mark.parametrize(
    "graph, query, starts, finals, expected",
    load_test_data(
        "test_rpq_by_tensor",
        lambda d: (
            dot_str_to_graph(d["graph"]),
            d["query"],
            d["starts"],
            d["finals"],
            {tuple(pair) for pair in d["expected"]},
        ),
    ),
)
def test_rpq_by_bfs_for_each(
    graph: nx.Graph,
    query: str,
    starts: set | None,
    finals: set | None,
    expected: set[tuple],
):
    actual = rpq.rpq_by_bfs(
        graph, query, starts, finals, mode=rpq.BfsMode.FIND_REACHABLE_FOR_EACH_START
    )

    assert actual == expected
