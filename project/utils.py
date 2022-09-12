import cfpq_data
import networkx as nx
from typing import NamedTuple
from typing import Iterable
from typing import IO


class GraphInfo(NamedTuple):
    nodes_num: int
    edges_num: int
    labels: Iterable[str]


def load_graph_from_cfpg_data(name: str) -> nx.MultiDiGraph:
    graph_path = cfpq_data.download(name)
    graph = cfpq_data.graph_from_csv(graph_path)
    return graph


def get_graph_info(graph: nx.Graph) -> GraphInfo:
    labels = map(lambda data: data[2]["label"], graph.edges.data())
    return GraphInfo(graph.number_of_nodes(), graph.number_of_edges(), labels)


def build_labeled_two_cycles_graph(
    first_cycle_num: int,
    first_cycle_label: str,
    second_cycle_num: int,
    second_cycle_label: str,
) -> nx.MultiDiGraph:
    graph = cfpq_data.labeled_two_cycles_graph(
        first_cycle_num,
        second_cycle_num,
        labels=(first_cycle_label, second_cycle_label),
    )
    return graph


def save_graph_as_dot(graph: nx.Graph, path: str | IO):
    pydot_graph = nx.drawing.nx_pydot.to_pydot(graph)
    with open(path, "w") as f:
        # Remove newlines as pydot treats some of them as nodes on import
        f.write(pydot_graph.to_string().replace("\n", ""))


def build_and_save_labeled_two_cycles_graph_as_dot(
    first_cycle_num: int,
    first_cycle_label: str,
    second_cycle_num: int,
    second_cycle_label: str,
    path: str | IO,
) -> nx.MultiDiGraph:
    graph = build_labeled_two_cycles_graph(
        first_cycle_num,
        first_cycle_label,
        second_cycle_num,
        second_cycle_label,
    )
    save_graph_as_dot(graph, path)
    return graph
