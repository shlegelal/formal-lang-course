import networkx as nx
import pyformlang.regular_expression as re

from experiments.cuda_impls.utils.bool_decomposition import BoolDecomposition
from project.rpq import fa_utils
from project.rpq.rpq import BfsMode
from project.utils.node_type import NodeType


def rpq_by_tensor(
    graph: nx.Graph,
    query: str | re.Regex,
    starts: set[NodeType] | None = None,
    finals: set[NodeType] | None = None,
) -> set[tuple[NodeType, NodeType]]:
    # Create boolean decompositions for the graph and the query
    graph_decomp = BoolDecomposition.from_nfa(
        fa_utils.graph_to_nfa(graph, starts, finals)
    )
    query_decomp = BoolDecomposition.from_nfa(fa_utils.regex_to_min_dfa(query))

    # Intersection of decompositions gives intersection of languages
    intersection = graph_decomp.intersect(query_decomp)
    # Transitive closure helps determine reachability
    transitive_closure_indices = intersection.transitive_closure_any_symbol()

    # Two nodes satisfy the query if one is the beginning of a path (i.e. a word) and
    # the other is its end
    results = set()
    for n_from_i, n_to_i in zip(*transitive_closure_indices):
        n_from = intersection.states[n_from_i]
        n_to = intersection.states[n_to_i]
        if n_from.is_start and n_to.is_final:
            beg_graph_node = n_from.data[0]
            end_graph_node = n_to.data[0]
            results.add((beg_graph_node, end_graph_node))
    return results


def rpq_by_bfs(
    graph: nx.Graph,
    query: str | re.Regex,
    starts: set[NodeType] | None = None,
    finals: set[NodeType] | None = None,
    mode: BfsMode = BfsMode.FIND_COMMON_REACHABLE_SET,
) -> set[NodeType] | set[tuple[NodeType, NodeType]]:
    graph_decomp = BoolDecomposition.from_nfa(
        fa_utils.graph_to_nfa(graph, starts, finals)
    )
    query_decomp = BoolDecomposition.from_nfa(fa_utils.regex_to_min_dfa(query))

    result_indices = graph_decomp.constrained_bfs(
        query_decomp, separated=mode == BfsMode.FIND_REACHABLE_FOR_EACH_START
    )

    match mode:
        case BfsMode.FIND_COMMON_REACHABLE_SET:
            return {graph_decomp.states[i].data for i in result_indices}
        case BfsMode.FIND_REACHABLE_FOR_EACH_START:
            return {
                (graph_decomp.states[i].data, graph_decomp.states[j].data)
                for i, j in result_indices
            }
