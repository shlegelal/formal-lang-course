import pytest
import networkx as nx

from project.rpq import rpq
from testing_utils import load_test_data
from testing_utils import dot_str_to_graph


@pytest.mark.parametrize(
    "graph, query, starts, finals, expected",
    load_test_data(
        "test_rpq",
        lambda d: (
            dot_str_to_graph(d["graph"]),
            d["query"],
            d["starts"],
            d["finals"],
            {tuple(pair) for pair in d["expected"]},
        ),
    ),
)
def test_rpq(
    graph: nx.Graph,
    query: str,
    starts: set | None,
    finals: set | None,
    expected: set[tuple],
):
    actual = rpq(graph, query, starts, finals)

    assert actual == expected
