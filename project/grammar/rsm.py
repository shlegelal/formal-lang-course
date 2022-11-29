from collections import namedtuple

from pyformlang.finite_automaton import State
from scipy.sparse import dok_array

from project.grammar.ecfg import ECFG
from project.utils.binary_matrix_utils import BinaryMatrix

RSM = namedtuple("RSM", "start boxes")


def rsm_from_ecfg(ecfg: ECFG) -> RSM:
    return RSM(
        ecfg.start,
        {head: body.to_epsilon_nfa() for head, body in ecfg.productions.items()},
    )


def minimize_rsm(rsm) -> RSM:
    for var, nfa in rsm.boxes.items():
        rsm.boxes[var] = nfa.minimize()
    return rsm


def bm_from_rsm(rsm: RSM):
    indexed_states = {}
    start_states = set()
    final_states = set()
    matrix = {}
    i = 0
    for var, nfa in rsm.boxes.items():
        for st in nfa.states:
            new_st = State((var, st.value))
            if new_st not in indexed_states.keys():
                if st in nfa.start_states:
                    start_states.add(i)
                if st in nfa.final_states:
                    final_states.add(i)
                indexed_states[new_st] = i
                i += 1
    for var, nfa in rsm.boxes.items():
        transitions = nfa.to_dict()
        for n_from in transitions:
            for symbol, ns_to in transitions[n_from].items():
                adj = matrix.setdefault(symbol.value, dok_array((i, i), dtype=bool))
                start_index = indexed_states[State((var, n_from))]
                for n_to in ns_to if isinstance(ns_to, set) else {ns_to}:
                    end_index = indexed_states[State((var, n_to))]
                    adj[start_index, end_index] = True

    for key in matrix:
        matrix[key] = matrix[key].tocsr()

    return BinaryMatrix(indexed_states, start_states, final_states, matrix)
