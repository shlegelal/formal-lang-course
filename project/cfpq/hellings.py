import networkx as nx
import pyformlang.cfg as c

from project.utils.node_type import NodeType
from project.cfpq.cfg_utils import cfg_to_wcnf


def constrained_transitive_closure_by_hellings(
    graph: nx.Graph, cfg: c.CFG
) -> set[tuple[NodeType, c.Variable, NodeType]]:
    cfg = cfg_to_wcnf(cfg)

    # Convert productions into a more efficient form
    eps_prods: set[c.Variable] = set()  # A -> epsilon
    term_prods: dict[c.Variable, set[c.Terminal]] = {}  # A -> a
    var_prods: dict[c.Variable, set[tuple[c.Variable, c.Variable]]] = {}  # A -> B C
    for p in cfg.productions:
        match p.body:
            case [c.Epsilon()]:
                eps_prods.add(p.head)
            case [c.Terminal() as t]:
                term_prods.setdefault(p.head, set()).add(t)
            case [c.Variable() as v1, c.Variable() as v2]:
                var_prods.setdefault(p.head, set()).add((v1, v2))

    # Initialize result
    res = {(n, v, n) for n in graph.nodes for v in eps_prods} | {
        (n1, v, n2)
        for n1, n2, l in graph.edges.data("label")
        for v in term_prods
        if c.Terminal(l) in term_prods[v]
    }

    # Run main Hellings cycles
    queue = res.copy()
    while len(queue) > 0:
        start1, v_i, end1 = queue.pop()

        tmp = (
            set()
        )  # Create a temporary to store results not to change res during iteration
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
