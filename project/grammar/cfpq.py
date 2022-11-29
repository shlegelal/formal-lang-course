from typing import Callable
import networkx as nx
import pyformlang.cfg as c
from networkx import MultiDiGraph
from scipy.sparse import dok_array, csr_array, eye

from project.grammar.cfg_utils import cfg_to_wcnf
from project.grammar.ecfg import ecfg_from_cfg
from project.grammar.rsm import bm_from_rsm, rsm_from_ecfg, minimize_rsm
from project.utils.automata_utils import build_nfa_by_graph
from project.utils.binary_matrix_utils import build_bm_by_nfa, intersect


def helling_cfpq(
    graph: nx.Graph,
    query: c.CFG,
    sn: set = None,
    fn: set = None,
    start: str | c.Variable = "S",
) -> set:
    return _cfpq_transitive_closure(
        graph, query, sn, fn, start, helling_constrained_transitive_closure
    )


def matrix_cfpq(
    graph: nx.Graph,
    query: c.CFG,
    sn: set = None,
    fn: set = None,
    start: str | c.Variable = "S",
) -> set:
    return _cfpq_transitive_closure(
        graph, query, sn, fn, start, matrix_constrained_transitive_closure
    )


def tensor_cfpq(
    graph: nx.Graph,
    query: str | c.CFG,
    start_nodes: set | None = None,
    final_nodes: set | None = None,
    start_var: str | c.Variable = c.Variable("S"),
) -> set:
    return _cfpq_transitive_closure(
        graph,
        query,
        start_nodes,
        final_nodes,
        start_var,
        tensor_constrained_transitive_closure,
    )


def _cfpq_transitive_closure(
    graph: nx.Graph,
    query: str | c.CFG,
    start_nodes: set | None,
    final_nodes: set | None,
    start_var: str | c.Variable,
    tc: Callable,
) -> set:
    if not isinstance(start_var, c.Variable):
        start_var = c.Variable(start_var)
    if start_nodes is None:
        start_nodes = graph.nodes
    if final_nodes is None:
        final_nodes = graph.nodes
    if start_var is None:
        start_var = query.start_symbol

    ctc = tc(graph, query)

    return {
        (start, final)
        for start, var, final in ctc
        if start in start_nodes and var == start_var and final in final_nodes
    }


def helling_constrained_transitive_closure(graph: nx.Graph, cfg: c.CFG) -> set:
    cfg = cfg_to_wcnf(cfg)
    eps_prods = set()
    term_prods = {}
    var_prods = {}
    for p in cfg.productions:
        match p.body:
            case [c.Epsilon()]:
                eps_prods.add(p.head)
            case [c.Terminal() as t]:
                term_prods.setdefault(p.head, set()).add(t)
            case [c.Variable() as v1, c.Variable() as v2]:
                var_prods.setdefault(p.head, set()).add((v1, v2))

    res = {(n, v, n) for n in graph.nodes for v in eps_prods} | {
        (n1, v, n2)
        for n1, n2, l in graph.edges.data("label")
        for v in term_prods
        if c.Terminal(l) in term_prods[v]
    }

    queue = res.copy()
    while len(queue) > 0:
        start1, v_i, end1 = queue.pop()

        tmp = set()
        for start2, v_j, end2 in res:
            if end2 == start1:
                for v_k in var_prods:
                    if (v_j, v_i) in var_prods[v_k] and (start2, v_k, end1) not in res:
                        queue.add((start2, v_k, end1))
                        tmp.add((start2, v_k, end1))
            if start2 == end1:
                for v_k in var_prods:
                    if (v_i, v_j) in var_prods[v_k] and (start1, v_k, end2) not in res:
                        queue.add((start1, v_k, end2))
                        tmp.add((start1, v_k, end2))

        res |= tmp

    return res


