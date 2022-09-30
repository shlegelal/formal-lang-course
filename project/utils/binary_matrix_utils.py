from collections import namedtuple
from pyformlang.finite_automaton import NondeterministicFiniteAutomaton, State
from scipy.sparse import dok_matrix, kron

BinaryMatrix = namedtuple(
    "BinaryMatrix", "indexed_states start_states final_states matrix"
)
"""
Namedtuple specifying a binary matrix for some automaton.
"""


def build_bm_by_nfa(nfa: NondeterministicFiniteAutomaton) -> BinaryMatrix:
    """
    Builds binary matrix by NFA.

    :param nfa: NFA to transform.
    :return: Binary matrix.
    """
    indexed_states = {state: idx for idx, state in enumerate(nfa.states)}
    matrix = dict()
    nfa_dict = nfa.to_dict()

    for label in nfa.symbols:
        tmp_matrix = dok_matrix((len(nfa.states), len(nfa.states)), dtype=bool)
        for state_from, transitions in nfa_dict.items():
            states_to = set()
            if label in transitions:
                states_to = (
                    transitions[label]
                    if isinstance(transitions[label], set)
                    else {transitions[label]}
                )
            for state_to in states_to:
                tmp_matrix[
                    indexed_states[state_from],
                    indexed_states[state_to],
                ] = True
        matrix[label] = tmp_matrix

    return BinaryMatrix(
        indexed_states,
        nfa.start_states,
        nfa.final_states,
        matrix,
    )


def build_nfa_by_bm(bm: BinaryMatrix) -> NondeterministicFiniteAutomaton:
    """
    Builds NFA by binary matrix.

    :param bm: Binary matrix to transform.
    :return: NFA.
    """
    nfa = NondeterministicFiniteAutomaton()

    for label in bm.matrix.keys():
        arr = bm.matrix[label].toarray()
        for i in range(len(arr)):
            for j in range(len(arr)):
                if arr[i][j]:
                    nfa.add_transition(
                        bm.indexed_states[State(i)],
                        label,
                        bm.indexed_states[State(j)],
                    )

    for start_state in bm.start_states:
        nfa.add_start_state(bm.indexed_states[State(start_state)])
    for final_state in bm.final_states:
        nfa.add_final_state(bm.indexed_states[State(final_state)])

    return nfa


def transitive_closure(bm: BinaryMatrix) -> dok_matrix:
    """
    Computes transitive closure of binary matrix.

    :param bm: Binary matrix to compute.
    :return: Transitive closure of binary matrix.
    """
    if not bm.matrix.values():
        return dok_matrix((1, 1))

    tc = sum(bm.matrix.values())
    prev_nnz = tc.nnz
    curr_nnz = 0

    while prev_nnz != curr_nnz:
        tc += tc @ tc
        prev_nnz, curr_nnz = curr_nnz, tc.nnz

    return tc


def intersect(bm_l: BinaryMatrix, bm_r: BinaryMatrix) -> BinaryMatrix:
    """
    Computes intersection of two binary matrices.

    :param bm_l: Left-hand side binary matrix.
    :param bm_r: Right-hand side binary matrix.
    :return: Intersection of two binary matrices.
    """
    common_labels = bm_l.matrix.keys() & bm_r.matrix.keys()

    indexed_states = {}
    start_states = set()
    final_states = set()
    matrix = dict()

    for label in common_labels:
        matrix[label] = kron(bm_l.matrix[label], bm_r.matrix[label], format="dok")

    for state_lhs, s_lhs_index in bm_l.indexed_states.items():
        for state_rhs, s_rhs_index in bm_r.indexed_states.items():
            new_state = new_state_idx = (
                s_lhs_index * len(bm_r.indexed_states) + s_rhs_index
            )
            indexed_states[new_state] = new_state_idx

            if state_lhs in bm_l.start_states and state_rhs in bm_r.start_states:
                start_states.add(new_state)

            if state_lhs in bm_l.final_states and state_rhs in bm_r.final_states:
                final_states.add(new_state)

    return BinaryMatrix(indexed_states, start_states, final_states, matrix)
