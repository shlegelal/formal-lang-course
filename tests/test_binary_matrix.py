import pytest
from pyformlang.finite_automaton import NondeterministicFiniteAutomaton, State

from project.utils.binary_matrix import (
    bm_by_nfa,
    nfa_by_bm,
    intersect,
    transitive_closure,
)
from test_utils import load_test_res, nfa_by_transactions


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
