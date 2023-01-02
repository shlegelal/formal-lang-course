from networkx import MultiDiGraph
from pyformlang.regular_expression import Regex
from scipy.sparse import csr_array, lil_array, vstack

from project.utils.automata import dfa_by_regex, nfa_by_graph
from project.utils.binary_matrix import (
    bm_by_nfa,
    intersect,
    transitive_closure,
    direct_sum,
)


def tensor_rpq(
    graph: MultiDiGraph,
    query: Regex,
    start_states: set = None,
    final_states: set = None,
) -> set:
    """
    Computes Regular Path Querying from given graph and regular expression
    :param graph: Graph with labeled edges.
    :param query: Regular expression.
    :param start_states: Start states in graph. If None, then every node in graph is the starting.
    :param final_states: Final states in graph. If None, then every node in graph is the final.
    :return: Regular Path Querying
    """
    graph_bm = bm_by_nfa(nfa_by_graph(graph, start_states, final_states))
    query_bm = bm_by_nfa(dfa_by_regex(query))

    intersection = intersect(graph_bm, query_bm)
    tc = transitive_closure(intersection)
    res = set()
    for n_from_i, n_to_i in zip(*tc):
        n_from = intersection.states[n_from_i]
        n_to = intersection.states[n_to_i]
        if n_from.is_start and n_to.is_final:
            beg_node = n_from.value[0]
            end_node = n_to.value[0]
            res.add((beg_node, end_node))

    return res


def _init_front(
    graph_states: list,
    query_states: list,
    start_row: lil_array,
) -> csr_array:
    x = len(query_states)
    y = len(query_states) + len(graph_states)
    f = lil_array((x, y), dtype=bool)
    for i, st in enumerate(query_states):
        if st.is_start:
            f[i, i] = True
            f[i, x:] = start_row

    return f.tocsr()


def _init_front_separated(
    graph_states: list,
    query_states: list,
    start_indexes: list,
) -> csr_array:
    x = len(query_states)
    y = len(graph_states)
    fs = [
        _init_front(
            graph_states,
            query_states,
            lil_array([i == st_i for i in range(y)], dtype=bool),
        )
        for st_i in start_indexes
    ]

    return csr_array(vstack(fs)) if len(fs) else csr_array((x, x + y), dtype=bool)


def _transform_front_part(
    k: int,
    front: csr_array,
) -> csr_array:
    result = lil_array(front.shape, dtype=bool)
    for i, j in zip(*front.nonzero()):
        if j < k:
            non_zero_row_right = front.getrow(i).tolil()[[0], k:]
            if non_zero_row_right.nnz > 0:
                row_shift = i // k * k
                result[row_shift + j, j] = True
                result[[row_shift + j], k:] += non_zero_row_right

    return result.tocsr()


def bfs_rpq(
    graph: MultiDiGraph,
    query: Regex,
    start_states: set = None,
    final_states: set = None,
    separated: bool = False,
) -> set:
    """
    Computes Regular Path Querying from given graph and regular expression
    :param graph: Graph with labeled edges.
    :param query: Regular expression.
    :param start_states: Start states in graph. If None, then every node in graph is the starting.
    :param final_states: Final states in graph. If None, then every node in graph is the final.
    :param separated: Enable to find the initial state.
    :return: Regular Path Querying
    """

    graph_bm = bm_by_nfa(nfa_by_graph(graph, start_states, final_states))
    query_bm = bm_by_nfa(dfa_by_regex(query))

    n = len(graph_bm.states)
    k = len(query_bm.states)

    if not n:
        return set()

    start_graph_indices = [i for i, st in enumerate(graph_bm.states) if st.is_start]

    init_front = (
        _init_front(
            graph_bm.states,
            query_bm.states,
            lil_array([st.is_start for st in graph_bm.states], dtype=bool),
        )
        if not separated
        else _init_front_separated(
            graph_bm.states, query_bm.states, start_graph_indices
        )
    )

    visited = csr_array(init_front.shape, dtype=bool)
    ds = direct_sum(query_bm, graph_bm)
    while True:
        prev_nnz = visited.nnz

        for tmp in ds.matrix.values():
            front_part = visited @ tmp if init_front is None else init_front @ tmp
            visited += _transform_front_part(len(query_bm.states), front_part)

        init_front = None

        if visited.nnz == prev_nnz:
            break

    res = set()
    for i, j in zip(*visited.nonzero()):
        if j >= k and query_bm.states[i % k].is_final:
            g_st_index = j - k
            if graph_bm.states[g_st_index].is_final:
                res.add(
                    g_st_index
                    if not separated
                    else (start_graph_indices[i // k], g_st_index)
                )

    return (
        {(graph_bm.states[i].value, graph_bm.states[j].value) for i, j in res}
        if separated
        else {graph_bm.states[i].value for i in res}
    )
