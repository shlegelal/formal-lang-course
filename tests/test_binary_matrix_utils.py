import pytest
from pyformlang.finite_automaton import NondeterministicFiniteAutomaton, State
from scipy.sparse import dok_matrix

from project.utils.binary_matrix_utils import (
    bm_by_nfa,
    nfa_by_bm,
    intersect,
    transitive_closure,
)
from load_test_res import load_test_res


def nfa_by_transactions(
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
    nfa = nfa_by_bm(bm_by_nfa(nfa_by_transactions([])))

    assert nfa.is_empty()


@pytest.mark.parametrize(
    "nfa",
    map(
        lambda res: (nfa_by_transactions(res[0], res[1], res[2])),
        load_test_res("test_intersect"),
    ),
)
def test_intersect_with_empty(nfa: NondeterministicFiniteAutomaton):
    bm = bm_by_nfa(nfa)
    empty_bm = bm_by_nfa(nfa_by_transactions([]))

    intersection = nfa_by_bm(intersect(bm, empty_bm))

    assert intersection.is_empty()


@pytest.mark.parametrize(
    "l_nfa",
    map(
        lambda res: nfa_by_transactions(res[0], res[1], res[2]),
        load_test_res("test_intersect"),
    ),
)
@pytest.mark.parametrize(
    "r_nfa",
    map(
        lambda res: nfa_by_transactions(res[0], res[1], res[2]),
        load_test_res("test_intersect"),
    ),
)
def test_intersect(
    l_nfa: NondeterministicFiniteAutomaton, r_nfa: NondeterministicFiniteAutomaton
):
    expected = l_nfa.get_intersection(r_nfa)

    l_bm = bm_by_nfa(l_nfa)
    r_bm = bm_by_nfa(r_nfa)

    actual = nfa_by_bm(intersect(l_bm, r_bm))

    assert expected.is_equivalent_to(actual)


@pytest.mark.parametrize(
    "nfa, expected",
    map(
        lambda res: (
            (nfa_by_transactions(res[0], res[1], res[2])),
            {
                (i, j)
                for i, tmp in enumerate(res[3])
                for j, data in enumerate(tmp)
                if data
            },
        ),
        load_test_res("test_transitive_closure"),
    ),
)
def test_transitive_closure(
    nfa: NondeterministicFiniteAutomaton, expected: list[list[bool]]
):
    bm = bm_by_nfa(nfa)
    actual = set(zip(*transitive_closure(bm)))

    assert actual == expected
