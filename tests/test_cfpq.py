import networkx as nx
import pytest

from project.cfpq import cfpq
from testing_utils import dot_str_to_graph
from testing_utils import load_test_data
from testing_utils import load_test_ids


@pytest.mark.parametrize(
    "graph, query, start_nodes, final_nodes, start_var, expected",
    load_test_data(
        "test_cfpq_by_hellings",
        lambda d: (
            dot_str_to_graph(d["graph"]),
            d["query"],
            d["start_nodes"],
            d["final_nodes"],
            d["start_var"] if d["start_var"] is not None else "S",
            {tuple(pair) for pair in d["expected"]},
        ),
    ),
    ids=load_test_ids("test_cfpq_by_hellings"),
)
def test_cfpq_by_hellings(
    graph: nx.Graph,
    query: str,
    start_nodes: set | None,
    final_nodes: set | None,
    start_var: str,
    expected: set[tuple],
):
    actual = cfpq.cfpq_by_hellings(graph, query, start_nodes, final_nodes, start_var)

    assert actual == expected
