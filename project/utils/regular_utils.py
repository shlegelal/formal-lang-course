from networkx import MultiDiGraph
from pyformlang.regular_expression import Regex

from project.utils.automata_utils import build_dfa_by_redex, build_nfa_by_graph
from project.utils.binary_matrix_utils import build_bm_by_nfa, intersect, transitive_closure


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
