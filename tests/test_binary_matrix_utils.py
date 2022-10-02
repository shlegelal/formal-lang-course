import pytest
from pyformlang.finite_automaton import NondeterministicFiniteAutomaton, State
from scipy.sparse import dok_matrix

from project.utils.binary_matrix_utils import (
    build_bm_by_nfa,
    build_nfa_by_bm,
    intersect,
    transitive_closure,
)
from load_test_res import load_test_res


def nfa(
    transitions_list: list[tuple], start_states: set = None, final_states: set = None
) -> NondeterministicFiniteAutomaton:
    res = NondeterministicFiniteAutomaton()

    if not len(transitions_list):
        return res

    res.add_transitions(transitions_list)
    for state in start_states:
        res.add_start_state(State(state))
    for state in final_states:
        res.add_final_state(State(state))

    return res


def test_build_empty():
    nfa_1 = build_nfa_by_bm(build_bm_by_nfa(nfa([])))

    assert nfa_1.is_empty()


@pytest.mark.parametrize(
    "nfa_1",
    map(
        lambda res: (nfa(res[0], res[1], res[2])),
        load_test_res("test_intersect"),
    ),
)
def test_intersect_with_empty(nfa_1: NondeterministicFiniteAutomaton):
    bm = build_bm_by_nfa(nfa_1)
    empty_bm = build_bm_by_nfa(nfa([]))

    intersection = build_nfa_by_bm(intersect(bm, empty_bm))

    assert intersection.is_empty()


@pytest.mark.parametrize(
    "l_nfa",
    map(
        lambda res: nfa(res[0], res[1], res[2]),
        load_test_res("test_intersect"),
    ),
)
@pytest.mark.parametrize(
    "r_nfa",
    map(
        lambda res: nfa(res[0], res[1], res[2]),
        load_test_res("test_intersect"),
    ),
)
def test_intersect(
    l_nfa: NondeterministicFiniteAutomaton, r_nfa: NondeterministicFiniteAutomaton
):
    expected = l_nfa.get_intersection(r_nfa)

    l_bm = build_bm_by_nfa(l_nfa)
    r_bm = build_bm_by_nfa(r_nfa)

    actual = build_nfa_by_bm(intersect(l_bm, r_bm))

    assert expected.is_equivalent_to(actual)


@pytest.mark.parametrize(
    "nfa_1, expected",
    map(
        lambda res: ((nfa(res[0], res[1], res[2])), res[3]),
        load_test_res("test_transitive_closure"),
    ),
)
def test_transitive_closure(
    nfa_1: NondeterministicFiniteAutomaton, expected: list[list[bool]]
):
    bm = build_bm_by_nfa(nfa_1)
    tc = dok_matrix(expected)

    assert transitive_closure(bm).toarray().data == tc.toarray().data
