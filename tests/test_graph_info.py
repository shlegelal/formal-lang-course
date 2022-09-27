import networkx as nx
import pytest

from project import graph_utils
from testing_utils import load_test_data

GRAPH_INFOS = {
    "null": graph_utils.get_graph_info(nx.null_graph()),
    "trivial": graph_utils.get_graph_info(nx.trivial_graph()),
    "single_edge": graph_utils.get_graph_info(nx.Graph([(1, 2, {"label": "a"})])),
    "skos": graph_utils.get_graph_info(graph_utils.load_graph_from_cfpg_data("skos")),
}


@pytest.mark.parametrize(
    "graph_info, expected_nodes_num",
    load_test_data(
        "test_nodes_num",
        lambda d: (GRAPH_INFOS[d["graph_name"]], d["expected_nodes_num"]),
    ),
)
def test_nodes_num(graph_info: graph_utils.GraphInfo, expected_nodes_num: int):
    assert graph_info.nodes_num == expected_nodes_num


@pytest.mark.parametrize(
    "graph_info, expected_edges_num",
    load_test_data(
        "test_edges_num",
        lambda d: (GRAPH_INFOS[d["graph_name"]], d["expected_edges_num"]),
    ),
)
def test_edges_num(graph_info: graph_utils.GraphInfo, expected_edges_num: int):
    assert graph_info.edges_num == expected_edges_num


@pytest.mark.parametrize(
    "graph_info, expected_labels",
    load_test_data(
        "test_labels", lambda d: (GRAPH_INFOS[d["graph_name"]], d["expected_edges_num"])
    ),
)
def test_labels(graph_info: graph_utils.GraphInfo, expected_labels: list[str]):
    assert list(graph_info.labels) == expected_labels
