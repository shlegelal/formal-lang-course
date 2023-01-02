from collections import namedtuple
from scipy.sparse import dok_array

from project.utils.ecfg import ECFG
from project.utils.binary_matrix import BinaryMatrix, StateInfo

RSM = namedtuple("RSM", "start boxes")


def rsm_by_ecfg(ecfg: ECFG) -> RSM:
    return RSM(
        ecfg.start,
        {head: body.to_epsilon_nfa() for head, body in ecfg.productions.items()},
    )


def minimize_rsm(rsm) -> RSM:
    for var, nfa in rsm.boxes.items():
        rsm.boxes[var] = nfa.minimize()
    return rsm


def bm_by_rsm(rsm: RSM, is_sort: bool = False):
    states = list(
        {
            StateInfo(
                (var, st.value),
                st in nfa.start_states,
                st in nfa.final_states,
            )
            for var, nfa in rsm.boxes.items()
            for st in nfa.states
        }
    )
    if is_sort:
        states.sort(key=lambda st: (st.value[0].value, st.value[1]))

    matrix = {}
    n = len(states)
    for var, nfa in rsm.boxes.items():
        transitions = nfa.to_dict()
        for n_from in transitions:
            for symbol, ns_to in transitions[n_from].items():
                tmp = matrix.setdefault(symbol.value, dok_array((n, n), dtype=bool))
                start_index = next(
                    i for i, st in enumerate(states) if st.value == (var, n_from)
                )
                for n_to in ns_to if isinstance(ns_to, set) else {ns_to}:
                    end_index = next(
                        i for i, st in enumerate(states) if st.value == (var, n_to)
                    )
                    tmp[start_index, end_index] = True

    for key in matrix:
        matrix[key] = matrix[key].tocsr()

    return BinaryMatrix(states, matrix)
