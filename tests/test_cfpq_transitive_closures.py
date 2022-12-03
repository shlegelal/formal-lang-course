import pytest
import networkx as nx
from pyformlang import cfg as c

from project.cfpq.hellings import constrained_transitive_closure_by_hellings
from project.cfpq.matrix import constrained_transitive_closure_by_matrix
from project.cfpq.tensor import constrained_transitive_closure_by_tensor
from testing_utils import load_test_data
from testing_utils import load_test_ids
from testing_utils import dot_str_to_graph


@pytest.mark.parametrize(
    "graph, cfg, expected",
    load_test_data(
        "TestCfpqConstrainedTransitiveClosures",
        lambda d: (
            dot_str_to_graph(d["graph"]),
            c.CFG.from_text(d["cfg"]),
            {
                (triple["start"], c.Variable(triple["variable"]), triple["end"])
                for triple in d["expected"]
            },
        ),
    ),
    ids=load_test_ids("TestCfpqConstrainedTransitiveClosures"),
)
class TestCfpqConstrainedTransitiveClosures:
    def test_hellings(self, graph: nx.Graph, cfg: c.CFG, expected: set[tuple]):
        actual = constrained_transitive_closure_by_hellings(graph, cfg)

        assert actual == expected

    def test_matrix(self, graph: nx.Graph, cfg: c.CFG, expected: set[tuple]):
        actual = constrained_transitive_closure_by_matrix(graph, cfg)

        assert actual == expected

    def test_tensor(self, graph: nx.Graph, cfg: c.CFG, expected: set[tuple]):
        actual = constrained_transitive_closure_by_tensor(graph, cfg)

        assert actual == expected
