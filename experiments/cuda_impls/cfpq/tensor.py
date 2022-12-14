import networkx as nx
import pycubool as cb
import pyformlang.cfg as c
import pyformlang.finite_automaton as fa

from experiments.cuda_impls.utils.bool_decomposition import BoolDecomposition
from project.cfpq.ecfg import Ecfg
from project.cfpq.rsm import Rsm
from project.utils.node_type import NodeType


def constrained_transitive_closure_by_tensor(
    graph: nx.Graph, cfg: c.CFG
) -> set[tuple[NodeType, c.Variable, NodeType]]:
    # Initialize decompositions
    rsm_decomp = BoolDecomposition.from_rsm(
        Rsm.from_ecfg(Ecfg.from_cfg(cfg)).minimize()
    )
    graph_decomp = BoolDecomposition.from_nfa(fa.EpsilonNFA.from_networkx(graph))
    if len(graph_decomp.states) == 0:  # pycubool cannot create empty matrices
        return set()

    # Add self loops for nullable variables
    diag = cb.Matrix.from_lists(
        (len(graph_decomp.states), len(graph_decomp.states)),
        [i for i in range(len(graph_decomp.states))],
        [i for i in range(len(graph_decomp.states))],
    )
    for v in cfg.get_nullable_symbols():
        assert isinstance(v, c.Variable)  # Just in case
        if v.value in graph_decomp.adjs:
            graph_decomp.adjs[v.value] = graph_decomp.adjs[v.value].ewiseadd(diag)
        else:
            graph_decomp.adjs[v.value] = diag.dup()

    # Compute intersection closures while new edges appear
    transitive_closure_size = 0
    while True:
        # Compute transitive closure of intersection
        transitive_closure_indices = list(
            zip(*rsm_decomp.intersect(graph_decomp).transitive_closure_any_symbol())
        )

        # If no new edges appear, we are done
        if len(transitive_closure_indices) == transitive_closure_size:
            break
        transitive_closure_size = len(transitive_closure_indices)

        # Iterate over non-empty indices
        for i, j in transitive_closure_indices:
            # Translate intersection indices into RSM decomposition indices
            r_i, r_j = i // len(graph_decomp.states), j // len(graph_decomp.states)
            # If the edge is from a start RSM node to a final RSM node
            s, f = rsm_decomp.states[r_i], rsm_decomp.states[r_j]
            if s.is_start and f.is_final:
                # Get the variable of the box of this edge
                assert s.data[0] == f.data[0]  # There are no edges between boxes
                v = s.data[0]

                # Translate intersection indices into graph decomposition indices
                g_i, g_j = i % len(graph_decomp.states), j % len(graph_decomp.states)

                # Add the edge to the graph (not its value to discriminate it later)
                graph_decomp.adjs.setdefault(
                    v,
                    cb.Matrix.empty(
                        (len(graph_decomp.states), len(graph_decomp.states))
                    ),
                )[g_i, g_j] = True

    # Construct the result
    result = set()
    for v, adj in graph_decomp.adjs.items():
        # Filter out the initial edges
        if isinstance(v, c.Variable):
            for i, j in adj.to_list():
                result.add(
                    (graph_decomp.states[i].data, v, graph_decomp.states[j].data)
                )
    return result
