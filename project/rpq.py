import networkx as nx
from typing import TypeVar

from project.bool_decomposition import BoolDecomposition
from project.automata_utils import graph_to_nfa
from project.automata_utils import regex_to_min_dfa

_NodeType = TypeVar("_NodeType")


def rpq(
    graph: nx.Graph,
    query: str,
    starts: set[_NodeType] | None = None,
    finals: set[_NodeType] | None = None,
) -> set[tuple[_NodeType, _NodeType]]:
    # Create boolean decompositions for the graph and the query
    graph_decomp = BoolDecomposition.from_nfa(graph_to_nfa(graph, starts, finals))
    query_decomp = BoolDecomposition.from_nfa(regex_to_min_dfa(query))

    # Intersection of decompositions gives intersection of languages
    intersection = graph_decomp.intersect(query_decomp)
    # Transitive closure helps determine reachability
    transitive_closure_indices = intersection.transitive_closure_any_symbol()

    # Two nodes satisfy the query if one is the beginning of a path (i.e. a word) and
    # the other is its end
    results = set()
    for beg_i, end_i in zip(*transitive_closure_indices):
        beg = intersection.states[beg_i]
        end = intersection.states[end_i]
        if beg.is_start and end.is_final:
            beg_graph_node = beg.data[0]
            end_graph_node = end.data[0]
            results.add((beg_graph_node, end_graph_node))
    return results
