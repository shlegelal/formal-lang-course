from typing import Any

import networkx as nx
import pycubool as cb
import pyformlang.cfg as c

from project.cfpq.cfg_utils import cfg_to_wcnf
from project.utils.node_type import NodeType


def constrained_transitive_closure_by_matrix(
    graph: nx.Graph, cfg: c.CFG
) -> set[tuple[NodeType, c.Variable, NodeType]]:
    cfg = cfg_to_wcnf(cfg)

    # Convert productions into a more efficient form
    eps_prods: set[c.Variable] = set()  # A -> epsilon
    term_prods: dict[Any, set[c.Variable]] = {}  # A -> a
    var_prods: set[tuple[c.Variable, c.Variable, c.Variable]] = set()  # A -> B C
    for p in cfg.productions:
        match p.body:
            case [c.Epsilon()]:
                eps_prods.add(p.head)
            case [c.Terminal() as t]:
                term_prods.setdefault(t.value, set()).add(p.head)
            case [c.Variable() as v1, c.Variable() as v2]:
                var_prods.add((p.head, v1, v2))

    # Initialize graph bool decomposition
    nodes = {n: i for i, n in enumerate(graph.nodes)}
    if len(nodes) == 0:  # pycubool cannot create empty matrices
        return set()
    adjs: dict[c.Variable, cb.Matrix] = {
        v: cb.Matrix.empty((len(nodes), len(nodes))) for v in cfg.variables
    }

    # Add edges to bool decomposition accounting for A -> a productions
    for n1, n2, l in graph.edges.data("label"):
        i = nodes[n1]
        j = nodes[n2]
        for v in term_prods.setdefault(l, set()):
            adjs[v][i, j] = True

    # Add self loops accounting for A -> epsilon productions
    diag = cb.Matrix.from_lists(
        (len(nodes), len(nodes)),
        [i for i in range(len(nodes))],
        [i for i in range(len(nodes))],
    )
    for v in eps_prods:
        adjs[v] = adjs[v].ewiseadd(diag)

    # Add transitions accounting for A -> B C productions
    changed = True
    while changed:
        changed = False
        for h, b1, b2 in var_prods:
            nvals_old = adjs[h].nvals
            adjs[b1].mxm(adjs[b2], out=adjs[h], accumulate=True)
            changed |= adjs[h].nvals != nvals_old

    # Construct the result
    nodes = {i: n for n, i in nodes.items()}
    result = set()
    for v, adj in adjs.items():
        for i, j in adj.to_list():
            result.add((nodes[i], v, nodes[j]))
    return result
