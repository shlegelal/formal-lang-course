from pyformlang.finite_automaton import DeterministicFiniteAutomaton
from pyformlang.regular_expression import Regex

from project.utils.binary_matrix import *
from project.utils.graph import *


class AutomataUtilsError(Exception):
    """
    Base exception for automata utils

    :param msg: Error message
    """

    def __init__(self, msg):
        self.msg = msg


def dfa_by_regex(regex: Regex) -> DeterministicFiniteAutomaton:
    """
    Builds DFA by a *regular expression* (https://pyformlang.readthedocs.io/en/latest/usage.html#regular-expression).

    :param regex: Regular expression.
    :return: Minimal DFA built on given regular expression.
    """
    return regex.to_epsilon_nfa().minimize()


def nfa_by_graph(
    graph: MultiDiGraph, start_states: set = None, final_states: set = None
) -> NondeterministicFiniteAutomaton:
    """
    Builds NFA by a graph.

    :param graph: Graph to transform to NFA.
    :param start_states: Start states in NFA. If None, then every node in NFA is the starting.
    :param final_states: Final states in NFA. If None, then every node in NFA is the final.
    :return: NFA built on given graph.
    :raises AutomataUtilsError: if the given starting or final states do not match the graph.
    """

    nfa = NondeterministicFiniteAutomaton()
    # There is no DuplicateTransitionError, since the set.
    nfa.add_transitions(get_edges_by_label(graph))
    all_nodes = set(graph)

    if not start_states:
        start_states = all_nodes
    if not final_states:
        final_states = all_nodes

    if not start_states.issubset(all_nodes):
        raise AutomataUtilsError(
            f"Invalid start states: {start_states.difference(all_nodes)}"
        )
    if not final_states.issubset(all_nodes):
        raise AutomataUtilsError(
            f"Invalid final states: {final_states.difference(all_nodes)}"
        )

    for state in start_states:
        nfa.add_start_state(State(state))
    for state in final_states:
        nfa.add_final_state(State(state))

    return nfa


def intersect_nfa(
    nfa1: NondeterministicFiniteAutomaton, nfa2: NondeterministicFiniteAutomaton
) -> NondeterministicFiniteAutomaton:
    bm1 = bm_by_nfa(nfa1)
    bm2 = bm_by_nfa(nfa2)
    intersection = intersect(bm1, bm2)

    return nfa_by_bm(intersection)
