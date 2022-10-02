import pydot
import pytest

from load_test_res import load_test_res
from networkx import is_isomorphic, isomorphism
from pyformlang.finite_automaton import FiniteAutomaton

from project.utils.automata_utils import *
from project.utils.regular_utils import rpq


def build_graph_by_srt(s: str) -> MultiDiGraph:
    return drawing.nx_pydot.from_pydot(pydot.graph_from_dot_data(s)[0])


def is_isomorphic_fa_and_graph(fa: FiniteAutomaton, graph: MultiDiGraph) -> bool:
    fa_graph = fa.to_networkx()
    # Remove nodes extra added by pyformlang
    for node in list(fa_graph):
        if isinstance(node, str) and node.endswith("_starting"):
            fa_graph.remove_node(node)
    # Convert string to bool from dot file
    for _, data in fa_graph.nodes.data():
        if data["is_start"] in ("True", "False"):
            data["is_start"] = data["is_start"] == "True"
        if data["is_final"] in ("True", "False"):
            data["is_final"] = data["is_final"] == "True"

    return is_isomorphic(
        fa_graph,
        graph,
        edge_match=isomorphism.categorical_edge_match("label", None),
    )


@pytest.mark.parametrize(
    "redex, expected_dfa",
    map(
        lambda res: (res[0], build_graph_by_srt(res[1])),
        load_test_res("test_build_dfa_by_redex"),
    ),
)
def test_build_dfa_by_redex(redex: str, expected_dfa: MultiDiGraph):
    assert is_isomorphic_fa_and_graph(build_dfa_by_redex(Regex(redex)), expected_dfa)


@pytest.mark.parametrize(
    "graph, start_states, final_states, expected_graph",
    map(
        lambda res: (
            build_graph_by_srt(res[0]),
            set(res[1]),
            set(res[2]),
            build_graph_by_srt(res[3]),
        ),
        load_test_res("test_build_nfa_by_graph"),
    ),
)
def test_build_nfa_by_graph(
    graph: MultiDiGraph,
    start_states: set | None,
    final_states: set | None,
    expected_graph: MultiDiGraph,
):
    actual_nfa = build_nfa_by_graph(graph, start_states, final_states)
    assert is_isomorphic_fa_and_graph(actual_nfa, expected_graph)


@pytest.mark.parametrize(
    "first_cycle_num, second_cycle_num",
    map(
        lambda res: (res[0], res[1]),
        load_test_res("test_build_nfa_by_labeled_two_cycles_graph"),
    ),
)
def test_build_nfa_by_labeled_two_cycles_graph(
    first_cycle_num: int, second_cycle_num: int
):
    expected_graph = generate_labeled_two_cycles_graph(
        (first_cycle_num, second_cycle_num), ("a", "b")
    )
    actual_nfa = build_nfa_by_graph(expected_graph)
    assert is_isomorphic_fa_and_graph(actual_nfa, expected_graph)


# @pytest.mark.parametrize("graph_name", load_test_res("test_build_nfa_by_dataset_graph"))
# def test_build_nfa_by_dataset_graph(graph_name: str):
#     expected_graph = get_graph(graph_name)
#     actual_nfa = build_nfa_by_graph(expected_graph)
#     assert is_isomorphic_fa_and_graph(actual_nfa, expected_graph)


@pytest.mark.parametrize(
    "graph, start_states, final_states",
    map(
        lambda res: (
            build_graph_by_srt(res[0]),
            set(res[1]),
            set(res[2]),
        ),
        load_test_res("test_build_nfa_by_graph_with_automata_utils_error"),
    ),
)
def test_build_nfa_by_graph_with_automata_utils_error(
    graph: MultiDiGraph,
    start_states: set | None,
    final_states: set | None,
):
    try:
        actual_nfa = build_nfa_by_graph(graph, start_states, final_states)
        assert is_isomorphic_fa_and_graph(actual_nfa, MultiDiGraph())
    except AutomataUtilsError:
        assert True


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
def test_rpq_labeled_two_cycles_graph(
    graph: MultiDiGraph,
    query: str,
    start_states: set | None,
    final_states: set | None,
    expected: set,
):
    assert rpq(graph, Regex(query), start_states, final_states) == expected


@pytest.mark.parametrize("query", load_test_res("test_rpq_empty_graph_query"))
def test_rpq_empty_graph(query: str):
    assert rpq(MultiDiGraph(), Regex(query), None, None) == set()
