from typing import Callable
import networkx as nx
import pyformlang.cfg as c
from scipy.sparse import dok_array, csr_array, eye

from project.grammar.cfg_utils import cfg_to_wcnf


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
