from networkx import MultiDiGraph
from pyformlang.finite_automaton import (
    DeterministicFiniteAutomaton,
    NondeterministicFiniteAutomaton,
    State,
)
from pyformlang.regular_expression import Regex

from project.utils.graph_utils import *


class AutomataUtilsError(Exception):
    """
    Base exception for automata utils

    :param msg: Error message
    """

    def __init__(self, msg):
        self.msg = msg


def build_dfa_by_redex(redex: Regex) -> DeterministicFiniteAutomaton:
    """
    Builds DFA by a *regular expression* (https://pyformlang.readthedocs.io/en/latest/usage.html#regular-expression).

    :param redex: Regular expression.
    :return: Minimal DFA built on given regular expression.
    """
    return redex.to_epsilon_nfa().minimize()


def build_nfa_by_graph(
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


def rpq(
    graph: MultiDiGraph,
    query: Regex,
    start_states: set = None,
    final_states: set = None,
) -> set:
    """
    Computes Regular Path Querying from given graph and regular expression
    :param graph: Graph with labeled edges.
    :param query: Regular expression.
    :param start_states: Start states in NFA. If None, then every node in NFA is the starting.
    :param final_states: Final states in NFA. If None, then every node in NFA is the final.
    :return: Regular Path Querying
    """
    graph_bm = build_bm_by_nfa(build_nfa_by_graph(graph, start_states, final_states))
    query_bm = build_bm_by_nfa(build_dfa_by_redex(query))
    intersection = intersect(graph_bm, query_bm)
    tc = transitive_closure(intersection)
    res = set()

    for state_from, state_to in zip(*tc.nonzero()):
        if (
            state_from in intersection.start_states
            and state_to in intersection.final_states
        ):
            res.add(
                (
                    state_from // len(query_bm.indexed_states),
                    state_to // len(query_bm.indexed_states),
                )
            )

    return res
