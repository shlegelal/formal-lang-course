from networkx import MultiDiGraph
from pyformlang.regular_expression import Regex
from scipy.sparse import dok_matrix, block_diag, csr_array, lil_array, vstack

from project.utils.automata_utils import build_dfa_by_redex, build_nfa_by_graph
from project.utils.binary_matrix_utils import build_bm_by_nfa, intersect, transitive_closure, BinaryMatrix


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
    graph_bm = build_bm_by_nfa(build_nfa_by_graph(graph, start_states, final_states))
    query_bm = build_bm_by_nfa(build_dfa_by_redex(query))
    intersection = intersect(graph_bm, query_bm)
    tc = transitive_closure(intersection)
    res = set()
    indexes = {i: st for st, i in graph_bm.indexed_states.items()}

    for state_from, state_to in zip(*tc.nonzero()):
        if (
            state_from in intersection.start_states
            and state_to in intersection.final_states
        ):
            res.add(
                (
                    indexes[state_from // len(query_bm.indexed_states)],
                    indexes[state_to // len(query_bm.indexed_states)],
                )
            )

    return res


def _direct_sum(
    bm_left: BinaryMatrix,
    bm_right: BinaryMatrix,
) -> dict:
    matrix = dict()
    n = len(bm_right.indexed_states)
    for key in bm_left.matrix.keys():
        matrix[key] = csr_array(block_diag(
            (
                bm_left.matrix[key],
                (dok_matrix((n, n)) if key not in bm_right.matrix.keys() else bm_right.matrix[key])
            )
        ))

    return matrix


def _init_front(
    x: int,
    y: int,
    states: dict,
    start_states: set,
    start_row: lil_array,
) -> csr_array:
    f = lil_array((x, y))
    for st, i in states.items():
        if st in start_states:
            f[i, i] = 1
            f[i, x:] = start_row

    return f.tocsr()


def _init_front_separated(
    x: int,
    y: int,
    states: dict,
    start_states: set,
    graph_states: dict,
    start_state: set,
) -> (csr_array, list):
    fs = []
    start_states_list = []
    for g_ss in start_state:
        start_states_list.append(g_ss)

        fs.append(
            _init_front(
                x,
                y,
                states,
                start_states,
                lil_array([[int(g_ss == st) for st in graph_states.keys()]]),
            )
        )

    return csr_array(vstack(fs)) if len(fs) > 0 else csr_array((x, y)), start_states_list


def _transport_front_part(
    k: int,
    front: csr_array,
) -> csr_array:
    result = lil_array(front.shape)
    for i, j in zip(*front.nonzero()):
        if j < k:
            non_zero_row_right = front.getrow(i).tolil()[[0], k:]
            if non_zero_row_right.nnz > 0:
                row_shift = i // k * k
                result[row_shift + j, j] = 1
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

    graph_bm = build_bm_by_nfa(build_nfa_by_graph(graph, start_states, final_states))
    query_bm = build_bm_by_nfa(build_dfa_by_redex(query))

    n = len(graph_bm.indexed_states)
    k = len(query_bm.indexed_states)

    if not n:
        return set()

    d = _direct_sum(query_bm, graph_bm)
    graph_index_start_state = []

    if separated:
        front, graph_index_start_state = _init_front_separated(
            k,
            k + n,
            query_bm.indexed_states,
            query_bm.start_states,
            graph_bm.indexed_states,
            graph_bm.start_states,
        )
    else:
        front = (
            _init_front(
                k,
                k + n,
                query_bm.indexed_states,
                query_bm.start_states,
                lil_array([[int(st in graph_bm.start_states) for st in graph_bm.indexed_states.keys()]]),
            )
        )

    visited = csr_array(front.shape)

    while True:
        tmp = visited.copy()

        for m in d.values():
            front_part = visited @ m if front is None else front @ m
            visited += _transport_front_part(k, front_part)

        front = None

        if visited.nnz == tmp.nnz:
            break

    result = set()
    graph_states = {i: st for st, i in graph_bm.indexed_states.items()}
    query_final_states_index = {i for st, i in query_bm.indexed_states.items() if st in query_bm.final_states}
    graph_final_states_index = {i for st, i in graph_bm.indexed_states.items() if st in graph_bm.final_states}

    for i, j in zip(*visited.nonzero()):
        if j >= k and i % k in query_final_states_index:
            graph_index = j - k
            if graph_index in graph_final_states_index:
                result.add(
                    graph_states[graph_index]
                    if not separated
                    else (graph_index_start_state[i // k], graph_states[graph_index])
                )

    return result
