import networkx as nx
from pathlib import Path

from project import utils


def test_write_dot_then_read_is_isomorphic(tmp_path: Path):
    path = (tmp_path / "test_graph.dot").as_posix()
    expected_graph = utils.build_two_cycles_graph((1, 1), ("a", "b"))

    utils.write_graph_to_dot(expected_graph, path)

    actual_graph = nx.drawing.nx_pydot.read_dot(path)
    # Have to convert string node labels back to ints
    int_mapping = dict(map(lambda n: (n[0], int(n[0])), actual_graph.nodes))
    actual_graph = nx.relabel_nodes(actual_graph, int_mapping)

    assert nx.is_isomorphic(expected_graph, actual_graph)