def matrix_constrained_transitive_closure(graph: nx.Graph, cfg: c.CFG) -> set:
    cfg = cfg_to_wcnf(cfg)
    eps_prods = set()
    term_prods = {}
    var_prods = set()
    for p in cfg.productions:
        match p.body:
            case [c.Epsilon()]:
                eps_prods.add(p.head)
            case [c.Terminal() as t]:
                term_prods.setdefault(t.value, set()).add(p.head)
            case [c.Variable() as v1, c.Variable() as v2]:
                var_prods.add((p.head, v1, v2))

    nodes = {n: i for i, n in enumerate(graph.nodes)}
    adjs: dict[c.Variable, dok_array] = {
        v: dok_array((len(nodes), len(nodes)), dtype=bool) for v in cfg.variables
    }

    for n1, n2, l in graph.edges.data("label"):
        i = nodes[n1]
        j = nodes[n2]
        for v in term_prods.setdefault(l, set()):
            adjs[v][i, j] = True

    for adj in adjs.values():
        adj.tocsr()

    diag = csr_array(eye(len(nodes), dtype=bool))
    for v in eps_prods:
        adjs[v] += diag

    changed = True
    while changed:
        changed = False
        for h, b1, b2 in var_prods:
            nnz_old = adjs[h].nnz
            adjs[h] += adjs[b1] @ adjs[b2]
            changed |= adjs[h].nnz != nnz_old

    nodes = {i: n for n, i in nodes.items()}
    result = set()
    for v, adj in adjs.items():
        for i, j in zip(*adj.nonzero()):
            result.add((nodes[i], v, nodes[j]))
    return result


def tensor_constrained_transitive_closure(graph: MultiDiGraph, cfg: c.CFG) -> set:
    rsm_d = bm_from_rsm(minimize_rsm(rsm_from_ecfg(ecfg_from_cfg(cfg))))

    graph_d = build_bm_by_nfa(build_nfa_by_graph(graph))

    diag = csr_array(eye(len(graph_d.indexed_states), dtype=bool))
    for v in cfg.get_nullable_symbols():
        graph_d.matrix[v.value] += diag

    transitive_closure_size = 0
    while True:
        transitive_closure_indices = list(
            _transitive_closure_any_symbol(intersect(rsm_d, graph_d))
        )

        if len(transitive_closure_indices) == transitive_closure_size:
            break
        transitive_closure_size = len(transitive_closure_indices)

        for i, j in transitive_closure_indices:
            r_i, r_j = i // len(rsm_d.indexed_states), j // len(rsm_d.indexed_states)
            if r_i in rsm_d.start_states and r_j in rsm_d.final_states:
                v = next(
                    st for st, i in rsm_d.indexed_states.items() if i == r_i
                ).value[0]

                g_i, g_j = i % len(rsm_d.indexed_states), j % len(rsm_d.indexed_states)
                ij_graph_adj = csr_array(
                    ([True], ([g_i], [g_j])),
                    shape=(len(graph_d.indexed_states), len(graph_d.indexed_states)),
                    dtype=bool,
                )

                if v in graph_d.matrix:
                    graph_d.matrix[v] += ij_graph_adj
                else:
                    graph_d.matrix[v] = ij_graph_adj.copy()

    result = set()
    g_states = {idx: state for state, idx in graph_d.indexed_states.items()}
    for v, adj in graph_d.matrix.items():
        if isinstance(v, c.Variable):
            for i, j in zip(*adj.nonzero()):
                result.add((g_states[i].value, v, g_states[j].value))
    return result


def _transitive_closure_any_symbol(self):
    n = len(self.indexed_states)
    adj_all = sum(self.matrix.values(), start=csr_array((n, n), dtype=bool))
    adj_all.eliminate_zeros()

    while True:
        prev_path_num = adj_all.nnz
        adj_all += adj_all @ adj_all
        if prev_path_num == adj_all.nnz:
            break

    d = adj_all.nonzero()
    res = set()
    for i in range(len(d[0])):
        res.add((d[0][i], d[1][i]))

    return res
