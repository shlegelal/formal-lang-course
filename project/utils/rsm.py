from collections import namedtuple
from scipy.sparse import dok_array
import pyformlang.cfg as c
from pyformlang import finite_automaton as fa

from project.utils.ecfg import ECFG
from project.utils.binary_matrix import BinaryMatrix, StateInfo, transitive_closure

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


def get_reachables(rsm: RSM) -> set:
    bm = bm_by_rsm(rsm)
    nonterminals = {}
    res = set()

    for var in set(rsm.boxes).union(bm.matrix):
        if not isinstance(var, c.Variable):
            continue
        start_finals = (
            rsm.boxes[var].start_states.intersection(rsm.boxes[var].final_states)
            if var in rsm.boxes
            else set()
        )
        if len(start_finals) == 0 and var in bm.matrix:
            nonterminals[var] = bm.matrix.pop(var)
        if var == rsm.start:
            res |= {(s, s) for s in start_finals}

    while True:
        old_len = len(nonterminals)

        transitive_closure_indices = zip(*transitive_closure(bm))
        for n_from_i, n_to_i in transitive_closure_indices:
            n_from = bm.states[n_from_i]
            n_to = bm.states[n_to_i]
            if n_from.is_start and n_to.is_final:
                var1, s1 = n_from.data
                var2, s2 = n_to.data
                assert var1 == var2
                if var1 in nonterminals:
                    bm.matrix[var1] = nonterminals.pop(var1)
                if var1 == rsm.start:
                    res.add((fa.State(s1), fa.State(s2)))

        if len(nonterminals) == old_len:
            break

    return res
