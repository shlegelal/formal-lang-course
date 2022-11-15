import pytest
import networkx as nx
from pyformlang import cfg as c

from project.cfpq.hellings import constrained_transitive_closure_by_hellings
from testing_utils import load_test_data
from testing_utils import load_test_ids
from testing_utils import dot_str_to_graph


@pytest.mark.parametrize(
    "graph, cfg, expected",
    load_test_data(
        "test_constrained_transitive_closure_by_hellings",
        lambda d: (
            dot_str_to_graph(d["graph"]),
            c.CFG.from_text(d["cfg"]),
            {
                (triple["start"], c.Variable(triple["variable"]), triple["end"])
                for triple in d["expected"]
            },
        ),
    ),
    ids=load_test_ids("test_constrained_transitive_closure_by_hellings"),
)
def test_constrained_transitive_closure_by_hellings(
    graph: nx.Graph, cfg: c.CFG, expected: set[tuple]
):
    actual = constrained_transitive_closure_by_hellings(graph, cfg)

    assert actual == expected
