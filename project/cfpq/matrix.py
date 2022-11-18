import networkx as nx
import pyformlang.cfg as c
from scipy.sparse import csr_array
from scipy.sparse import dok_array
from scipy.sparse import eye
from typing import Any

from project.utils.node_type import NodeType
from project.cfpq.cfg_utils import cfg_to_wcnf


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
    adjs: dict[c.Variable, dok_array] = {
        v: dok_array((len(nodes), len(nodes)), dtype=bool) for v in cfg.variables
    }

    # Add edges to bool decomposition accounting for A -> a productions
    for n1, n2, l in graph.edges.data("label"):
        i = nodes[n1]
        j = nodes[n2]
        for v in term_prods.setdefault(l, set()):
            adjs[v][i, j] = True

    # Convert matrices to CSR for more efficient computations
    for adj in adjs.values():
        adj.tocsr()

    # Add self loops accounting for A -> epsilon productions
    diag = csr_array(eye(len(nodes), dtype=bool))
    for v in eps_prods:
        adjs[v] += diag

    # Add transitions accounting for A -> B C productions
    changed = True
    while changed:
        changed = False
        for h, b1, b2 in var_prods:
            nnz_old = adjs[h].nnz
            adjs[h] += adjs[b1] @ adjs[b2]
            changed |= adjs[h].nnz != nnz_old

    # Construct the result
    nodes = {i: n for n, i in nodes.items()}
    result = set()
    for v, adj in adjs.items():
        for i, j in zip(*adj.nonzero()):
            result.add((nodes[i], v, nodes[j]))
    return result
