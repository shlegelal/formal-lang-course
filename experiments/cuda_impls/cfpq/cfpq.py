import networkx as nx
import pyformlang.cfg as c

from experiments.cuda_impls.cfpq.matrix import constrained_transitive_closure_by_matrix
from experiments.cuda_impls.cfpq.tensor import constrained_transitive_closure_by_tensor
from project.cfpq.cfpq import _cfpq_by_transitive_closure
from project.utils.node_type import NodeType


def cfpq_by_matrix(
    graph: nx.Graph,
    query: str | c.CFG,
    start_nodes: set[NodeType] | None = None,
    final_nodes: set[NodeType] | None = None,
    start_var: str | c.Variable = c.Variable("S"),
) -> set[tuple[NodeType, NodeType]]:
    return _cfpq_by_transitive_closure(
        graph,
        query,
        start_nodes,
        final_nodes,
        start_var,
        constrained_transitive_closure_by_matrix,
    )


def cfpq_by_tensor(
    graph: nx.Graph,
    query: str | c.CFG,
    start_nodes: set[NodeType] | None = None,
    final_nodes: set[NodeType] | None = None,
    start_var: str | c.Variable = c.Variable("S"),
) -> set[tuple[NodeType, NodeType]]:
    return _cfpq_by_transitive_closure(
        graph,
        query,
        start_nodes,
        final_nodes,
        start_var,
        constrained_transitive_closure_by_tensor,
    )
