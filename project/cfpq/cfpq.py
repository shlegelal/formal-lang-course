import networkx as nx
import pyformlang.cfg as c

from project.utils.node_type import NodeType
from project.cfpq.hellings import constrained_transitive_closure_by_hellings


def cfpq_by_hellings(
    graph: nx.Graph,
    query: str | c.CFG,
    start_nodes: set[NodeType] | None = None,
    final_nodes: set[NodeType] | None = None,
    start_var: str | c.Variable = c.Variable("S"),
) -> set[tuple[NodeType, NodeType]]:
    if not isinstance(start_var, c.Variable):
        start_var = c.Variable(start_var)
    if not isinstance(query, c.CFG):
        query = c.CFG.from_text(query, start_symbol=start_var)
    if start_nodes is None:
        start_nodes = graph.nodes
    if final_nodes is None:
        final_nodes = graph.nodes
    if start_var is None:
        start_var = query.start_symbol

    constrained_transitive_closure = constrained_transitive_closure_by_hellings(
        graph, query
    )

    return {
        (start, final)
        for start, var, final in constrained_transitive_closure
        if start in start_nodes and var == start_var and final in final_nodes
    }
