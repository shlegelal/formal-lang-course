import pytest
import networkx as nx

from project.rpq import rpq
from testing_utils import load_test_data
from testing_utils import dot_str_to_graph


@pytest.mark.parametrize(
    "graph, query, starts, finals, expected",
    map(
        lambda data: (
            dot_str_to_graph(data[0]),
            data[1],
            data[2],
            data[3],
            {tuple(pair) for pair in data[4]},
        ),
        load_test_data("test_rpq"),
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
