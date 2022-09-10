import cfpq_data
import networkx as nx
from typing import NamedTuple, Iterable, IO


class GraphInfo(NamedTuple):
    """Graph information."""

    nodes_num: int
    """ Number of nodes in the graph. """
    edges_num: int
    """ Number of edges in the graph. """
    labels: Iterable[str]
    """ Labels of each edge in the graph. """


def load_graph(name: str) -> nx.MultiDiGraph:
    """Loads a graph from cfpq_data dataset."""
    graph_path = cfpq_data.download(name)
    graph = cfpq_data.graph_from_csv(graph_path)
    return graph


def get_graph_info(graph: nx.Graph) -> GraphInfo:
    """Retrieves information from the given graph."""
    labels = map(lambda data: data[2]["label"], graph.edges.data())
    return GraphInfo(graph.number_of_nodes(), graph.number_of_edges(), labels)


def build_two_cycles_graph(
    ns: tuple[int, int], labels: tuple[str, str]
) -> nx.MultiDiGraph:
    """
    Creates a graph with two cycles and labeled edges.

    :param ns: numbers of nodes in two cycles.
    :param labels: labels for edges in two cycles.
    :return: the resulting graph.
    """
    graph = cfpq_data.labeled_two_cycles_graph(ns[0], ns[1], labels=labels)
    return graph


def write_graph_to_dot(graph: nx.Graph, path: str | IO):
    """Writes the given graph into the specified DOT file."""
    pydot_graph = nx.drawing.nx_pydot.to_pydot(graph)
    with open(path, "w") as f:
        # Have to remove newlines as pydot treats some of them as nodes on import
        f.write(pydot_graph.to_string().replace("\n", ""))
