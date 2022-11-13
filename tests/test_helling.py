import networkx as nx
import pytest
import pyformlang.cfg as c

from load_test_res import load_test_res
from project.grammar.helling import helling, constrained_transitive_closure
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
def test_constrained_transitive(graph, cfg, expected):
    actual = constrained_transitive_closure(graph, cfg)

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
def test_helling(
    graph: nx.Graph,
    query: c.CFG,
    start_states: set | None,
    final_states: set | None,
    start: str,
    expected: set[tuple],
):
    actual = helling(graph, query, start_states, final_states, start)

    assert actual == expected
