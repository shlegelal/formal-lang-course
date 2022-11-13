import networkx as nx
import pyformlang.cfg as c

from project.grammar.cfg_utils import cfg_to_wcnf


def helling(
    graph: nx.Graph,
    query: c.CFG,
    start_nodes: set = None,
    final_nodes: set = None,
    start_var: str | c.Variable = "S",
) -> set:
    if not isinstance(start_var, c.Variable):
        start_var = c.Variable(start_var)
    if start_nodes is None:
        start_nodes = graph.nodes
    if final_nodes is None:
        final_nodes = graph.nodes
    if start_var is None:
        start_var = query.start_symbol

    ctc = constrained_transitive_closure(graph, query)

    return {
        (start, final)
        for start, var, final in ctc
        if start in start_nodes and var == start_var and final in final_nodes
    }


def constrained_transitive_closure(graph: nx.Graph, cfg: c.CFG) -> set:
    cfg = cfg_to_wcnf(cfg)

    eps_prods: set[c.Variable] = set()
    term_prods: dict[c.Variable, set[c.Terminal]] = {}
    var_prods: dict[c.Variable, set[tuple[c.Variable, c.Variable]]] = {}
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
