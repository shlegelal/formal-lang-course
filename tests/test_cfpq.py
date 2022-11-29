import networkx as nx
import pytest
import pyformlang.cfg as c

from load_test_res import load_test_res
from project.grammar.cfpq import (
    helling_constrained_transitive_closure,
    helling_cfpq,
    matrix_constrained_transitive_closure,
    matrix_cfpq,
    tensor_cfpq,
)
from test_automata_utils import build_graph_by_srt


@pytest.mark.parametrize(
    "graph, cfg, expected",
    map(
        lambda r: (
            build_graph_by_srt(r[0]),
            c.CFG.from_text(r[1]),
            {
                (triple["start"], c.Variable(triple["variable"]), triple["end"])
                for triple in r[2]
            },
        ),
        load_test_res("test_constrained_transitive_closure"),
    ),
)
@pytest.mark.parametrize(
    "ctc",
    [helling_constrained_transitive_closure, matrix_constrained_transitive_closure],
)
def test_constrained_transitive(graph, cfg, expected, ctc):
    actual = ctc(graph, cfg)

    assert actual == expected


@pytest.mark.parametrize(
    "graph, query, start_states, final_states, start, expected",
    map(
        lambda r: (
            build_graph_by_srt(r[0]),
            c.CFG.from_text(r[1]),
            r[2],
            r[3],
            r[4] if r[4] is not None else "S",
            {tuple(pair) for pair in r[5]},
        ),
        load_test_res("test_helling"),
    ),
)
@pytest.mark.parametrize("cfpq", [helling_cfpq, matrix_cfpq, tensor_cfpq])
def test_cfpq(
    graph: nx.Graph,
    query: c.CFG,
    start_states: set | None,
    final_states: set | None,
    start: str,
    expected: set[tuple],
    cfpq,
):
    actual = cfpq(graph, query, start_states, final_states, start)

    assert actual == expected
