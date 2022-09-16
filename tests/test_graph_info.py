import networkx as nx
import pytest

from project import utils
from load_test_data import load_test_data

GRAPH_INFOS = {
    "null": utils.get_graph_info(nx.null_graph()),
    "trivial": utils.get_graph_info(nx.trivial_graph()),
    "single_edge": utils.get_graph_info(nx.Graph([(1, 2, {"label": "a"})])),
    "skos": utils.get_graph_info(utils.load_graph_from_cfpg_data("skos")),
}


@pytest.mark.parametrize(
    "graph_info, expected_nodes_num",
    map(lambda data: (GRAPH_INFOS[data[0]], data[1]), load_test_data("test_nodes_num")),
)
def test_nodes_num(graph_info: utils.GraphInfo, expected_nodes_num: int):
    assert graph_info.nodes_num == expected_nodes_num


@pytest.mark.parametrize(
    "graph_info, expected_edges_num",
    map(lambda data: (GRAPH_INFOS[data[0]], data[1]), load_test_data("test_edges_num")),
)
def test_edges_num(graph_info: utils.GraphInfo, expected_edges_num: int):
    assert graph_info.edges_num == expected_edges_num


@pytest.mark.parametrize(
    "graph_info, expected_labels",
    map(lambda data: (GRAPH_INFOS[data[0]], data[1]), load_test_data("test_labels")),
)
def test_labels(graph_info: utils.GraphInfo, expected_labels: list[str]):
    assert list(graph_info.labels) == expected_labels
