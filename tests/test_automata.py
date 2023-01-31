import pytest

from test_utils import load_test_res, is_isomorphic_fa_and_graph
from project.utils.graph import get_graph_by_dot
from project.utils.automata import *


# @pytest.mark.parametrize(
#     "regex, expected_dfa",
#     map(
#         lambda res: (res[0], build_graph_by_srt(res[1])),
#         load_test_res("test_build_dfa_by_regex"),
#     ),
# )
# def test_build_dfa_by_regex(regex: str, expected_dfa: MultiDiGraph):
#     assert is_isomorphic_fa_and_graph(build_dfa_by_regex(Regex(regex)), expected_dfa)


@pytest.mark.parametrize(
    "graph, start_states, final_states, expected_graph",
    map(
        lambda res: (
            get_graph_by_dot(res[0]),
            set(res[1]),
            set(res[2]),
            get_graph_by_dot(res[3]),
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
    actual_nfa = nfa_by_graph(graph, start_states, final_states)
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
    actual_nfa = nfa_by_graph(expected_graph)
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
            get_graph_by_dot(res[0]),
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
        actual_nfa = nfa_by_graph(graph, start_states, final_states)
        assert is_isomorphic_fa_and_graph(actual_nfa, MultiDiGraph())
    except AutomataUtilsError:
        assert True
